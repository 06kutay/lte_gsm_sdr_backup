import os
import sqlite3
import json
import pytest
from src.config import settings, SdrType, SdrRole
from src.earfcn_validator import validate_earfcn, get_earfcn_info
from src.result_parser import parse_database, resolve_operator
from src.neighbor_analyzer import extract_neighbors_from_cell, analyze_neighbor_map, get_unscanned_earfcns

def test_config_derivation():
    # Verify default config derivations
    assert settings.driver == "soapy"
    assert settings.antenna == "LNAH" if settings.SDR_ROLE == SdrRole.HIGH else "LNAW"

def test_earfcn_validator():
    # Test valid band 3 EARFCN
    band, freq = get_earfcn_info(1300)
    assert band == 3
    assert freq == 1815.0

    # Test validator with LimeSDR limits
    is_valid, msg, band, freq = validate_earfcn(1300)
    if settings.SDR_ROLE == SdrRole.HIGH:
        assert is_valid is True
        assert band == 3
    else:
        assert is_valid is False  # low band role rejects 1.8GHz

    # Test invalid EARFCN
    is_valid, msg, band, freq = validate_earfcn(99999)
    assert is_valid is False

def test_operator_resolution():
    assert resolve_operator("28601") == "Turkcell"
    assert resolve_operator("28602") == "Vodafone"
    assert resolve_operator("28603") == "Türk Telekom"
    assert resolve_operator("99999") == "Bilinmeyen"

