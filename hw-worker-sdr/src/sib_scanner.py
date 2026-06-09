import os
import subprocess
import time
import json
import select
import logging
import signal
from typing import List, Dict, Set
from src.config import settings, SdrType
from src.zmq_publisher import zmq_pub

logger = logging.getLogger("sib_scanner")

class SibScanner:
    def __init__(self):
        self.active_scan_id = None
        self.status = "IDLE"
        self.current_earfcn = 0
        self.current_step = "0/0"
        self.decoded_sibs = set()
        self.srsue_proc = None
        self.parser_proc = None
        
        # Determine paths that work on both host and inside container
        self.ue_conf = "/vol/helpers/ue.conf"
        if not os.path.exists(self.ue_conf):
            self.ue_conf = "/home/mobsec/Desktop/netmon/lte-sib-parser/vol/helpers/ue.conf"
            
        self.parse_script = "/vol/scripts/parse_save_sib.py"
        if not os.path.exists(self.parse_script):
            self.parse_script = "/home/mobsec/Desktop/netmon/lte-sib-parser/vol/scripts/parse_save_sib.py"
            
        self.ue_log = "/tmp/ue.log"
        self.database_dir = "/vol/output"
        if not os.path.exists(self.database_dir):
            self.database_dir = "/home/mobsec/Desktop/netmon/lte-sib-parser/vol/output"

    def stop_active_scan(self) -> bool:
        """
        Gracefully kills active scan subprocesses
        """
        stopped = False
        if self.parser_proc and self.parser_proc.poll() is None:
            logger.info("parse_save_sib.py process sonlandiriliyor...")
            self.parser_proc.terminate()
            try:
                self.parser_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.parser_proc.kill()
            stopped = True
            
        if self.srsue_proc and self.srsue_proc.poll() is None:
            logger.info("srsue process sonlandiriliyor...")
            # Send SIGINT first to let it release the SDR device
            try:
                self.srsue_proc.send_signal(signal.SIGINT)
                self.srsue_proc.wait(timeout=3)
            except Exception:
                self.srsue_proc.kill()
            stopped = True

        self.srsue_proc = None
        self.parser_proc = None
        self.status = "STOPPED"
        self.decoded_sibs.clear()
        
        # Publish complete event if scan stopped
        if self.active_scan_id:
            zmq_pub.publish_progress("scan_stopped", self.current_earfcn, {"scan_id": self.active_scan_id})
            
        return stopped

    def scan_earfcn(self, earfcn: int, idx: int, total: int, gain: int, timeout: int, extra_timeout: int, db_path: str) -> Dict:
        """
        Runs direct srsue and parser processes for a single EARFCN channel.
        Parses output in real-time, publishes to ZMQ, and returns a scan summary.
        """
        self.current_earfcn = earfcn
        self.current_step = f"{idx}/{total}"
        self.decoded_sibs.clear()
        self.status = "RUNNING"

        # 1. Clean old log file
        if os.path.exists(self.ue_log):
            try:
                os.remove(self.ue_log)
            except Exception as e:
                logger.warning(f"Eski ue.log silinemedi: {e}")

        # 2. Build srsue args
        dev_args_list = []
        if settings.SDR_SERIAL:
            dev_args_list.append(f"serial={settings.SDR_SERIAL}")
        # Append antenna port (high role: LNAH / low role: LNAW)
        dev_args_list.append(f"rxant={settings.antenna}")
        device_args = ",".join(dev_args_list)

        device_name = "soapy" if settings.SDR_TYPE == SdrType.LIMESDR else "uhd"

        srsue_cmd = [
            "srsue", self.ue_conf,
            "--log.filename", self.ue_log,
            "--expert.lte_sample_rates=true",
            "--rf.device_name", device_name,
            "--rf.device_args", device_args,
            "--rf.rx_gain", str(gain),
            "--rat.eutra.dl_earfcn", str(earfcn)
        ]

        logger.info(f"srsue baslatiliyor: {' '.join(srsue_cmd)}")
        zmq_pub.publish_progress("tuning", earfcn, {"step": self.current_step, "scan_id": self.active_scan_id})

        # Start srsue in background redirecting stdout to DEVNULL (srsue logs to ue.log)
        self.srsue_proc = subprocess.Popen(
            srsue_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Give srsue 1.5 seconds to initialize and create the log file
        time.sleep(1.5)

        # 3. Build parser script args
        parser_cmd = [
            "python3", self.parse_script,
            "-f", self.ue_log,
            "-t", str(timeout),
            "-T", str(extra_timeout),
            "-e", str(earfcn),
            "-d", db_path
        ]

        logger.info(f"parse_save_sib.py baslatiliyor: {' '.join(parser_cmd)}")
        self.parser_proc = subprocess.Popen(
            parser_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        start_time = time.time()
        success = False
        rsrp = None

        # 4. Real-time stdout parsing of the python parse_save_sib helper
        while self.parser_proc.poll() is None:
            r, _, _ = select.select([self.parser_proc.stdout], [], [], 0.5)
            if self.parser_proc.stdout in r:
                line = self.parser_proc.stdout.readline()
                if not line:
                    continue
                
                line_strip = line.strip()
                if line_strip.startswith("{") and line_strip.endswith("}"):
                    try:
                        data = json.loads(line_strip)
                        if "rsrp" in data:
                            rsrp = data["rsrp"]
                            zmq_pub.publish_progress("rsrp_measured", earfcn, {"rsrp": rsrp})
                        elif "type" in data:
                            sib_type = data["type"].upper()
                            self.decoded_sibs.add(sib_type)
                            success = True
                            
                            extra = {}
                            if sib_type == "SIB5" and "interFreqCarrierFreqList" in data.get("info", {}):
                                n_found = len(data["info"]["interFreqCarrierFreqList"])
                                extra["neighbors_found"] = n_found
                            else:
                                extra["data"] = data.get("info")
                                
                            zmq_pub.publish_progress("decoded", earfcn, {"sib": sib_type, **extra})
                    except Exception as parse_ex:
                        logger.error(f"Event JSON parse hatasi: {parse_ex}")

        # Wait for parser to exit completely
        stdout, stderr = self.parser_proc.communicate()
        duration = time.time() - start_time

        # 5. Stop srsue gracefully
        if self.srsue_proc and self.srsue_proc.poll() is None:
            try:
                self.srsue_proc.send_signal(signal.SIGINT)
                self.srsue_proc.wait(timeout=2)
            except Exception:
                self.srsue_proc.kill()

        self.srsue_proc = None
        self.parser_proc = None

        # Check final status
        if success:
            zmq_pub.publish_progress("complete", earfcn, {"duration": round(duration, 1)})
            logger.info(f"✅ EARFCN {earfcn} taramasi basariyla tamamlandi. Süre: {duration:.1f}sn")
            return {"earfcn": earfcn, "success": True, "duration": duration, "rsrp": rsrp}
        else:
            zmq_pub.publish_progress("error", earfcn, {"reason": "timeout"})
            logger.warning(f"❌ EARFCN {earfcn} taramasi zaman asimina ugradi.")
            return {"earfcn": earfcn, "success": False, "duration": duration, "rsrp": None}

    def run_campaign(self, scan_id: str, earfcns: List[int], gain: int, timeout: int, extra_timeout: int) -> Dict:
        """
        Executes a sequence of single earfcn scans as a single campaign
        """
        self.active_scan_id = scan_id
        db_file = os.path.join(self.database_dir, f"scan_{scan_id}.sqlite")
        
        logger.info(f"🎬 Tarama Kampanyasi Baslatildi: {scan_id} (Kanal sayısı: {len(earfcns)})")
        results = []
        total = len(earfcns)
        
        for idx, earfcn in enumerate(earfcns, start=1):
            if self.status == "STOPPED":
                break
            res = self.scan_earfcn(earfcn, idx, total, gain, timeout, extra_timeout, db_file)
            results.append(res)
            
        self.status = "COMPLETED"
        summary = {
            "scan_id": scan_id,
            "total_channels": total,
            "successful_channels": sum(1 for r in results if r["success"]),
            "db_path": db_file
        }
        zmq_pub.publish_progress("scan_complete", self.current_earfcn, {"summary": summary})
        return summary

# Global scanner instance
sib_scanner = SibScanner()
