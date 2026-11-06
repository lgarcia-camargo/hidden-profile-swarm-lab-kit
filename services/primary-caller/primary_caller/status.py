from __future__ import annotations


def raw_to_board(raw: str) -> str:
    """Map ledger scorer output to public board labels."""
    u = (raw or "").upper()
    if u == "TRUE":
        return "PASS"
    if u == "FALSE":
        return "FAIL"
    return "PENDING"
