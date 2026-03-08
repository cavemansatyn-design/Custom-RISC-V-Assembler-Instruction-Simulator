"""
RISC-V register name and number mapping.

Supports both ABI names (zero, ra, sp, ...) and numeric names (x0-x31).
"""

from typing import Optional

# ABI names to register number (0-31)
ABI_TO_NUM: dict[str, int] = {
    "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
    "t0": 5, "t1": 6, "t2": 7, "s0": 8, "fp": 8, "s1": 9,
    "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17,
    "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23, "s8": 24, "s9": 25,
    "s10": 26, "s11": 27, "t3": 28, "t4": 29, "t5": 30, "t6": 31,
}

# x0..x31 also valid
for i in range(32):
    ABI_TO_NUM[f"x{i}"] = i


def parse_register(token: str) -> int:
    """
    Parse a register token (e.g. 'x5', 't0', 'sp') to register number 0-31.

    Raises:
        ValueError: if token is not a valid register name.
    """
    token = token.strip().lower()
    if token not in ABI_TO_NUM:
        raise ValueError(f"Invalid register name: {token}")
    return ABI_TO_NUM[token]


def is_valid_register(token: str) -> bool:
    """Return True if token is a valid register name."""
    return token.strip().lower() in ABI_TO_NUM


def reg_to_bin(reg_num: int, width: int = 5) -> str:
    """Convert register number to width-bit binary string (no 0b prefix)."""
    if not 0 <= reg_num <= 31:
        raise ValueError(f"Register number must be 0-31, got {reg_num}")
    return format(reg_num, f"0{width}b")
