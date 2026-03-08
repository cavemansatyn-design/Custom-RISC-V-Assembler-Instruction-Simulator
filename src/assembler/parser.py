"""
Assembly parser for RISC-V RV32I.

Parses .asm files: strips comments, handles labels, and produces a list of
parsed lines (instruction or label) for the encoder. Performs syntax validation.
"""

import re
from typing import NamedTuple, Optional
from dataclasses import dataclass
from pathlib import Path

from .instruction_set import is_valid_instruction, FormatType, get_instruction
from .registers import parse_register, is_valid_register


@dataclass
class ParsedLine:
    """Single parsed line: either a label or an instruction with operands."""
    line_no: int
    raw: str
    label: Optional[str] = None   # if line is "loop:" or ends with ":"
    mnemonic: Optional[str] = None
    operands: list[str] = None

    def __post_init__(self):
        if self.operands is None:
            self.operands = []


def strip_comment(line: str) -> str:
    """Remove comment (from # to end of line)."""
    i = line.find("#")
    return line[:i].strip() if i >= 0 else line.strip()


def split_operands(operand_str: str) -> list[str]:
    """Split operand string by comma, then strip each. Handles offset(reg) as one token."""
    if not operand_str or not operand_str.strip():
        return []
    parts: list[str] = []
    current = []
    depth = 0  # paren depth
    for c in operand_str.strip() + ",":
        if c == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            current.append(c)
    return [p for p in parts if p]


def parse_line(line: str, line_no: int) -> ParsedLine:
    """
    Parse one line of assembly into label (optional), mnemonic, and operands.

    Raises:
        ValueError: on invalid syntax (unknown instruction, bad register, etc.).
    """
    raw = line
    s = strip_comment(line)
    if not s:
        return ParsedLine(line_no=line_no, raw=raw)

    label = None
    # Label at start: "loop:" or "main:"
    if ":" in s:
        idx = s.index(":")
        label = s[:idx].strip()
        s = s[idx + 1:].strip()
        if not label:
            raise ValueError(f"Line {line_no}: empty label")
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", label):
            raise ValueError(f"Line {line_no}: invalid label name '{label}'")

    if not s:
        return ParsedLine(line_no=line_no, raw=raw, label=label)

    # First token is mnemonic
    parts = s.split(maxsplit=1)
    mnemonic = parts[0].strip().lower()
    operand_str = parts[1].strip() if len(parts) > 1 else ""

    if not is_valid_instruction(mnemonic):
        raise ValueError(f"Line {line_no}: illegal instruction '{mnemonic}'")

    operands = split_operands(operand_str)
    idef = get_instruction(mnemonic)

    # Operand count check
    if idef.format_type == FormatType.R:
        if len(operands) != 3:
            raise ValueError(f"Line {line_no}: R-type '{mnemonic}' requires 3 operands (rd, rs1, rs2)")
        for t in operands:
            if not is_valid_register(t):
                raise ValueError(f"Line {line_no}: invalid register name '{t}'")
    elif idef.format_type == FormatType.I:
        if mnemonic == "lw":
            if len(operands) != 2:
                raise ValueError(f"Line {line_no}: 'lw' requires 2 operands (rd, offset(rs1))")
        elif mnemonic == "addi":
            if len(operands) != 3:
                raise ValueError(f"Line {line_no}: 'addi' requires 3 operands (rd, rs1, imm)")
        elif mnemonic == "jalr":
            if len(operands) != 3 and len(operands) != 2:
                raise ValueError(f"Line {line_no}: 'jalr' requires 2 or 3 operands (rd, rs1, imm?)")
        for t in operands:
            if "(" in t:
                continue
            if t.lstrip("-").isdigit():
                continue
            if is_valid_register(t):
                continue
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", t):
                raise ValueError(f"Line {line_no}: invalid operand '{t}'")
    elif idef.format_type == FormatType.S:
        if len(operands) != 2:
            raise ValueError(f"Line {line_no}: 'sw' requires 2 operands (rs2, offset(rs1))")
    elif idef.format_type == FormatType.B:
        if len(operands) != 3:
            raise ValueError(f"Line {line_no}: B-type '{mnemonic}' requires 3 operands (rs1, rs2, label)")
        for i, t in enumerate(operands[:2]):
            if not is_valid_register(t):
                raise ValueError(f"Line {line_no}: invalid register '{t}'")
    elif idef.format_type == FormatType.J:
        if len(operands) != 2:
            raise ValueError(f"Line {line_no}: 'jal' requires 2 operands (rd, label)")
        if not is_valid_register(operands[0]):
            raise ValueError(f"Line {line_no}: invalid register '{operands[0]}'")
    elif idef.format_type == FormatType.PSEUDO:
        if mnemonic in ("halt", "rst") and len(operands) != 0:
            raise ValueError(f"Line {line_no}: '{mnemonic}' takes no operands")

    return ParsedLine(line_no=line_no, raw=raw, label=label, mnemonic=mnemonic, operands=operands)


def parse_imm(s: str) -> int:
    """Parse immediate: decimal, hex (0x), or label (returned as-is for later resolution)."""
    s = s.strip()
    if not s:
        raise ValueError("Empty immediate")
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    if s.startswith("-") and s[1:].lstrip("-").isdigit():
        return int(s, 10)
    if s.isdigit():
        return int(s, 10)
    # Label: return as special or we use string; encoder will resolve
    raise ValueError(f"Invalid immediate or unresolved label: {s}")


def parse_offset_rs1(operand: str) -> tuple[int, int]:
    """Parse 'offset(rs1)' or 'imm(rs1)' into (offset, rs1_num). Supports decimal and 0x hex."""
    operand = operand.strip()
    m = re.match(r"^(-?0x[0-9a-fA-F]+|-?\d+)\s*\(\s*(\w+)\s*\)$", operand)
    if not m:
        raise ValueError(f"Expected offset(rs1) form, got: {operand}")
    off_str = m.group(1)
    offset = int(off_str, 16) if off_str.strip().lower().startswith("0x") else int(off_str, 10)
    rs1 = parse_register(m.group(2))
    return offset, rs1


def parse_file(path: Path) -> list[ParsedLine]:
    """
    Parse an entire assembly file. Does not resolve labels; that is done in encoder.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    result = []
    for i, line in enumerate(lines, start=1):
        try:
            result.append(parse_line(line, i))
        except ValueError as e:
            raise ValueError(f"{path}:{i}: {e}") from e
    return result
