"""API facade for the BWT package."""

from bwt_api.bwt_api import BwtApi
from bwt_api.silk_api import BwtSilkApi
from bwt_api.smart_dos_api import BwtSmartDosApi

__all__ = ["BwtApi", "BwtSilkApi", "BwtSmartDosApi"]

def treated_to_blended(treated: int, hardness_in: int, hardness_out: int) -> float:
    if hardness_in == 0 or hardness_in == hardness_out:
        return treated

    return treated / (1.0 - hardness_out / hardness_in)