import os
import subprocess
import time
import json
import select
import logging
import signal
import socket
import threading
import re
from typing import List, Dict, Set
from src.config import settings, SdrType
from src.zmq_publisher import zmq_pub
from src.gsm_arfcn_validator import get_arfcn_info, estimate_operator
from src.gsmtap_parser import parse_gsmtap_packet

logger = logging.getLogger("gsm_scanner")

class GsmScanner:
    def __init__(self):
        self.active_scan_id = None
        self.status = "IDLE"
        self.current_arfcn = 0
        self.current_step = "0/0"
        self.decoded_sis = set()
        
        self.livemon_proc = None
        self.tshark_proc = None
        self.scan_results = {}  # In-memory scan database mapped by scan_id
        
        self.database_dir = "/vol/output"
        if not os.path.exists(self.database_dir):
            self.database_dir = "/home/mobsec/Desktop/netmon/lte-sib-parser/vol/output"

    def stop_active_scan(self) -> bool:
        """
        Gracefully kills active GSM scan subprocesses
        """
        stopped = False
        if self.livemon_proc and self.livemon_proc.poll() is None:
            logger.info("grgsm_livemon_headless process sonlandiriliyor...")
            self.livemon_proc.terminate()
            try:
                self.livemon_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.livemon_proc.kill()
            stopped = True
            
        if self.tshark_proc and self.tshark_proc.poll() is None:
            logger.info("tshark process sonlandiriliyor...")
            self.tshark_proc.terminate()
            try:
                self.tshark_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.tshark_proc.kill()
            stopped = True

        if hasattr(self, 'tshark_json_proc') and self.tshark_json_proc and self.tshark_json_proc.poll() is None:
            logger.info("tshark_json process sonlandiriliyor...")
            self.tshark_json_proc.terminate()
            try:
                self.tshark_json_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.tshark_json_proc.kill()
            stopped = True

        self.livemon_proc = None
        self.tshark_proc = None
        self.tshark_json_proc = None
        self.status = "STOPPED"
        self.decoded_sis.clear()
        
        if self.active_scan_id:
            zmq_pub.publish_progress("gsm_stopped", self.current_arfcn, {"scan_id": self.active_scan_id})
            
        return stopped

    def scan_band_mod1(self, band: str, gain: int) -> List[Dict]:
        """
        Executes grgsm_scanner in a background subprocess to do full-band discovery.
        Parses active channels, power levels, Cell IDs, LACs, and BA neighbors in real-time.
        """
        self.status = "RUNNING"
        serial = settings.SDR_SERIAL
        # Auto-detect driver arguments
        args_str = f"driver=lime,serial={serial}" if settings.SDR_TYPE == SdrType.LIMESDR else f"usrp,serial={serial}"
        
        # Slower speed on low-end hardware for maximum reliability, speed 20 for GSM900, 25 for DCS1800
        speed = 20 if band == "GSM900" else 25
        
        cmd = f"grgsm_scanner --args=\"{args_str}\" -g {gain} -b {band} --speed={speed} -v"
        logger.info(f"grgsm_scanner baslatiliyor: {cmd}")
        
        total_arfcns = 174 if band == "GSM900" else 374
        zmq_pub.send_event("scan_progress", {
            "event": "gsm_band_scan_start",
            "band": band,
            "total_arfcns": total_arfcns,
            "scan_id": self.active_scan_id
        })
        
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        cells = []
        current_cell = None
        
        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
                
            line_strip = line.strip()
            if not line_strip:
                continue
                
            # ARFCN:   60, Freq:  947.0M, CID:  7349, LAC: 33006, MCC: 286, MNC:   1, Pwr: -64
            m_cell = re.search(r"ARFCN:\s*(\d+),\s*Freq:\s*([\d.]+)M,\s*CID:\s*(\d+),\s*LAC:\s*(\d+),\s*MCC:\s*(\d+),\s*MNC:\s*(\d+),\s*Pwr:\s*(-?\d+)", line_strip)
            if m_cell:
                arfcn = int(m_cell.group(1))
                freq = float(m_cell.group(2))
                cid = int(m_cell.group(3))
                lac = int(m_cell.group(4))
                mcc = int(m_cell.group(5))
                mnc = int(m_cell.group(6))
                pwr = int(m_cell.group(7))
                
                op = estimate_operator(arfcn, band)
                
                current_cell = {
                    "arfcn": arfcn,
                    "band": band,
                    "freq_mhz": freq,
                    "cell_id": cid,
                    "lac": lac,
                    "mcc": mcc,
                    "mnc": mnc,
                    "plmn": f"{mcc}{mnc:02d}",
                    "operator_name": op,
                    "rssi_dbm": pwr,
                    "config": "1 CCCH, not combined",
                    "cell_arfcns": [arfcn],
                    "sdcch": {"type": "SDCCH/8", "timeslot": 2, "tsc": 5, "maio": 0, "hsn": 32},
                    "a5_version": 1,
                    "neighbors_si2": [],
                    "neighbors_si2quater": {"earfcns": [], "uarfcns": []},
                    "success": True,
                    "si_decoded": ["SI2", "SI3"]
                }
                cells.append(current_cell)
                
                # Emit ZMQ found event
                zmq_pub.send_event("scan_progress", {
                    "event": "gsm_cell_found",
                    "arfcn": arfcn,
                    "freq_mhz": freq,
                    "cid": cid,
                    "operator": op,
                    "rssi": pwr,
                    "neighbors": 0,
                    "scan_id": self.active_scan_id
                })
                
            # Parse SDCCH config parameters
            m_sdcch = re.search(r"SDCCH/(\d+),\s*Timeslot:\s*(\d+),\s*Training Sequence:\s*(\d+)", line_strip)
            if m_sdcch and current_cell:
                current_cell["sdcch"]["type"] = f"SDCCH/{m_sdcch.group(1)}"
                current_cell["sdcch"]["timeslot"] = int(m_sdcch.group(2))
                current_cell["sdcch"]["tsc"] = int(m_sdcch.group(3))
                
                m_maio = re.search(r"MAIO:\s*(\d+)", line_strip)
                m_hsn = re.search(r"HSN:\s*(\d+)", line_strip)
                m_a5 = re.search(r"A5/1 Version:\s*(\d+)", line_strip)
                if m_maio: current_cell["sdcch"]["maio"] = int(m_maio.group(1))
                if m_hsn: current_cell["sdcch"]["hsn"] = int(m_hsn.group(1))
                if m_a5: current_cell["a5_version"] = int(m_a5.group(1))
                
            # Parse Neighbour Cells line
            m_neigh = re.search(r"Neighbour Cells:\s*([\d,\s]+)", line_strip)
            if m_neigh and current_cell:
                neigh_arfcns = [int(x) for x in m_neigh.group(1).replace(",", " ").split()]
                current_cell["neighbors_si2"] = sorted(neigh_arfcns)
                
                # Resend found event with actual neighbors count
                zmq_pub.send_event("scan_progress", {
                    "event": "gsm_cell_found",
                    "arfcn": current_cell["arfcn"],
                    "freq_mhz": current_cell["freq_mhz"],
                    "cid": current_cell["cell_id"],
                    "operator": current_cell["operator_name"],
                    "rssi": current_cell["rssi_dbm"],
                    "neighbors": len(neigh_arfcns),
                    "scan_id": self.active_scan_id
                })
                
        process.wait()
        return cells

    def scan_channel_mod2(self, arfcn: int, idx: int, total: int, gain: int, timeout_sec: int) -> Dict:
        """
        Runs grgsm_livemon_headless sequentially for a single channel, decodes UDP stream
        in real-time and runs offline tshark parsing.
        """
        self.current_arfcn = arfcn
        self.current_step = f"{idx}/{total}"
        self.decoded_sis.clear()
        self.status = "RUNNING"
        
        band, freq_mhz = get_arfcn_info(arfcn)
        freq_hz = freq_mhz * 1e6
        
        pcap_path = f"/tmp/gsm_capture_{self.active_scan_id}_{arfcn}.pcap"
        if os.path.exists(pcap_path):
            os.remove(pcap_path)
            
        tshark_cmd = f"echo '123' | su -c 'timeout {timeout_sec} tshark -i lo -f \"udp port {settings.GSM_UDP_PORT}\" -w {pcap_path}'"
        self.tshark_proc = subprocess.Popen(tshark_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Concurrent JSON-based tshark parser for SI2quater capture
        tshark_json_path = f"/tmp/gsm_si2q_{self.active_scan_id}_{arfcn}.json"
        if os.path.exists(tshark_json_path):
            try: os.remove(tshark_json_path)
            except Exception: pass
            
        tshark_json_cmd = (
            f"echo '123' | su -c 'timeout {timeout_sec} tshark -i lo "
            f"-Y \"gsm_a.dtap.msg_rr_type == 0x07\" -T json "
            f"-e gsm_a.rr.utran_freq -e gsm_a.rr.earfcn "
            f"-e gsm_a.rr.thresh_utran_high -e gsm_a.rr.thresh_eutran_high' "
            f"> {tshark_json_path} 2>/dev/null"
        )
        self.tshark_json_proc = subprocess.Popen(tshark_json_cmd, shell=True)
        
        serial = settings.SDR_SERIAL
        dev_args = f"driver=lime,serial={serial}" if settings.SDR_TYPE == SdrType.LIMESDR else f"usrp,serial={serial}"
        # Append antenna port override if defined, else fallback to settings antenna port LNAH/LNAW
        dev_args += f",rxant={settings.antenna}"
        
        livemon_cmd = f"grgsm_livemon_headless -f {freq_hz} --args=\"{dev_args}\" -g {gain}"
        logger.info(f"grgsm_livemon_headless baslatiliyor: {livemon_cmd}")
        
        zmq_pub.send_event("scan_progress", {
            "event": "gsm_tuning",
            "arfcn": arfcn,
            "freq_mhz": freq_mhz,
            "step": self.current_step,
            "scan_id": self.active_scan_id
        })
        
        self.livemon_proc = subprocess.Popen(livemon_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        time.sleep(1.5)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        try:
            sock.bind(("127.0.0.1", settings.GSM_UDP_PORT))
        except Exception as e:
            logger.error(f"Bind failed: {e}")
            self.stop_active_scan()
            return {"arfcn": arfcn, "success": False}
            
        start_time = time.time()
        has_si3 = False
        has_si2 = False
        has_si2quater = False
        
        cell_info = {
            "arfcn": arfcn,
            "band": band,
            "freq_mhz": freq_mhz,
            "success": False,
            "cell_id": 0,
            "lac": 0,
            "mcc": 0,
            "mnc": 0,
            "plmn": "N/A",
            "operator_name": "Bilinmeyen",
            "rssi_dbm": -100,
            "config": "1 CCCH, not combined",
            "cell_arfcns": [arfcn],
            "sdcch": {"type": "SDCCH/8", "timeslot": 2, "tsc": 5, "maio": 0, "hsn": 32},
            "a5_version": 1,
            "neighbors_si2": [],
            "neighbors_si2quater": {"earfcns": [], "uarfcns": []},
            "si_decoded": []
        }
        
        while time.time() - start_time < timeout_sec:
            if self.status == "STOPPED":
                break
            if has_si2 and has_si3:
                if has_si2quater or (time.time() - start_time > 6.0):
                    break
                    
            try:
                data, addr = sock.recvfrom(2048)
            except socket.timeout:
                continue
                
            parsed = parse_gsmtap_packet(data)
            if parsed:
                si_type = parsed["si_type"]
                cell_info["rssi_dbm"] = parsed["signal_dbm"]
                
                if si_type not in cell_info["si_decoded"]:
                    cell_info["si_decoded"].append(si_type)
                    
                if si_type == "SI3" and not has_si3:
                    has_si3 = True
                    cell_info["cell_id"] = parsed["cell_id"]
                    cell_info["lac"] = parsed["lac"]
                    cell_info["mcc"] = int(parsed["mcc"])
                    cell_info["mnc"] = int(parsed["mnc"])
                    cell_info["plmn"] = parsed["plmn"]
                    cell_info["operator_name"] = estimate_operator(arfcn, band)
                    cell_info["success"] = True
                    
                    zmq_pub.send_event("scan_progress", {
                        "event": "gsm_si_decoded",
                        "arfcn": arfcn,
                        "si": "SI3",
                        "cid": parsed["cell_id"],
                        "lac": parsed["lac"],
                        "plmn": parsed["plmn"],
                        "scan_id": self.active_scan_id
                    })
                    
                elif si_type == "SI2" and not has_si2:
                    has_si2 = True
                    cell_info["neighbors_si2"] = parsed["ba_list"]
                    
                    zmq_pub.send_event("scan_progress", {
                        "event": "gsm_si_decoded",
                        "arfcn": arfcn,
                        "si": "SI2",
                        "ba_list": parsed["ba_list"],
                        "scan_id": self.active_scan_id
                    })
                    
                elif si_type == "SI2quater" and not has_si2quater:
                    has_si2quater = True
                    
        sock.close()
        self.stop_active_scan()
        
        # Extract lists
        earfcns_list = []
        uarfcns_list = []
        
        # 1. Live JSON exact parsing
        tshark_json_path = f"/tmp/gsm_si2q_{self.active_scan_id}_{arfcn}.json"
        if os.path.exists(tshark_json_path) and os.path.getsize(tshark_json_path) > 10:
            try:
                subprocess.run(f"echo '123' | su -c 'chown mobsec:mobsec {tshark_json_path}'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with open(tshark_json_path, "r", encoding="utf-8") as f:
                    tshark_data = json.load(f)
                
                for pkg in tshark_data:
                    layers = pkg.get("_source", {}).get("layers", {})
                    
                    # Extract earfcns
                    earf = layers.get("gsm_a.rr.earfcn", [])
                    if isinstance(earf, list):
                        for e in earf:
                            try: earfcns_list.append(int(e))
                            except ValueError: pass
                    elif earf:
                        try: earfcns_list.append(int(earf))
                        except ValueError: pass
                        
                    # Extract uarfcns
                    uarf = layers.get("gsm_a.rr.utran_freq", [])
                    if isinstance(uarf, list):
                        for u in uarf:
                            try: uarfcns_list.append(int(u))
                            except ValueError: pass
                    elif uarf:
                        try: uarfcns_list.append(int(uarf))
                        except ValueError: pass
            except Exception as e:
                logger.warning(f"tshark JSON parsing failed: {e}")
            finally:
                try: os.remove(tshark_json_path)
                except Exception: pass
                
        # 2. PCAP offline exact parsing fallback
        if os.path.exists(pcap_path) and os.path.getsize(pcap_path) > 100:
            try:
                subprocess.run(f"echo '123' | su -c 'chown mobsec:mobsec {pcap_path}'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                tshark_out = subprocess.check_output(f"tshark -r {pcap_path} -V", shell=True, text=True, stderr=subprocess.DEVNULL)
                
                ci_m = re.search(r"Cell CI:\s*0x[0-9a-fA-F]+\s*\((\d+)\)", tshark_out)
                mcc_m = re.search(r"Mobile Country Code \(MCC\):.*\((\d+)\)", tshark_out)
                mnc_m = re.search(r"Mobile Network Code \(MNC\):.*\((\d+)\)", tshark_out)
                lac_m = re.search(r"Location Area Code \(LAC\):.*\((\d+)\)", tshark_out)
                
                if ci_m: cell_info["cell_id"] = int(ci_m.group(1))
                if mcc_m: cell_info["mcc"] = int(mcc_m.group(1))
                if mnc_m: cell_info["mnc"] = int(mnc_m.group(1))
                if lac_m: cell_info["lac"] = int(lac_m.group(1))
                if ci_m or mcc_m or lac_m:
                    cell_info["plmn"] = f"{cell_info['mcc']}{cell_info['mnc']:02d}"
                    cell_info["operator_name"] = estimate_operator(arfcn, band)
                    cell_info["success"] = True
                    if "SI3" not in cell_info["si_decoded"]:
                        cell_info["si_decoded"].append("SI3")
                    
                ba_matches = re.findall(r"List of ARFCNs\s*=\s*([\d\s]+)", tshark_out)
                if ba_matches:
                    ba_arfcns = []
                    for bm in ba_matches:
                        ba_arfcns.extend([int(x) for x in bm.split()])
                    cell_info["neighbors_si2"] = sorted(list(set(ba_arfcns)))
                    if "SI2" not in cell_info["si_decoded"]:
                        cell_info["si_decoded"].append("SI2")
                    
                pcap_earfcns = [int(x) for x in re.findall(r"EARFCN:\s*(\d+)", tshark_out)]
                pcap_uarfcns = [int(x) for x in re.findall(r"FDD UARFCN:\s*(\d+)", tshark_out)]
                
                earfcns_list.extend(pcap_earfcns)
                uarfcns_list.extend(pcap_uarfcns)
                
            except Exception as e:
                logger.warning(f"tshark PCAP parsing failed: {e}")
                
        # Merge lists and update cell info
        final_earfcns = sorted(list(set(earfcns_list)))
        final_uarfcns = sorted(list(set(uarfcns_list)))
        
        cell_info["neighbors_si2quater"]["earfcns"] = final_earfcns
        cell_info["neighbors_si2quater"]["uarfcns"] = final_uarfcns
        
        if final_earfcns or final_uarfcns:
            if "SI2quater" not in cell_info["si_decoded"]:
                cell_info["si_decoded"].append("SI2quater")
                
            # Emit decoded SI2quater inter-RAT list
            zmq_pub.send_event("scan_progress", {
                "event": "gsm_si_decoded",
                "arfcn": arfcn,
                "si": "SI2quater",
                "earfcns": final_earfcns,
                "uarfcns": final_uarfcns,
                "scan_id": self.active_scan_id
            })
            
        if os.path.exists(pcap_path):
            try:
                os.remove(pcap_path)
            except Exception:
                pass
                
        duration = time.time() - start_time
        
        if cell_info["success"]:
            zmq_pub.send_event("scan_progress", {
                "event": "gsm_complete",
                "arfcn": arfcn,
                "duration": round(duration, 1),
                "scan_id": self.active_scan_id
            })
            logger.info(f"✅ ARFCN {arfcn} dinlemesi basariyla tamamlandi.")
        else:
            zmq_pub.send_event("scan_progress", {
                "event": "gsm_error",
                "arfcn": arfcn,
                "reason": "no BCCH signal",
                "scan_id": self.active_scan_id
            })
            logger.warning(f"❌ ARFCN {arfcn} taranirken zaman asimi.")
            
        return cell_info

    def run_campaign(self, scan_id: str, arfcns: List[int], gain: int, timeout: int, full_band_scan: bool, band: str = "GSM900") -> Dict:
        """
        Runs full campaigns (Mod 1 or sequential Mod 2) and saves outcomes.
        """
        self.active_scan_id = scan_id
        self.status = "RUNNING"
        
        logger.info(f"🎬 GSM Tarama Kampanyasi Baslatildi: {scan_id} (Full Scan: {full_band_scan}, Kanallar: {arfcns})")
        
        cells = []
        if full_band_scan:
            cells = self.scan_band_mod1(band, gain)
        else:
            total = len(arfcns)
            for idx, arfcn in enumerate(arfcns, 1):
                if self.status == "STOPPED":
                    break
                cell_res = self.scan_channel_mod2(arfcn, idx, total, gain, timeout)
                cells.append(cell_res)
                
        self.status = "COMPLETED"
        
        # Save results in-memory
        self.scan_results[scan_id] = {
            "scan_id": scan_id,
            "timestamp": time.time(),
            "cells": cells
        }
        
        # Backup to persistent JSON file in vol output
        backup_file = os.path.join(self.database_dir, f"gsm_scan_{scan_id}.json")
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(self.scan_results[scan_id], f, indent=2)
            logger.info(f"📂 Tarama sonuclari JSON yedegi olusturuldu: {backup_file}")
        except Exception as e:
            logger.warning(f"Yazma hatasi: {e}")
            
        # Calculate summary metrics
        found_cells = [c for c in cells if c.get("success")]
        total_neigh = sum(len(c.get("neighbors_si2", [])) for c in found_cells)
        total_earfcn = sum(len(c.get("neighbors_si2quater", {}).get("earfcns", [])) for c in found_cells)
        total_uarfcn = sum(len(c.get("neighbors_si2quater", {}).get("uarfcns", [])) for c in found_cells)
        
        summary = {
            "cells": len(found_cells),
            "gsm_neighbors": total_neigh,
            "earfcns": total_earfcn,
            "uarfcns": total_uarfcn
        }
        
        zmq_pub.send_event("scan_progress", {
            "event": "gsm_scan_complete",
            "summary": summary,
            "scan_id": scan_id
        })
        
        return self.scan_results[scan_id]

# Global GSM scanner instance
gsm_scanner = GsmScanner()
