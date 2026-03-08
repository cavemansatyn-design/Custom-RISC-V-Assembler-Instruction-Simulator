"""
RISC-V RV32I instruction set definitions for the assembler.

Defines opcodes, funct3, funct7, and instruction formats for the supported
RV32I subset plus bonus instructions (rst, halt).
"""

from typing import NamedTuple, Optional
from enum import Enum


class FormatType(str, Enum):
    """Instruction format types per RISC-V specification."""
    R = "R"
    I = "I"
    S = "S"
    B = "B"
    J = "J"
    PSEUDO = "PSEUDO"  # rst, halt


class InstructionDef(NamedTuple):
    """Definition of a single instruction: format and encoding bits."""
    mnemonic: str
    format_type: FormatType
    opcode: str  # 7-bit binary string
    funct3: Optional[str] = None  # 3-bit, for R/I/S/B
    funct7: Optional[str] = None  # 7-bit, for R-type


# RV32I opcodes (7-bit)
OPCODE_OP = "0110011"   # R-type: add, sub, slt, srl, or, and
OPCODE_OP_IMM = "0010011"  # I-type: addi
OPCODE_LOAD = "0000011"   # I-type: lw
OPCODE_JALR = "1100111"   # I-type: jalr
OPCODE_STORE = "0100011"  # S-type: sw
OPCODE_BRANCH = "1100011" # B-type: beq, bne, blt
OPCODE_JAL = "1101111"    # J-type: jal
OPCODE_SYSTEM = "1110011" # ecall/ebreak -> we use for halt

# Bonus: custom opcode for rst (invalid in RV32I, simulator treats specially)
OPCODE_RST = "1111111"

# Instruction definitions: mnemonic -> InstructionDef
INSTRUCTIONS: dict[str, InstructionDef] = {
    # R-type
    "add":  InstructionDef("add",  FormatType.R, OPCODE_OP, funct3="000", funct7="0000000"),
    "sub":  InstructionDef("sub",  FormatType.R, OPCODE_OP, funct3="000", funct7="0100000"),
    "slt":  InstructionDef("slt",  FormatType.R, OPCODE_OP, funct3="010", funct7="0000000"),
    "srl":  InstructionDef("srl",  FormatType.R, OPCODE_OP, funct3="101", funct7="0000000"),
    "or":   InstructionDef("or",   FormatType.R, OPCODE_OP, funct3="110", funct7="0000000"),
    "and":  InstructionDef("and",  FormatType.R, OPCODE_OP, funct3="111", funct7="0000000"),
    # I-type
    "lw":   InstructionDef("lw",   FormatType.I, OPCODE_LOAD, funct3="010"),
    "addi": InstructionDef("addi", FormatType.I, OPCODE_OP_IMM, funct3="000"),
    "jalr": InstructionDef("jalr", FormatType.I, OPCODE_JALR, funct3="000"),
    # S-type
    "sw":   InstructionDef("sw",   FormatType.S, OPCODE_STORE, funct3="010"),
    # B-type
    "beq":  InstructionDef("beq",  FormatType.B, OPCODE_BRANCH, funct3="000"),
    "bne":  InstructionDef("bne",  FormatType.B, OPCODE_BRANCH, funct3="001"),
    "blt":  InstructionDef("blt",  FormatType.B, OPCODE_BRANCH, funct3="100"),
    # J-type
    "jal":  InstructionDef("jal",  FormatType.J, OPCODE_JAL),
    # Bonus
    "halt": InstructionDef("halt", FormatType.PSEUDO, OPCODE_SYSTEM),  # encodes as ecall 0x00000073
    "rst":  InstructionDef("rst",  FormatType.PSEUDO, OPCODE_RST),
}


def get_instruction(mnemonic: str) -> Optional[InstructionDef]:
    """Return instruction definition for mnemonic, or None if unknown."""
    return INSTRUCTIONS.get(mnemonic.lower().strip())


def is_valid_instruction(mnemonic: str) -> bool:
    """Check if mnemonic is a supported instruction."""
    return mnemonic.lower().strip() in INSTRUCTIONS


def get_opcode(mnemonic: str) -> str:
    """Return 7-bit opcode for instruction."""
    idef = get_instruction(mnemonic)
    if not idef:
        raise ValueError(f"Unknown instruction: {mnemonic}")
    return idef.opcode
