from typing import Tuple, Optional, Dict
from src.config import settings, SdrType, SdrRole

def get_arfcn_info(arfcn: int) -> Tuple[Optional[str], Optional[float]]:
    """
    Returns (band, downlink_frequency_mhz) for a given ARFCN
    based on 3GPP TS 45.005.
    """
    # GSM900 (P-GSM)
    if 1 <= arfcn <= 124:
        return "GSM900", 935.0 + 0.2 * arfcn
    # GSM900 (E-GSM)
    elif 975 <= arfcn <= 1023:
        return "GSM900", 935.0 + 0.2 * (arfcn - 1024)
    # E-GSM 900 Boundary
    elif arfcn == 0:
        return "GSM900", 935.0
    # DCS1800
    elif 512 <= arfcn <= 885:
        return "DCS1800", 1805.2 + 0.2 * (arfcn - 512)
    return None, None

def validate_arfcn(arfcn: int) -> Tuple[bool, str, Optional[str], Optional[float]]:
    """
    Validates if an ARFCN can be scanned by this specific worker instance
    based on TS 45.005, SDR model limitations, and the worker's band role.
    
    Returns (is_valid, error_message, band, frequency_mhz)
    """
    band, freq = get_arfcn_info(arfcn)
    if band is None or freq is None:
        return False, f"ARFCN {arfcn} tanimsiz veya 3GPP TS 45.005 kapsami disinda.", None, None

    # Check hardware model limits (limesdr vs usrp)
    if settings.SDR_TYPE == SdrType.LIMESDR:
        if not (10.0 <= freq <= 3500.0):
            return False, f"Frekans ({freq:.1f} MHz) LimeSDR Mini 2.0 donanim limitleri (10 MHz - 3.5 GHz) disinda.", band, freq
    else:  # USRP
        if not (70.0 <= freq <= 6000.0):
            return False, f"Frekans ({freq:.1f} MHz) USRP B205 donanim limitleri (70 MHz - 6 GHz) disinda.", band, freq

    # Check worker role bounds
    threshold = settings.FREQ_THRESHOLD_MHZ
    if settings.SDR_ROLE == SdrRole.HIGH:
        if freq < threshold:
            return False, f"Frekans ({freq:.1f} MHz) dusuk bandda. Bu worker yuksek band (>= {threshold} MHz) taramasi icin atanmis.", band, freq
    else:  # LOW
        if freq >= threshold:
            return False, f"Frekans ({freq:.1f} MHz) yuksek bandda. Bu worker dusuk band (< {threshold} MHz) taramasi icin atanmis.", band, freq

    if arfcn == 0:
        return True, "ARFCN 0 (E-GSM 935.0 MHz) gecerlidir ancak bazi sistemlerde ozel anlam tasir (Sinir durum).", band, freq

    return True, "Gecerli", band, freq

def estimate_operator(arfcn: int, band: str) -> str:
    """
    Estimates the network operator based on local regulatory allocations in Turkey
    """
    if band == "GSM900":
        if 1 <= arfcn <= 35:
            return "Turkcell"
        elif 36 <= arfcn <= 70:
            return "Vodafone"
        elif 71 <= arfcn <= 105:
            return "Türk Telekom"
    elif band == "DCS1800":
        if 512 <= arfcn <= 586:
            return "Vodafone"
        elif 587 <= arfcn <= 661:
            return "Türk Telekom"
        elif 662 <= arfcn <= 736:
            return "Turkcell"
    return "Bilinmeyen"
