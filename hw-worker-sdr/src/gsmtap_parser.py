import struct
from typing import Optional, Dict

def parse_gsmtap_packet(data: bytes) -> Optional[dict]:
    """
    Parses a raw GSMTAP packet, extracts header details, and decodes Layer 3 RR messages.
    """
    if len(data) < 16:
        return None
    
    version = data[0]
    hdr_len = data[1]
    header_size = hdr_len * 4
    
    if len(data) < header_size:
        return None
        
    payload_type = data[2]
    sub_type = data[3]
    arfcn_raw = (data[4] << 8) | data[5]
    arfcn = arfcn_raw & 0x7fff  # Clear uplink bit
    timeslot = data[6]
    
    signal_dbm = -100
    if len(data) >= 14:
        # Signed 8-bit signal level
        signal_dbm = struct.unpack('b', bytes([data[13]]))[0]
        
    payload = data[header_size:]
    if len(payload) < 3 or payload[1] != 0x06:
        return None
        
    msg_type = payload[2]
    
    # SI3
    if msg_type == 0x1b:
        try:
            cell_id = (payload[3] << 8) | payload[4]
            mcc_d1 = payload[5] & 0x0f
            mcc_d2 = (payload[5] >> 4) & 0x0f
            mcc_d3 = payload[6] & 0x0f
            mcc = f"{mcc_d1}{mcc_d2}{mcc_d3}"
            
            mnc_d1 = payload[7] & 0x0f
            mnc_d2 = (payload[7] >> 4) & 0x0f
            mnc_d3 = (payload[6] >> 4) & 0x0f
            mnc = f"{mnc_d1}{mnc_d2}" if mnc_d3 == 0x0f else f"{mnc_d1}{mnc_d2}{mnc_d3}"
            lac = (payload[8] << 8) | payload[9]
            
            return {
                "si_type": "SI3",
                "arfcn": arfcn,
                "cell_id": cell_id,
                "lac": lac,
                "mcc": mcc,
                "mnc": mnc,
                "plmn": f"{mcc}{mnc}",
                "signal_dbm": signal_dbm
            }
        except Exception:
            pass
            
    # SI2
    elif msg_type == 0x1a:
        try:
            if (payload[6] & 0xc0) == 0x00:  # Format 0
                ba_list = []
                for i in range(16):
                    byte_val = payload[6 + i]
                    for bit in range(8):
                        if (byte_val >> bit) & 1:
                            ba_list.append(i * 8 + bit + 1)
                return {
                    "si_type": "SI2",
                    "arfcn": arfcn,
                    "ba_list": sorted(ba_list),
                    "signal_dbm": signal_dbm
                }
        except Exception:
            pass
            
    # SI2quater
    elif msg_type == 0x07:
        parsed_res = {
            "si_type": "SI2quater",
            "arfcn": arfcn,
            "signal_dbm": signal_dbm
        }
        # payload[3:] strips pseudo-length, protocol discriminator (RR), and msg_type
        native_parsed = parse_si2quater_payload(payload[3:])
        parsed_res.update(native_parsed)
        return parsed_res
        
    # SI2bis / SI2ter
    elif msg_type == 0x02:
        return {
            "si_type": "SI2bis",
            "arfcn": arfcn,
            "signal_dbm": signal_dbm
        }
    elif msg_type == 0x03:
        return {
            "si_type": "SI2ter",
            "arfcn": arfcn,
            "signal_dbm": signal_dbm
        }
        
    return None

def parse_si2quater_payload(payload: bytes) -> dict:
    """
    Skeleton bit-level parser for SI2quater Rest Octets (3GPP TS 44.018 Section 9.1.54).
    This establishes the structural scaffolding placeholder.
    In the future, this will native bit-decode BA_IND, 3G_BA_IND, MP_CHANGE_MARK,
    SI2quater_INDEX, SI2quater_COUNT, UTRAN FDD, and E-UTRAN Descriptions.
    """
    # 3GPP TS 44.018 spec parameters:
    ba_ind = 0
    three_g_ba_ind = 0
    mp_change_mark = 0
    si2quater_index = 0
    si2quater_count = 0
    
    # Decoded target structures:
    earfcns = []
    uarfcns = []
    
    # Structure skeleton reflecting expected metadata
    return {
        "ba_ind": ba_ind,
        "three_g_ba_ind": three_g_ba_ind,
        "mp_change_mark": mp_change_mark,
        "si2quater_index": si2quater_index,
        "si2quater_count": si2quater_count,
        "earfcns": earfcns,
        "uarfcns": uarfcns,
        "scaffolding": True
    }
