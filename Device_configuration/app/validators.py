# app/validators.py
import ipaddress
from typing import List, Tuple

VENDOR_KEYWORDS = {
    "cisco": "interface",
    "juniper": "set",
    "versa": "system",
}


def validate_ipv4(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return addr.version == 4
    except ValueError:
        return False


def validate_vendor_config(vendor: str, config: str) -> bool:
    key = vendor.strip().lower()
    if key not in VENDOR_KEYWORDS:
        raise ValueError(f"Unsupported vendor '{vendor}'. Supported: Cisco, Juniper, Versa.")
    required_kw = VENDOR_KEYWORDS[key]
    return required_kw in config.lower()


def run_validation(vendor: str, ip: str, config: str) -> Tuple[str, List[str]]:
    """
    Returns: ("PASSED"/"FAILED", [errors])
    """
    errors: List[str] = []

    if not validate_ipv4(ip):
        errors.append("Invalid IPv4 address.")

    try:
        ok_vendor = validate_vendor_config(vendor, config)
        if not ok_vendor:
            errors.append(f"Config missing required keyword for vendor '{vendor}'.")
    except ValueError as e:
        errors.append(str(e))

    status = "PASSED" if len(errors) == 0 else "FAILED"
    return status, errors
