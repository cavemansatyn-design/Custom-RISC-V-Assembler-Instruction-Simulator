"""
RISC-V RV32I instruction decoder.

Decodes 32-bit instruction words into opcode, fields (rd, rs1, rs2, imm),
and instruction type for execution.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DecodedInstruction:
    """Decoded instruction fields."""
    raw: int  # 32-bit word
    opcode: str  # 7-bit
    rd: int
    rs1: int
    rs2: int
    imm: int
    funct3: str
    funct7: str
    format_type: str  # "R", "I", "S", "B", "J", "SYSTEM", "RST"


def decode(inst: int) -> DecodedInstruction:
    """
    Decode a 32-bit instruction into fields.
    """
    opcode = inst & 0x7F
    rd = (inst >> 7) & 0x1F
    funct3 = (inst >> 12) & 0x7
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F
    funct7 = (inst >> 25) & 0x7F

    imm_i = (inst >> 20)  # sign-extend 12-bit
    if imm_i & 0x800:
        imm_i |= -0x1000
    else:
        imm_i &= 0xFFF

    imm_s = ((inst >> 7) & 0x1F) | ((inst >> 25) << 5)
    if imm_s & 0x800:
        imm_s |= -0x1000
    else:
        imm_s &= 0xFFF

    # B-type: imm[12|10:5|4:1|11] * 2
    b12 = (inst >> 31) & 1
    b11 = (inst >> 7) & 1
    b10_5 = (inst >> 25) & 0x3F
    b4_1 = (inst >> 8) & 0xF
    imm_b = (b12 << 12) | (b11 << 11) | (b10_5 << 5) | (b4_1 << 1)
    if imm_b & 0x1000:
        imm_b |= -0x2000
    else:
        imm_b &= 0x1FFF

    # J-type: imm[20|10:1|11|19:12] * 2
    j20 = (inst >> 31) & 1
    j19_12 = (inst >> 12) & 0xFF
    j11 = (inst >> 20) & 1
    j10_1 = (inst >> 21) & 0x3FF
    imm_j = (j20 << 20) | (j19_12 << 12) | (j11 << 11) | (j10_1 << 1)
    if imm_j & 0x100000:
        imm_j |= -0x200000
    else:
        imm_j &= 0x1F_FFFF

    if opcode == 0x33:
        format_type = "R"
        imm = 0
    elif opcode in (0x03, 0x13, 0x67):
        format_type = "I"
        imm = imm_i
    elif opcode == 0x23:
        format_type = "S"
        imm = imm_s
    elif opcode == 0x63:
        format_type = "B"
        imm = imm_b
    elif opcode == 0x6F:
        format_type = "J"
        imm = imm_j
    elif opcode == 0x73:
        format_type = "SYSTEM"
        imm = 0
    elif opcode == 0x7F:
        format_type = "RST"
        imm = 0
    else:
        format_type = "UNKNOWN"
        imm = 0

    return DecodedInstruction(
        raw=inst,
        opcode=format(opcode, "07b"),
        rd=rd,
        rs1=rs1,
        rs2=rs2,
        imm=imm,
        funct3=format(funct3, "03b"),
        funct7=format(funct7, "07b"),
        format_type=format_type,
    )