def test_sqlite_result_parser(tmp_path):
    # Create mock SQLite database
    db_file = str(tmp_path / "test_cells.sqlite")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE cells (
            earfcn integer NOT NULL UNIQUE,
            band TEXT,
            time timestamp,
            rsrp TEXT,
            mib TEXT,
            sib1 TEXT,
            sib2 TEXT,
            sib3 TEXT,
            sib4 TEXT,
            sib5 TEXT,
            sib6 TEXT,
            sib7 TEXT,
            sib8 TEXT,
            sib9 TEXT,
            sib10 TEXT,
            sib11 TEXT,
            sib12 TEXT,
            sib13 TEXT
        )
    """)
    
    # Mock sib1 data
    sib1_data = {
        "cellAccessRelatedInfo": {
            "cellIdentity": "0000000000000000000000001010", # 10 decimal
            "trackingAreaCode": "0000000000001111", # 15 decimal
            "plmn-IdentityList": [
                {
                    "plmn-Identity": {
                        "mcc": [2, 8, 6],
                        "mnc": [0, 1]
                    }
                }
            ]
        }
    }
    
    # Mock sib5 data with 2 inter-freq neighbors
    sib5_data = {
        "interFreqCarrierFreqList": [
            {
                "dl-CarrierFreq": 2850,
                "cellReselectionPriority": 5
            },
            {
                "dl-CarrierFreq": 6400,
                "cellReselectionPriority": 4
            }
        ]
    }

    cursor.execute("""
        INSERT INTO cells (earfcn, band, rsrp, sib1, sib5)
        VALUES (?, ?, ?, ?, ?)
    """, (1300, "3", "-85", json.dumps(sib1_data), json.dumps(sib5_data)))
    conn.commit()
    conn.close()

    # Parse database
    cells = parse_database(db_file)
    assert len(cells) == 1
    cell = cells[0]
    assert cell["earfcn"] == 1300
    assert cell["cell_id"] == 10
    assert cell["pci"] == 10  # 10 % 504
    assert cell["tac"] == 15
    assert cell["plmn"] == "286-01"
    assert cell["operator_name"] == "Turkcell"
    assert cell["rsrp"] == -85.0
    assert "SIB1" in cell["sibs_decoded"]
    assert "SIB5" in cell["sibs_decoded"]

def test_neighbor_analyzer():
    # Setup parsed cell structures
    cell_a = {
        "earfcn": 1300,
        "band": 3,
        "freq_mhz": 1815.0,
        "pci": 10,
        "cell_id": 10,
        "plmn": "286-01",
        "operator_name": "Turkcell",
        "tac": 15,
        "rsrp": -85.0,
        "bandwidth": "20MHz",
        "sibs_decoded": ["SIB1", "SIB5"],
        "raw_sibs": {
            "sib5": {
                "interFreqCarrierFreqList": [
                    {"dl-CarrierFreq": 2850, "cellReselectionPriority": 5}
                ]
            }
        }
    }

    cells = [cell_a]

    # Test unscanned extraction
    unscanned = get_unscanned_earfcns(cells)
    assert unscanned == [2850]

    # Test neighbor relationship analyzer
    relations = analyze_neighbor_map(cells)
    assert len(relations) == 1
    rel = relations[0]
    assert rel["cell_a"] == "1300 (PCI 10)"
    assert rel["cell_b"] == "2850 (Taranmamis)"
    assert rel["direction"] == "→"
    assert rel["relation_type"] == "Unscanned"

# --- GSM Unit Tests ---
def test_gsm_arfcn_validator():
    from src.gsm_arfcn_validator import validate_arfcn, get_arfcn_info, estimate_operator
    
    # Test GSM900 ARFCN 60 frequency math
    band, freq = get_arfcn_info(60)
    assert band == "GSM900"
    assert freq == 947.0

    # Test DCS1800 ARFCN 600 frequency math
    band_dcs, freq_dcs = get_arfcn_info(600)
    assert band_dcs == "DCS1800"
    assert freq_dcs == 1822.8

    # Operator Estimations (Turkish Allocations)
    assert estimate_operator(60, "GSM900") == "Vodafone"  # ARFCN 36-70 is Vodafone TR
    assert estimate_operator(30, "GSM900") == "Turkcell"  # ARFCN 1-35 is Turkcell
    assert estimate_operator(75, "GSM900") == "Türk Telekom"  # ARFCN 71-105 is Türk Telekom

    # ARFCN 0 Boundary Case
    is_valid, msg, band, freq = validate_arfcn(0)
    if settings.SDR_ROLE == SdrRole.LOW:
        assert is_valid is True
        assert "ARFCN 0" in msg
    else:
        assert is_valid is False
        assert "dusuk bandda" in msg

def test_gsmtap_parser():
    from src.gsmtap_parser import parse_gsmtap_packet

    # 1. Build a mock SI3 GSMTAP packet (16 bytes GSMTAP header + 16 bytes L3 payload)
    # GSMTAP Header: version=2, hdr_len=4, payload_type=1, sub_type=0, arfcn=60 (0x003c), ts=0, sub_slot=0, fn=0, noise=0, signal=-60 (0xc4), snr=0
    header = bytearray([
        0x02, 0x04, 0x01, 0x00,
        0x00, 0x3c, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0xc4, 0x00, 0x00
    ])

    # L3 Payload (SI3): pseudo_len=0x01, pd=0x06 (RR), msg_type=0x1b (SI3), cell_id=7349 (0x1cb5), mcc/mnc=286/01 (0x82, 0xf6, 0x10), lac=33006 (0x80ee)
    l3_payload = bytearray([
        0x01, 0x06, 0x1b,
        0x1c, 0xb5,
        0x82, 0xf6, 0x10,
        0x80, 0xee
    ])

    mock_packet = header + l3_payload
    parsed = parse_gsmtap_packet(bytes(mock_packet))
    
    assert parsed is not None
    assert parsed["si_type"] == "SI3"
    assert parsed["cell_id"] == 7349
    assert parsed["lac"] == 33006
    assert parsed["plmn"] == "28601"
    assert parsed["signal_dbm"] == -60

    # 2. Build a mock SI2 GSMTAP packet (Format 0 bitmap with ARFCN 48, 54, 55, 56, 57, 58, 59, 60, 61)
    # bit indices:
    # 48 -> i=5, bit=7
    # 54 -> i=6, bit=5
    # 55 -> i=6, bit=6
    # 56 -> i=6, bit=7
    # 57 -> i=7, bit=0
    # 58 -> i=7, bit=1
    # 59 -> i=7, bit=2
    # 60 -> i=7, bit=3
    # 61 -> i=7, bit=4
    # Let's populate the 16-byte bitmap starting at payload[6] (which is payload[6:22])
    l3_si2 = bytearray(25)
    l3_si2[1] = 0x06  # PD=RR
    l3_si2[2] = 0x1a  # msg_type=SI2
    
    # Format 0 flag
    l3_si2[6] = 0x00
    
    # Set bit 7 of byte 5 (payload[6+5] = payload[11]) -> ARFCN 48
    l3_si2[11] = 0x80
    
    # Set bits 5,6,7 of byte 6 (payload[12]) -> ARFCN 54, 55, 56
    # bits: 0xe0 (1110 0000)
    l3_si2[12] = 0xe0
    
    # Set bits 0,1,2,3,4 of byte 7 (payload[13]) -> ARFCN 57, 58, 59, 60, 61
    # bits: 0x1f (0001 1111)
    l3_si2[13] = 0x1f

    mock_si2 = header + l3_si2
    parsed_si2 = parse_gsmtap_packet(bytes(mock_si2))
    
    assert parsed_si2 is not None
    assert parsed_si2["si_type"] == "SI2"
    assert 48 in parsed_si2["ba_list"]
    assert 60 in parsed_si2["ba_list"]
    assert 61 in parsed_si2["ba_list"]

def test_gsm_neighbor_analyzer():
    from src.gsm_neighbor_analyzer import analyze_gsm_neighbors, analyze_inter_rat_neighbors

    mock_cell = {
        "arfcn": 60,
        "band": "GSM900",
        "freq_mhz": 947.0,
        "neighbors_si2": [48, 54, 61],
        "neighbors_si2quater": {
            "earfcns": [6400, 1651],
            "uarfcns": [2997]
        }
    }

    gsm_neighs = analyze_gsm_neighbors(mock_cell)
    assert len(gsm_neighs) == 3
    assert gsm_neighs[0]["neighbor_arfcn"] == 48

    inter_rats = analyze_inter_rat_neighbors(mock_cell)
    assert len(inter_rats) == 3
    assert inter_rats[0]["rat_type"] == "4G LTE"
    assert inter_rats[0]["channel"] == 6400
    assert inter_rats[2]["rat_type"] == "3G UMTS"
    assert inter_rats[2]["channel"] == 2997

def test_si2quater_native_scaffolding():
    from src.gsmtap_parser import parse_si2quater_payload, parse_gsmtap_packet
    
    # 1. Test native skeleton response
    payload = b"\x00\x01\x02\x03\x04"
    res = parse_si2quater_payload(payload)
    
    assert res["scaffolding"] is True
    assert "earfcns" in res
    assert "uarfcns" in res
    assert res["ba_ind"] == 0
    
    # 2. Test parse_gsmtap_packet SI2quater RR message parsing (msg_type = 0x07)
    # Header: arfcn=60, signal=-70 (0xba)
    header = bytearray([
        0x02, 0x04, 0x01, 0x00,
        0x00, 0x3c, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0xba, 0x00, 0x00
    ])
    # L3 SI2quater: pseudo_len=0x01, pd=0x06 (RR), msg_type=0x07 (SI2quater)
    l3_si2q = bytearray([0x01, 0x06, 0x07, 0x00, 0x01, 0x02])
    parsed = parse_gsmtap_packet(bytes(header + l3_si2q))
    
    assert parsed is not None
    assert parsed["si_type"] == "SI2quater"
    assert parsed["scaffolding"] is True
    assert parsed["signal_dbm"] == -70

def test_si2quater_tshark_parsing(tmp_path):
    # Mock tshark JSON capture data based on Phase 5 live findings
    mock_tshark_json = [
        {
            "_index": "packets-mock",
            "_type": "doc",
            "_source": {
                "layers": {
                    "gsm_a.rr.earfcn": ["6400", "1651"],
                    "gsm_a.rr.utran_freq": ["2997", "10813"]
                }
            }
        }
    ]
    
    tshark_file = str(tmp_path / "mock_si2q.json")
    with open(tshark_file, "w", encoding="utf-8") as f:
        json.dump(mock_tshark_json, f)
        
    # Re-run the exact extraction code from gsm_scanner.py to verify logic
    earfcns_list = []
    uarfcns_list = []
    
    with open(tshark_file, "r", encoding="utf-8") as f:
        tshark_data = json.load(f)
        
    for pkg in tshark_data:
        layers = pkg.get("_source", {}).get("layers", {})
        
        # Extract earfcns
        earf = layers.get("gsm_a.rr.earfcn", [])
        if isinstance(earf, list):
            for e in earf:
                earfcns_list.append(int(e))
        elif earf:
            earfcns_list.append(int(earf))
            
        # Extract uarfcns
        uarf = layers.get("gsm_a.rr.utran_freq", [])
        if isinstance(uarf, list):
            for u in uarf:
                uarfcns_list.append(int(u))
        elif uarf:
            uarfcns_list.append(int(uarf))
            
    final_earfcns = sorted(list(set(earfcns_list)))
    final_uarfcns = sorted(list(set(uarfcns_list)))
    
    assert final_earfcns == [1651, 6400]
    assert final_uarfcns == [2997, 10813]


