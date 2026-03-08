"""
RISC-V RV32I instruction encoder.

Converts parsed assembly (with resolved labels) into 32-bit binary instructions.
Handles immediates, offsets, and PC-relative branch/jal offsets.
"""

from typing import Optional
from .instruction_set import (
    get_instruction,
    FormatType,
    INSTRUCTIONS,
    OPCODE_SYSTEM,
    OPCODE_RST,
)
from .registers import parse_register, reg_to_bin


def imm_to_bin(value: int, bits: int, signed: bool = True) -> str:
    """
    Encode integer immediate into `bits`-bit binary string (no 0b).
    If signed and value is negative, two's complement.
    """
    mask = (1 << bits) - 1
    if signed and value < 0:
        value = (1 << bits) + value
    return format(value & mask, f"0{bits}b")


def encode_r(rd: int, rs1: int, rs2: int, funct3: str, funct7: str, opcode: str) -> str:
    """Encode R-type: funct7 | rs2 | rs1 | funct3 | rd | opcode (32 bits)."""
    return (
        funct7
        + reg_to_bin(rs2)
        + reg_to_bin(rs1)
        + funct3
        + reg_to_bin(rd)
        + opcode
    )


def encode_i(rd: int, rs1: int, imm: int, funct3: str, opcode: str) -> str:
    """Encode I-type: imm[11:0] | rs1 | funct3 | rd | opcode (32 bits)."""
    return (
        imm_to_bin(imm, 12)
        + reg_to_bin(rs1)
        + funct3
        + reg_to_bin(rd)
        + opcode
    )


def encode_s(rs1: int, rs2: int, imm: int, funct3: str, opcode: str) -> str:
    """Encode S-type: imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode (32 bits)."""
    imm12 = imm_to_bin(imm, 12)
    return (
        imm12[:7]
        + reg_to_bin(rs2)
        + reg_to_bin(rs1)
        + funct3
        + imm12[7:]
        + opcode
    )


def encode_b(rs1: int, rs2: int, imm: int, funct3: str, opcode: str) -> str:
    """Encode B-type. imm must be multiple of 2 (branch target)."""
    if imm & 1:
        raise ValueError("Branch offset must be aligned to 2 bytes")
    # Sign-extend to 13 bits for range check, then take bits for encoding
    if imm >= 0:
        imm13 = imm & 0x1FFF
    else:
        imm13 = (1 << 13) + imm
    # B-type layout: imm[12] | imm[10:5] | rs2 | rs1 | funct3 | imm[4:1] | imm[11] | opcode
    b12 = (imm13 >> 12) & 1
    b11 = (imm13 >> 11) & 1
    b10_5 = (imm13 >> 5) & 0x3F
    b4_1 = (imm13 >> 1) & 0xF
    return (
        str(b12) + imm_to_bin(b10_5, 6) + reg_to_bin(rs2) + reg_to_bin(rs1)
        + funct3 + imm_to_bin(b4_1, 4) + str(b11) + opcode
    )


def encode_j(rd: int, imm: int, opcode: str) -> str:
    """Encode J-type. imm must be multiple of 2 (jal target)."""
    if imm & 1:
        raise ValueError("JAL offset must be aligned to 2 bytes")
    if imm >= 0:
        imm20 = (imm >> 1) & 0xFFFFF
    else:
        imm20 = ((1 << 20) + (imm >> 1)) & 0xFFFFF
    # J-type: imm[20|10:1|11|19:12] | rd | opcode (20 + 5 + 7 = 32)
    j20 = (imm20 >> 19) & 1
    j10_1 = imm20 & 0x3FF
    j11 = (imm20 >> 10) & 1
    j19_12 = (imm20 >> 11) & 0xFF
    return (
        str(j20) + imm_to_bin(j10_1, 10) + str(j11) + imm_to_bin(j19_12, 8)
        + reg_to_bin(rd) + opcode
    )


class AssemblerError(Exception):
    """Raised when assembly cannot be encoded (e.g. immediate out of range)."""
    pass


def resolve_labels(
    parsed_lines: list,
    label_to_pc: dict[str, int],
) -> list[tuple[int, object]]:
    """
    First pass: build list of (pc_word_index, parsed_line) for instructions only.
    Labels already recorded in label_to_pc; we only emit instructions and assign PC.
    """
    pc = 0
    out = []
    for pl in parsed_lines:
        if pl.label is not None and pl.mnemonic is None:
            continue
        if pl.mnemonic is None:
            continue
        out.append((pc, pl))
        pc += 4
    return out


