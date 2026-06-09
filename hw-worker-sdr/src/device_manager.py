import subprocess
import time
import threading
import logging
import os
from src.config import settings, SdrType
from src.zmq_publisher import zmq_pub

logger = logging.getLogger("device_manager")

class DeviceManager:
    def __init__(self):
        self.is_serving = False
        self.serial = settings.SDR_SERIAL
        self.sdr_type = settings.SDR_TYPE
        self.uptime_start = time.time()
        self.probe_thread = None
        self.running = False
        self.callback = None
        self.mock_mode = os.environ.get("MOCK_SDR", "false").lower() in ("true", "1", "yes")

    def probe_device(self) -> bool:
        """
        Executes hardware probe commands to verify device availability.
        Returns True if device is available, False otherwise.
        """
        if self.mock_mode:
            logger.debug("Mock SDR mode aktif, donanim probe basarili sayildi.")
            return True

        serial_args = f' --args="serial={self.serial}"' if self.serial else ""
        try:
            if self.sdr_type == SdrType.LIMESDR:
                cmd = f"LimeUtil --find{serial_args}"
            else:  # USRP
                cmd = f"uhd_find_devices{serial_args}"

            logger.debug(f"Donanim sorgulaniyor: {cmd}")
            res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            
            if res.returncode == 0:
                stdout_lower = res.stdout.lower()
                # Check for empty output or failure messages
                if not res.stdout.strip() or "no devices found" in stdout_lower or "failed" in stdout_lower:
                    logger.debug("Cihaz bulunamadi (No devices found).")
                    return False
                logger.debug(f"Cihaz basariyla algilandi: {res.stdout.strip()}")
                return True
            else:
                logger.debug(f"Probe komutu basarisiz cikis verdi: {res.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.warning("SDR Probe komutu zaman asimina ugradi.")
            return False
        except Exception as e:
            logger.error(f"SDR Probe sirasida beklenmedik hata: {e}")
            return False

    def _probe_loop(self):
        logger.info("SDR Donanim Polling Dongusu Baslatildi.")
        while self.running:
            try:
                device_present = self.probe_device()
                uptime = time.time() - self.uptime_start

                if device_present:
                    if not self.is_serving:
                        self.is_serving = True
                        logger.info(f"🟢 SDR DONANIM BAGLANDI: {self.sdr_type} (Serial: {self.serial})")
                        zmq_pub.publish_health(status="ready", uptime=uptime)
                        # Trigger microservice registration to the backend
                        if self.callback:
                            try:
                                self.callback()
                            except Exception as ex:
                                logger.error(f"Mikroservis backend kayit cagrisi basarisiz: {ex}")
                    else:
                        # Periodically publish healthy status
                        zmq_pub.publish_health(status="ready", uptime=uptime)
                else:
                    if self.is_serving:
                        self.is_serving = False
                        logger.error("🔴 SDR DONANIM BAGLANTISI KOPTI!")
                    
                    zmq_pub.publish_health(
                        status="device_offline",
                        uptime=uptime,
                        reason="USB disconnected"
                    )

            except Exception as e:
                logger.error(f"Polling dongusunde beklenmedik hata: {e}")

            time.sleep(10)

    def start(self, on_serving_callback=None):
        self.running = True
        self.callback = on_serving_callback
        self.probe_thread = threading.Thread(target=self._probe_loop, daemon=True)
        self.probe_thread.start()

    def stop(self):
        self.running = False
        if self.probe_thread:
            self.probe_thread.join(timeout=2)
        logger.info("SDR Donanim Polling Dongusu Durduruldu.")

# Global device manager instance
device_manager = DeviceManager()
