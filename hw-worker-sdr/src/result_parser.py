import sqlite3
import json
import logging
from typing import List, Dict, Optional
from src.earfcn_validator import get_earfcn_info

logger = logging.getLogger("result_parser")

def resolve_operator(plmn: str) -> str:
    """
    Translates MCC/MNC PLMN string into operator name
    """
    clean_plmn = plmn.replace("-", "").strip()
    if clean_plmn in ("28601", "2861"):
        return "Turkcell"
    elif clean_plmn in ("28602", "2862"):
        return "Vodafone"
    elif clean_plmn in ("28603", "2863"):
        return "Türk Telekom"
    return "Bilinmeyen"

def parse_cell_row(row: tuple, columns: List[str]) -> Dict:
    """
    Parses a single row from the cells table into a structured dictionary
    """
    row_dict = dict(zip(columns, row))
    earfcn = int(row_dict["earfcn"])
    
    # Calculate band and frequency based on TS 36.101
    band, freq = get_earfcn_info(earfcn)
    
    rsrp_val = row_dict.get("rsrp")
    rsrp = float(rsrp_val) if rsrp_val is not None else -140.0

    cell_data = {
        "earfcn": earfcn,
        "band": band or 0,
        "freq_mhz": freq or 0.0,
        "pci": 0,
        "cell_id": 0,
        "plmn": "N/A",
        "operator_name": "Bilinmeyen",
        "tac": 0,
        "rsrp": rsrp,
        "bandwidth": "20MHz",  # default
        "sibs_decoded": []
    }

    # Track decoded SIBs
    for sib_col in ["mib", "sib1", "sib2", "sib3", "sib4", "sib5", "sib6", "sib7", "sib8", "sib9", "sib10", "sib11", "sib12", "sib13"]:
        val = row_dict.get(sib_col)
        if val:
            cell_data["sibs_decoded"].append(sib_col.upper())
            # Parse json info
            try:
                parsed_json = json.loads(val)
                row_dict[sib_col] = parsed_json
            except Exception:
                row_dict[sib_col] = None
        else:
            row_dict[sib_col] = None

    # MIB check
    if row_dict["mib"]:
        pass

    # SIB1 check
    if row_dict["sib1"]:
        sib1 = row_dict["sib1"]
        cari = sib1.get("cellAccessRelatedInfo", {})
        
        # cellIdentity -> 28 bits string, e.g. "0000000000000000000000010100"
        if "cellIdentity" in cari:
            try:
                cell_id = int(cari["cellIdentity"], 2)
                cell_data["cell_id"] = cell_id
                cell_data["pci"] = cell_id % 504
            except Exception as ex:
                logger.error(f"cellIdentity parse hatasi: {ex}")

        # trackingAreaCode -> 16 bits string
        if "trackingAreaCode" in cari:
            try:
                cell_data["tac"] = int(cari["trackingAreaCode"], 2)
            except Exception as ex:
                logger.error(f"trackingAreaCode parse hatasi: {ex}")

        # plmn-IdentityList
        if "plmn-IdentityList" in cari and len(cari["plmn-IdentityList"]) > 0:
            plmn_entry = cari["plmn-IdentityList"][0].get("plmn-Identity", {})
            if "mcc" in plmn_entry and "mnc" in plmn_entry:
                mcc = "".join(str(x) for x in plmn_entry["mcc"])
                mnc = "".join(str(x) for x in plmn_entry["mnc"])
                cell_data["plmn"] = f"{mcc}-{mnc}"
                cell_data["operator_name"] = resolve_operator(f"{mcc}{mnc}")

    # Store parsed SIB json blocks in the returned dict as raw properties
    cell_data["raw_sibs"] = row_dict
    
    return cell_data

def parse_database(db_path: str) -> List[Dict]:
    """
    Queries SQLite database and parses all scanned cell records.
    """
    logger.info(f"SQLite veritabani analiz ediliyor: {db_path}")
    cells = []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute("PRAGMA table_info(cells)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if not columns:
            logger.warning("Veritabaninda cells tablosu bos veya bulunamadi.")
            conn.close()
            return []

        # Build clean select query for present columns
        select_cols = ", ".join(columns)
        cursor.execute(f"SELECT {select_cols} FROM cells")
        
        for row in cursor.fetchall():
            try:
                parsed_cell = parse_cell_row(row, columns)
                cells.append(parsed_cell)
            except Exception as row_ex:
                logger.error(f"Satir parse edilirken hata oluştu: {row_ex}")
                
        conn.close()
    except Exception as e:
        logger.error(f"SQLite veritabani okunamadi: {e}")
        
    return cells
