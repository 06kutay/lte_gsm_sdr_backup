from typing import Tuple, Optional
from src.config import settings, SdrType, SdrRole

def get_earfcn_info(earfcn: int) -> Tuple[Optional[int], Optional[float]]:
    """
    Returns (band, downlink_frequency_mhz) for a given E-UTRA absolute radio frequency channel number (EARFCN)
    based on 3GPP TS 36.101.
    """
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

def validate_earfcn(earfcn: int) -> Tuple[bool, str, Optional[int], Optional[float]]:
    """
    Validates if an EARFCN can be scanned by this specific worker instance
    based on TS 36.101, SDR model limitations, and the worker's band role.
    
    Returns (is_valid, error_message, band, frequency_mhz)
    """
    band, freq = get_earfcn_info(earfcn)
    if band is None or freq is None:
        return False, f"EARFCN {earfcn} tanimsiz veya 3GPP TS 36.101 kapsami disinda.", None, None

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

    return True, "Gecerli", band, freq
