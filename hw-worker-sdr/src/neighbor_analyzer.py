import logging
from typing import List, Dict, Set, Tuple
from src.earfcn_validator import get_earfcn_info

logger = logging.getLogger("neighbor_analyzer")

def extract_neighbors_from_cell(cell: Dict) -> List[Dict]:
    """
    Extracts all SIB4, SIB5, SIB6, and SIB7 neighbors from a single cell info dictionary.
    Returns a list of neighbor info dicts.
    """
    neighbors = []
    raw_sibs = cell.get("raw_sibs", {})
    
    # 1. SIB4: Intra-frequency neighbors
    sib4_data = raw_sibs.get("sib4")
    if sib4_data:
        # SIB4 typically contains physical cell IDs of neighbor cells
        # e.g., intraFreqNeighCellList
        neigh_list = sib4_data.get("intraFreqNeighCellList", [])
        for n in neigh_list:
            pci = n.get("physCellId", 0)
            neighbors.append({
                "neighbor_earfcn": cell["earfcn"],
                "neighbor_band": cell["band"],
                "neighbor_freq": cell["freq_mhz"],
                "priority": 0,
                "thresh_x_high": 0,
                "thresh_x_low": 0,
                "bandwidth": cell["bandwidth"],
                "neighbor_type": "intra",
                "pci_or_psc": pci
            })

    # 2. SIB5: Inter-frequency neighbors (LTE -> LTE)
    sib5_data = raw_sibs.get("sib5")
    if sib5_data:
        # e.g., interFreqCarrierFreqList
        neigh_list = sib5_data.get("interFreqCarrierFreqList", [])
        for n in neigh_list:
            n_earfcn = n.get("dl-CarrierFreq")
            if n_earfcn is not None:
                n_band, n_freq = get_earfcn_info(n_earfcn)
                neighbors.append({
                    "neighbor_earfcn": n_earfcn,
                    "neighbor_band": n_band or 0,
                    "neighbor_freq": n_freq or 0.0,
                    "priority": n.get("cellReselectionPriority", 0),
                    "thresh_x_high": n.get("threshX-High", 0),
                    "thresh_x_low": n.get("threshX-Low", 0),
                    "bandwidth": n.get("allowedMeasBandwidth", "mbw25"),
                    "neighbor_type": "inter",
                    "pci_or_psc": 0
                })

    # 3. SIB6: Inter-RAT UTRAN (3G) neighbors (LTE -> 3G)
    sib6_data = raw_sibs.get("sib6")
    if sib6_data:
        # e.g., carrierFreqListUTRA-FDD
        neigh_list = sib6_data.get("carrierFreqListUTRA-FDD", [])
        for n in neigh_list:
            uarfcn = n.get("carrierFreq")
            if uarfcn is not None:
                # 3G UARFCN has different band calculations, we label as UARFCN
                neighbors.append({
                    "neighbor_earfcn": uarfcn,
                    "neighbor_band": 0,  # UTRA band
                    "neighbor_freq": 0.0,
                    "priority": n.get("cellReselectionPriority", 0),
                    "thresh_x_high": n.get("threshX-High", 0),
                    "thresh_x_low": n.get("threshX-Low", 0),
                    "bandwidth": "N/A",
                    "neighbor_type": "utran",
                    "pci_or_psc": 0
                })

    # 4. SIB7: Inter-RAT GERAN (2G) neighbors (LTE -> 2G)
    sib7_data = raw_sibs.get("sib7")
    if sib7_data:
        # e.g., carrierFreqsInfoList
        neigh_list = sib7_data.get("carrierFreqsInfoList", [])
        for n in neigh_list:
            cinfo = n.get("carrierFreqs", {})
            arfcn = cinfo.get("startingARFCN")
            if arfcn is not None:
                neighbors.append({
                    "neighbor_earfcn": arfcn,
                    "neighbor_band": 0,  # GERAN band
                    "neighbor_freq": 0.0,
                    "priority": n.get("commonInfo", {}).get("cellReselectionPriority", 0),
                    "thresh_x_high": 0,
                    "thresh_x_low": 0,
                    "bandwidth": "N/A",
                    "neighbor_type": "geran",
                    "pci_or_psc": 0
                })

    return neighbors

def analyze_neighbor_map(cells: List[Dict]) -> List[Dict]:
    """
    Analyzes bidirectional/unidirectional/unscanned relationships among scanned cells.
    Returns a list of relation dictionaries conforming to gRPC NeighborRelation.
    """
    scanned_earfcns = {c["earfcn"]: c for c in cells}
    relations = []
    visited_pairs = set()

    for cell in cells:
        earfcn_a = cell["earfcn"]
        pci_a = cell["pci"]
        cell_a_label = f"{earfcn_a} (PCI {pci_a})"
        
        # Get neighbors of Cell A
        neighbors = extract_neighbors_from_cell(cell)
        
        for neigh in neighbors:
            if neigh["neighbor_type"] not in ("intra", "inter"):
                # Non-LTE RATs are unidirectional or unscanned LTE relations
                continue

            earfcn_b = neigh["neighbor_earfcn"]
            
            if earfcn_b in scanned_earfcns:
                cell_b = scanned_earfcns[earfcn_b]
                pci_b = cell_b["pci"]
                cell_b_label = f"{earfcn_b} (PCI {pci_b})"
                
                # Check if reciprocal relationship exists
                b_neighbors = extract_neighbors_from_cell(cell_b)
                b_has_a = any(bn["neighbor_earfcn"] == earfcn_a for bn in b_neighbors if bn["neighbor_type"] in ("intra", "inter"))
                
                pair_key = tuple(sorted([earfcn_a, earfcn_b]))
                if b_has_a:
                    # Bidirectional
                    if pair_key not in visited_pairs:
                        relations.append({
                            "cell_a": cell_a_label,
                            "cell_b": cell_b_label,
                            "direction": "↔",
                            "relation_type": "Bidirectional"
                        })
                        visited_pairs.add(pair_key)
                else:
                    # Unidirectional (A -> B)
                    relations.append({
                        "cell_a": cell_a_label,
                        "cell_b": cell_b_label,
                        "direction": "→",
                        "relation_type": "Unidirectional"
                    })
            else:
                # Unscanned
                cell_b_label = f"{earfcn_b} (Taranmamis)"
                relations.append({
                    "cell_a": cell_a_label,
                    "cell_b": cell_b_label,
                    "direction": "→",
                    "relation_type": "Unscanned"
                })

    return relations

def get_unscanned_earfcns(cells: List[Dict]) -> List[int]:
    """
    Returns a sorted list of unique EARFCNs discovered as inter-frequency neighbors (SIB5)
    but not present in the scanned cells list.
    """
    scanned_set = {c["earfcn"] for c in cells}
    unscanned_set = set()
    
    for cell in cells:
        neighbors = extract_neighbors_from_cell(cell)
        for n in neighbors:
            if n["neighbor_type"] == "inter":
                n_earfcn = n["neighbor_earfcn"]
                if n_earfcn not in scanned_set:
                    unscanned_set.add(n_earfcn)
                    
    return sorted(list(unscanned_set))
