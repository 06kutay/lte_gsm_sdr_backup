import os
from typing import List, Dict, Set, Tuple, Optional
from src.gsm_arfcn_validator import get_arfcn_info, estimate_operator

def check_lte_scanned(earfcn: int, wiki_dir: str = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki") -> Tuple[bool, str]:
    """
    Checks if an EARFCN has been scanned (exists as a Cell_EARFCN_PCI page in the Obsidian wiki).
    Returns (already_scanned, cross_link_path)
    """
    cells_dir = os.path.join(wiki_dir, "cells")
    if os.path.exists(cells_dir):
        for fn in os.listdir(cells_dir):
            if fn.startswith(f"Cell_EARFCN{earfcn}_") and fn.endswith(".md"):
                cell_name = fn[:-3]
                return True, f"cells/{cell_name}"
    return False, ""

def analyze_gsm_neighbors(cell: Dict) -> List[Dict]:
    """
    Resolves BA list neighbor cells from parsed SI2/SI2bis/SI2ter messages.
    """
    neighbors = []
    ba_list = cell.get("neighbors_si2", [])
    
    for arfcn in ba_list:
        band, freq = get_arfcn_info(arfcn)
        op = estimate_operator(arfcn, band or "Bilinmeyen")
        neighbors.append({
            "neighbor_arfcn": arfcn,
            "neighbor_band": band or "Bilinmeyen",
            "neighbor_freq": freq or 0.0,
            "neighbor_type": "2G GSM",
            "operator_estimate": op
        })
    return neighbors

def analyze_inter_rat_neighbors(cell: Dict, wiki_dir: str = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki") -> List[Dict]:
    """
    Extracts 3G/4G inter-RAT cells from SI2quater payloads.
    """
    inter_rat = []
    si2q = cell.get("neighbors_si2quater", {"earfcns": [], "uarfcns": []})
    
    # 4G LTE EARFCNs
    for earfcn in si2q.get("earfcns", []):
        # DL Frequency calculation for standard bands (Band 20, Band 3, Band 1, Band 7, Band 28)
        band, freq = get_earfcn_info_lte(earfcn)
        scanned, cross_link = check_lte_scanned(earfcn, wiki_dir)
        inter_rat.append({
            "rat_type": "4G LTE",
            "channel": earfcn,
            "band": f"Band {band}" if band else "Bilinmeyen",
            "freq_mhz": freq or 0.0,
            "already_scanned": scanned,
            "cross_link": cross_link
        })
        
    # 3G UMTS UARFCNs
    for uarfcn in si2q.get("uarfcns", []):
        band, freq = get_uarfcn_info_umts(uarfcn)
        inter_rat.append({
            "rat_type": "3G UMTS",
            "channel": uarfcn,
            "band": f"Band {band}" if band else "Bilinmeyen",
            "freq_mhz": freq or 0.0,
            "already_scanned": False,
            "cross_link": ""
        })
        
    return inter_rat

def get_earfcn_info_lte(earfcn: int) -> Tuple[Optional[int], Optional[float]]:
    # Band 1: 0 - 599
    if 0 <= earfcn <= 599:
        return 1, 2110.0 + 0.1 * (earfcn - 0)
    # Band 3: 1200 - 1949
    elif 1200 <= earfcn <= 1949:
        return 3, 1805.0 + 0.1 * (earfcn - 1200)
    # Band 7: 2750 - 3449
    elif 2750 <= earfcn <= 3449:
        return 7, 2620.0 + 0.1 * (earfcn - 2750)
    # Band 20: 6150 - 6449
    elif 6150 <= earfcn <= 6449:
        return 20, 791.0 + 0.1 * (earfcn - 6150)
    # Band 28: 9210 - 9659
    elif 9210 <= earfcn <= 9659:
        return 28, 758.0 + 0.1 * (earfcn - 9210)
    return None, None

def get_uarfcn_info_umts(uarfcn: int) -> Tuple[Optional[int], Optional[float]]:
    # Band 1: 10562-10838
    if 10562 <= uarfcn <= 10838:
        return 1, 2110.0 + 0.2 * (uarfcn - 10562)
    # Band 8: 2937-3088
    elif 2937 <= uarfcn <= 3088:
        return 8, 925.0 + 0.2 * (uarfcn - 2937)
    # Turkcell OTA allocations
    elif uarfcn == 2997:
        return 1, 2110.0
    elif uarfcn == 10813:
        return 8, 940.0
    return None, None