def encode_instruction(
    parsed_line,
    pc: int,
    label_to_pc: dict[str, int],
) -> str:
    """
    Encode a single parsed instruction to 32-bit binary string.

    Args:
        parsed_line: ParsedLine with mnemonic and operands
        pc: PC (byte address) of this instruction
        label_to_pc: map from label name to byte address

    Returns:
        32-character binary string (no 0b prefix)

    Raises:
        AssemblerError: on immediate out of range or invalid operand
    """
    idef = get_instruction(parsed_line.mnemonic)
    opcode = idef.opcode
    operands = parsed_line.operands

    if idef.format_type == FormatType.PSEUDO:
        if parsed_line.mnemonic == "halt":
            # Encode as ecall: 0x00000073
            return "000000000000" + "00000" + "000" + "00000" + OPCODE_SYSTEM
        if parsed_line.mnemonic == "rst":
            # Custom encoding for simulator
            return "0000000" + "00000" + "00000" + "000" + "00000" + OPCODE_RST

    if idef.format_type == FormatType.R:
        rd = parse_register(operands[0])
        rs1 = parse_register(operands[1])
        rs2 = parse_register(operands[2])
        return encode_r(
            rd, rs1, rs2,
            idef.funct3, idef.funct7, opcode,
        )

    if idef.format_type == FormatType.I:
        if parsed_line.mnemonic == "lw":
            rd = parse_register(operands[0])
            from .parser import parse_offset_rs1
            offset, rs1 = parse_offset_rs1(operands[1])
            if not -(1 << 11) <= offset < (1 << 11):
                raise AssemblerError(
                    f"Line {parsed_line.line_no}: lw offset {offset} out of range [-2048, 2047]"
                )
            return encode_i(rd, rs1, offset, idef.funct3, opcode)
        if parsed_line.mnemonic == "addi":
            rd = parse_register(operands[0])
            rs1 = parse_register(operands[1])
            imm = parse_imm_operand(operands[2], parsed_line.line_no, 12)
            return encode_i(rd, rs1, imm, idef.funct3, opcode)
        if parsed_line.mnemonic == "jalr":
            rd = parse_register(operands[0])
            if len(operands) == 2:
                rs1 = parse_register(operands[1])
                imm = 0
            else:
                rs1 = parse_register(operands[1])
                imm = parse_imm_operand(operands[2], parsed_line.line_no, 12)
            return encode_i(rd, rs1, imm, idef.funct3, opcode)

    if idef.format_type == FormatType.S:
        from .parser import parse_offset_rs1
        rs2 = parse_register(operands[0])
        offset, rs1 = parse_offset_rs1(operands[1])
        if not -(1 << 11) <= offset < (1 << 11):
            raise AssemblerError(
                f"Line {parsed_line.line_no}: sw offset {offset} out of range [-2048, 2047]"
            )
        return encode_s(rs1, rs2, offset, idef.funct3, opcode)

    if idef.format_type == FormatType.B:
        rs1 = parse_register(operands[0])
        rs2 = parse_register(operands[1])
        target = resolve_label_operand(operands[2], label_to_pc, parsed_line.line_no)
        offset = target - pc
        if not -(1 << 12) <= offset < (1 << 12):
            raise AssemblerError(
                f"Line {parsed_line.line_no}: branch offset {offset} out of range [-4096, 4095]"
            )
        return encode_b(rs1, rs2, offset, idef.funct3, opcode)

    if idef.format_type == FormatType.J:
        rd = parse_register(operands[0])
        target = resolve_label_operand(operands[1], label_to_pc, parsed_line.line_no)
        offset = target - pc
        if not -(1 << 20) <= offset < (1 << 20):
            raise AssemblerError(
                f"Line {parsed_line.line_no}: jal offset {offset} out of range"
            )
        return encode_j(rd, offset, opcode)

    raise AssemblerError(f"Line {parsed_line.line_no}: unhandled format {idef.format_type}")


def parse_imm_operand(s: str, line_no: int, bits: int) -> int:
    """Parse immediate operand and check range for given bit width (signed)."""
    s = s.strip()
    try:
        if s.startswith("0x") or s.startswith("0X"):
            val = int(s, 16)
        else:
            val = int(s, 10)
    except ValueError:
        raise AssemblerError(f"Line {line_no}: invalid immediate '{s}'")
    lo = -(1 << (bits - 1))
    hi = (1 << (bits - 1)) - 1
    if not lo <= val <= hi:
        raise AssemblerError(
            f"Line {line_no}: immediate {val} out of range [{lo}, {hi}] for {bits}-bit"
        )
    return val


def resolve_label_operand(s: str, label_to_pc: dict[str, int], line_no: int) -> int:
    """Resolve label or numeric address to byte address."""
    s = s.strip()
    if s in label_to_pc:
        return label_to_pc[s]
    try:
        if s.startswith("0x") or s.startswith("0X"):
            return int(s, 16)
        return int(s, 10)
    except ValueError:
        raise AssemblerError(f"Line {line_no}: undefined label '{s}'")
