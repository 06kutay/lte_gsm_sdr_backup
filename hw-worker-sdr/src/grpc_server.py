import os
import json
import time
import uuid
import logging
import threading
from typing import Dict, List
import grpc
from concurrent import futures

import proto.sdr_worker_pb2 as pb2
import proto.sdr_worker_pb2_grpc as pb2_grpc

from src.config import settings
from src.device_manager import device_manager
from src.earfcn_validator import validate_earfcn
from src.sib_scanner import sib_scanner
from src.result_parser import parse_database
from src.neighbor_analyzer import (
    extract_neighbors_from_cell,
    analyze_neighbor_map,
    get_unscanned_earfcns
)
from src.gsm_arfcn_validator import validate_arfcn as validate_gsm_arfcn, get_arfcn_info as get_gsm_arfcn_info
from src.gsm_scanner import gsm_scanner
from src.gsm_neighbor_analyzer import analyze_gsm_neighbors, analyze_inter_rat_neighbors

logger = logging.getLogger("grpc_server")

class SDRWorkerServiceServicer(pb2_grpc.SDRWorkerServiceServicer):
    def GetHealth(self, request, context):
        status = "SERVING" if device_manager.is_serving else "NOT_SERVING"
        uptime = time.time() - device_manager.uptime_start
        return pb2.HealthResponse(
            status=status,
            sdr_type=settings.SDR_TYPE.value,
            serial=settings.SDR_SERIAL,
            role=settings.SDR_ROLE.value,
            antenna=settings.antenna,
            uptime=uptime
        )

    def ValidateEarfcns(self, request, context):
        validations = []
        all_valid = True
        for earfcn in request.earfcns:
            is_valid, err_msg, band, freq = validate_earfcn(earfcn)
            if not is_valid:
                all_valid = False
            validations.append(pb2.EarfcnValidation(
                earfcn=earfcn,
                band=band or 0,
                freq_mhz=freq or 0.0,
                is_valid=is_valid,
                error_message=err_msg,
                antenna_port=settings.antenna if is_valid else ""
            ))
        return pb2.ValidationResult(validations=validations, all_valid=all_valid)

    def StartScan(self, request, context):
        if not device_manager.is_serving:
            return pb2.ScanResponse(
                scan_id="",
                started=False,
                message="SDR Donanimi bagli degil (NOT_SERVING)!"
            )

        if sib_scanner.status == "RUNNING" or gsm_scanner.status == "RUNNING":
            active_id = sib_scanner.active_scan_id or gsm_scanner.active_scan_id or ""
            return pb2.ScanResponse(
                scan_id=active_id,
                started=False,
                message="Aktif bir tarama zaten devam ediyor!"
            )

        # Generate unique scan ID
        scan_id = "lte_" + str(uuid.uuid4())[:8] + "_" + datetime_stamp()
        
        # Read parameters falling back to config if not provided
        gain = request.gain if request.gain > 0 else settings.DEFAULT_GAIN
        timeout = request.timeout if request.timeout > 0 else settings.DEFAULT_TIMEOUT
        extra_timeout = request.extra_timeout if request.extra_timeout > 0 else settings.DEFAULT_EXTRA_TIMEOUT

        # Start campaign in a separate thread so gRPC doesn't block
        def run_campaign_thread():
            try:
                sib_scanner.run_campaign(
                    scan_id=scan_id,
                    earfcns=list(request.earfcns),
                    gain=gain,
                    timeout=timeout,
                    extra_timeout=extra_timeout
                )
            except Exception as e:
                logger.error(f"Tarama thread hatasi: {e}")
                sib_scanner.status = "FAILED"

        threading.Thread(target=run_campaign_thread, daemon=True).start()

        return pb2.ScanResponse(
            scan_id=scan_id,
            started=True,
            message="Tarama basariyla baslatildi."
        )

    def GetScanStatus(self, request, context):
        if request.scan_id.startswith("gsm_"):
            if gsm_scanner.active_scan_id != request.scan_id:
                return pb2.ScanStatusResponse(
                    scan_id=request.scan_id,
                    status="NOT_FOUND",
                    current_earfcn=0,
                    current_step="0/0",
                    decoded_sibs=[]
                )
            return pb2.ScanStatusResponse(
                scan_id=request.scan_id,
                status=gsm_scanner.status,
                current_earfcn=gsm_scanner.current_arfcn,
                current_step=gsm_scanner.current_step,
                decoded_sibs=list(gsm_scanner.decoded_sis)
            )

        if sib_scanner.active_scan_id != request.scan_id:
            return pb2.ScanStatusResponse(
                scan_id=request.scan_id,
                status="NOT_FOUND",
                current_earfcn=0,
                current_step="0/0",
                decoded_sibs=[]
            )
            
        return pb2.ScanStatusResponse(
            scan_id=request.scan_id,
            status=sib_scanner.status,
            current_earfcn=sib_scanner.current_earfcn,
            current_step=sib_scanner.current_step,
            decoded_sibs=list(sib_scanner.decoded_sibs)
        )

    def GetScanResults(self, request, context):
        db_file = f"{sib_scanner.database_dir}/scan_{request.scan_id}.sqlite"
        cells = parse_database(db_file)
        
        grpc_cells = []
        for c in cells:
            cell_msg = pb2.CellInfo(
                earfcn=c["earfcn"],
                band=c["band"],
                freq_mhz=c["freq_mhz"],
                pci=c["pci"],
                cell_id=c["cell_id"],
                plmn=c["plmn"],
                operator_name=c["operator_name"],
                tac=c["tac"],
                rsrp=c["rsrp"],
                bandwidth=c["bandwidth"]
            )
            cell_msg.sibs_decoded.extend(c["sibs_decoded"])
            grpc_cells.append(cell_msg)
            
        return pb2.ScanResultsResponse(
            scan_id=request.scan_id,
            cells=grpc_cells
        )

    def GetCellInfo(self, request, context):
        db_file = f"{sib_scanner.database_dir}/scan_{request.scan_id}.sqlite"
        cells = parse_database(db_file)
        
        target_cell = None
        for c in cells:
            if c["earfcn"] == request.earfcn:
                target_cell = c
                break
                
        if not target_cell:
            return pb2.CellInfoResponse(found=False)

        cell_msg = pb2.CellInfo(
            earfcn=target_cell["earfcn"],
            band=target_cell["band"],
            freq_mhz=target_cell["freq_mhz"],
            pci=target_cell["pci"],
            cell_id=target_cell["cell_id"],
            plmn=target_cell["plmn"],
            operator_name=target_cell["operator_name"],
            tac=target_cell["tac"],
            rsrp=target_cell["rsrp"],
            bandwidth=target_cell["bandwidth"]
        )
        cell_msg.sibs_decoded.extend(target_cell["sibs_decoded"])
        
        return pb2.CellInfoResponse(found=True, cell=cell_msg)

    def GetNeighbors(self, request, context):
        db_file = f"{sib_scanner.database_dir}/scan_{request.scan_id}.sqlite"
        cells = parse_database(db_file)
        
        target_cell = None
        for c in cells:
            if c["earfcn"] == request.earfcn:
                target_cell = c
                break
                
        if not target_cell:
            return pb2.NeighborResponse(earfcn=request.earfcn, neighbors=[])
            
        neighbors = extract_neighbors_from_cell(target_cell)
        grpc_neighs = []
        for n in neighbors:
            grpc_neighs.append(pb2.NeighborInfo(
                neighbor_earfcn=n["neighbor_earfcn"],
                neighbor_band=n["neighbor_band"],
                neighbor_freq=n["neighbor_freq"],
                priority=n["priority"],
                thresh_x_high=n["thresh_x_high"],
                thresh_x_low=n["thresh_x_low"],
                bandwidth=n["bandwidth"],
                neighbor_type=n["neighbor_type"],
                pci_or_psc=n["pci_or_psc"]
            ))
            
        return pb2.NeighborResponse(earfcn=request.earfcn, neighbors=grpc_neighs)

    def GetNeighborMap(self, request, context):
        db_file = f"{sib_scanner.database_dir}/scan_{request.scan_id}.sqlite"
        cells = parse_database(db_file)
        relations = analyze_neighbor_map(cells)
        
        grpc_rels = []
        for r in relations:
            grpc_rels.append(pb2.NeighborRelation(
                cell_a=r["cell_a"],
                cell_b=r["cell_b"],
                direction=r["direction"],
                relation_type=r["relation_type"]
            ))
            
        return pb2.NeighborMapResponse(
            scan_id=request.scan_id,
            relations=grpc_rels
        )

    def GetUnscannedEarfcns(self, request, context):
        db_file = f"{sib_scanner.database_dir}/scan_{request.scan_id}.sqlite"
        cells = parse_database(db_file)
        unscanned = get_unscanned_earfcns(cells)
        return pb2.EarfcnList(earfcns=unscanned)

    def StopScan(self, request, context):
        if request.scan_id.startswith("gsm_"):
            if gsm_scanner.active_scan_id != request.scan_id:
                return pb2.StopResponse(
                    scan_id=request.scan_id,
                    stopped=False,
                    message="Belirtilen scan ID aktif taramayla eşleşmiyor!"
                )
            stopped = gsm_scanner.stop_active_scan()
            return pb2.StopResponse(
                scan_id=request.scan_id,
                stopped=stopped,
                message="Tarama basariyla durduruldu." if stopped else "Tarama zaten sonlandirilmisti."
            )

        if sib_scanner.active_scan_id != request.scan_id:
            return pb2.StopResponse(
                scan_id=request.scan_id,
                stopped=False,
                message="Belirtilen scan ID aktif taramayla eşleşmiyor!"
            )
            
        stopped = sib_scanner.stop_active_scan()
        return pb2.StopResponse(
            scan_id=request.scan_id,
            stopped=stopped,
            message="Tarama basariyla durduruldu." if stopped else "Tarama zaten sonlandirilmisti."
        )

    def StartGsmScan(self, request, context):
        if not device_manager.is_serving:
            return pb2.ScanResponse(
                scan_id="",
                started=False,
                message="SDR Donanimi bagli degil (NOT_SERVING)!"
            )

        if sib_scanner.status == "RUNNING" or gsm_scanner.status == "RUNNING":
            active_id = sib_scanner.active_scan_id or gsm_scanner.active_scan_id or ""
            return pb2.ScanResponse(
                scan_id=active_id,
                started=False,
                message="Aktif bir tarama zaten devam ediyor!"
            )

        scan_id = "gsm_" + str(uuid.uuid4())[:8] + "_" + datetime_stamp()
        gain = request.gain if request.gain > 0 else settings.DEFAULT_GAIN
        timeout = request.timeout if request.timeout > 0 else settings.GSM_TIMEOUT_PER_ARFCN

        def run_gsm_campaign_thread():
            try:
                gsm_scanner.run_campaign(
                    scan_id=scan_id,
                    arfcns=list(request.arfcns),
                    gain=gain,
                    timeout=timeout,
                    full_band_scan=False
                )
            except Exception as e:
                logger.error(f"GSM Tarama thread hatasi: {e}")
                gsm_scanner.status = "FAILED"

        threading.Thread(target=run_gsm_campaign_thread, daemon=True).start()

        return pb2.ScanResponse(
            scan_id=scan_id,
            started=True,
            message="GSM taramasi basariyla baslatildi."
        )

    def StartGsmBandScan(self, request, context):
        if not device_manager.is_serving:
            return pb2.ScanResponse(
                scan_id="",
                started=False,
                message="SDR Donanimi bagli degil (NOT_SERVING)!"
            )

        if sib_scanner.status == "RUNNING" or gsm_scanner.status == "RUNNING":
            active_id = sib_scanner.active_scan_id or gsm_scanner.active_scan_id or ""
            return pb2.ScanResponse(
                scan_id=active_id,
                started=False,
                message="Aktif bir tarama zaten devam ediyor!"
            )

        scan_id = "gsm_band_" + str(uuid.uuid4())[:8] + "_" + datetime_stamp()
        gain = request.gain if request.gain > 0 else settings.DEFAULT_GAIN
        band = request.band if request.band in ("GSM900", "DCS1800") else settings.GSM_DEFAULT_BAND

        def run_gsm_band_campaign_thread():
            try:
                gsm_scanner.run_campaign(
                    scan_id=scan_id,
                    arfcns=[],
                    gain=gain,
                    timeout=0,
                    full_band_scan=True,
                    band=band
                )
            except Exception as e:
                logger.error(f"GSM Band Tarama thread hatasi: {e}")
                gsm_scanner.status = "FAILED"

        threading.Thread(target=run_gsm_band_campaign_thread, daemon=True).start()

        return pb2.ScanResponse(
            scan_id=scan_id,
            started=True,
            message="GSM full-band taramasi basariyla baslatildi."
        )

    def GetGsmScanResults(self, request, context):
        scan_id = request.scan_id
        campaign = gsm_scanner.scan_results.get(scan_id)
        if not campaign:
            # Fallback: try loading from JSON file
            backup_file = f"{gsm_scanner.database_dir}/gsm_scan_{scan_id}.json"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r", encoding="utf-8") as f:
                        campaign = json.load(f)
                except Exception:
                    pass
                    
        if not campaign:
            return pb2.GsmScanResultsResponse(scan_id=scan_id, cells=[])
            
        cells_list = []
        for c in campaign.get("cells", []):
            cell_msg = pb2.GsmCellInfo(
                arfcn=c["arfcn"],
                band=c["band"],
                freq_mhz=c["freq_mhz"],
                cell_id=c["cell_id"],
                lac=c["lac"],
                mcc=c["mcc"],
                mnc=c["mnc"],
                plmn=c["plmn"],
                operator_name=c["operator_name"],
                rssi_dbm=c["rssi_dbm"]
            )
            cell_msg.si_decoded.extend(c.get("si_decoded", []))
            cell_msg.neighbors_si2.extend(c.get("neighbors_si2", []))
            cells_list.append(cell_msg)
            
        return pb2.GsmScanResultsResponse(scan_id=scan_id, cells=cells_list)

    def GetGsmNeighbors(self, request, context):
        scan_id = request.scan_id
        campaign = gsm_scanner.scan_results.get(scan_id)
        if not campaign:
            backup_file = f"{gsm_scanner.database_dir}/gsm_scan_{scan_id}.json"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r", encoding="utf-8") as f:
                        campaign = json.load(f)
                except Exception:
                    pass
                    
        if not campaign:
            return pb2.GsmNeighborResponse(arfcn=request.arfcn, neighbors=[])
            
        target_cell = None
        for c in campaign.get("cells", []):
            if c["arfcn"] == request.arfcn:
                target_cell = c
                break
                
        if not target_cell:
            return pb2.GsmNeighborResponse(arfcn=request.arfcn, neighbors=[])
            
        neighbors = analyze_gsm_neighbors(target_cell)
        grpc_neighs = []
        for n in neighbors:
            grpc_neighs.append(pb2.GsmNeighborInfo(
                arfcn=n["neighbor_arfcn"],
                band=n["neighbor_band"],
                freq_mhz=n["neighbor_freq"],
                neighbor_type=n["neighbor_type"],
                operator_estimate=n["operator_estimate"]
            ))
            
        return pb2.GsmNeighborResponse(arfcn=request.arfcn, neighbors=grpc_neighs)

    def GetGsmInterRatNeighbors(self, request, context):
        scan_id = request.scan_id
        campaign = gsm_scanner.scan_results.get(scan_id)
        if not campaign:
            backup_file = f"{gsm_scanner.database_dir}/gsm_scan_{scan_id}.json"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r", encoding="utf-8") as f:
                        campaign = json.load(f)
                except Exception:
                    pass
                    
        if not campaign:
            return pb2.GsmInterRatResponse(scan_id=scan_id, inter_rat_neighbors=[])
            
        inter_rats_grpc = []
        for cell in campaign.get("cells", []):
            ir_list = analyze_inter_rat_neighbors(cell)
            for ir in ir_list:
                inter_rats_grpc.append(pb2.GsmInterRatNeighbor(
                    rat_type=ir["rat_type"],
                    channel=ir["channel"],
                    band=ir["band"],
                    freq_mhz=ir["freq_mhz"],
                    already_scanned=ir["already_scanned"],
                    cross_link=ir["cross_link"]
                ))
                
        return pb2.GsmInterRatResponse(scan_id=scan_id, inter_rat_neighbors=inter_rats_grpc)

    def ValidateArfcns(self, request, context):
        validations = []
        all_valid = True
        for arfcn in request.arfcns:
            is_valid, err_msg, band, freq = validate_gsm_arfcn(arfcn)
            if not is_valid:
                all_valid = False
            validations.append(pb2.ArfcnValidation(
                arfcn=arfcn,
                band=band or "Bilinmeyen",
                freq_mhz=freq or 0.0,
                is_valid=is_valid,
                error_message=err_msg,
                antenna_port=settings.antenna if is_valid else ""
            ))
        return pb2.ArfcnValidationResult(validations=validations, all_valid=all_valid)

def datetime_stamp() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_SDRWorkerServiceServicer_to_server(SDRWorkerServiceServicer(), server)
    
    # Enable gRPC Reflection for grpcurl tests
    from grpc_reflection.v1alpha import reflection
    SERVICE_NAMES = (
        pb2.DESCRIPTOR.services_by_name['SDRWorkerService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    port_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(port_addr)
    server.start()
    logger.info(f"gRPC Server basariyla baslatildi ve {port_addr} portunu dinliyor (Reflection Aktif).")
    return server
