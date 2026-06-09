import zmq
import json
import logging
import threading
from datetime import datetime
from src.config import settings

logger = logging.getLogger("zmq_publisher")

class ZmqPublisher:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.lock = threading.Lock()
        self.serial = settings.SDR_SERIAL or "unknown"
        self.port = settings.ZMQ_PUB_PORT

    def start(self):
        try:
            bind_addr = f"tcp://*:{self.port}"
            self.socket.bind(bind_addr)
            logger.info(f"ZMQ Publisher basariyla baslatildi ve {bind_addr} adresine baglandi.")
        except Exception as e:
            logger.error(f"ZMQ Publisher baslatilamadi: {e}")

    def send_event(self, event_type: str, data: dict):
        """
        Publishes a JSON payload over ZMQ under the topic: sdr_{serial}_{event_type}
        """
        topic = f"sdr_{self.serial}_{event_type}"
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **data
        }
        message = f"{topic} {json.dumps(payload)}"
        
        with self.lock:
            try:
                self.socket.send_string(message)
                logger.debug(f"ZMQ Event gonderildi - Topic: {topic}, Data: {payload}")
            except Exception as e:
                logger.error(f"ZMQ Event gonderilemedi: {e}")

    def publish_progress(self, event_name: str, earfcn: int, extra_data: dict = None):
        """
        Helper to publish scan progress events
        """
        data = {
            "event": event_name,
            "earfcn": earfcn,
            **(extra_data or {})
        }
        self.send_event("scan_progress", data)

    def publish_health(self, status: str, uptime: float, reason: str = None):
        """
        Helper to publish health status events
        """
        data = {
            "status": status,
            "sdr_type": settings.SDR_TYPE,
            "serial": self.serial,
            "uptime": uptime
        }
        if reason:
            data["reason"] = reason
        self.send_event("health", data)

    def close(self):
        try:
            self.socket.close()
            self.context.term()
            logger.info("ZMQ Publisher basariyla kapatildi.")
        except Exception as e:
            logger.error(f"ZMQ Publisher kapatilirken hata: {e}")

# Global publisher instance
zmq_pub = ZmqPublisher()
