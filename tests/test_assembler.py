"""Tests for the RISC-V assembler."""

import pytest
from pathlib import Path
import sys

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.assembler.instruction_set import get_instruction, is_valid_instruction, FormatType
from src.assembler.registers import parse_register, is_valid_register
from src.assembler.parser import parse_line, parse_file, parse_offset_rs1
from src.assembler.encoder import encode_instruction, AssemblerError
from src.assembler import assemble


class TestRegisters:
    def test_parse_x0_x31(self):
        for i in range(32):
            assert parse_register(f"x{i}") == i

    def test_parse_abi_names(self):
        assert parse_register("zero") == 0
        assert parse_register("ra") == 1
        assert parse_register("sp") == 2
        assert parse_register("a0") == 10

    def test_invalid_register(self):
        with pytest.raises(ValueError, match="Invalid register"):
            parse_register("x32")
        with pytest.raises(ValueError, match="Invalid register"):
            parse_register("invalid")


class TestInstructionSet:
    def test_r_type(self):
        idef = get_instruction("add")
        assert idef.format_type == FormatType.R
        assert idef.funct3 == "000"
        assert idef.funct7 == "0000000"

    def test_b_type(self):
        idef = get_instruction("beq")
        assert idef.format_type == FormatType.B
        assert idef.funct3 == "000"

    def test_unknown_instruction(self):
        assert get_instruction("unknown") is None
        assert not is_valid_instruction("unknown")


class TestParser:
    def test_parse_add(self):
        pl = parse_line("add x1, x2, x3", 1)
        assert pl.mnemonic == "add"
        assert pl.operands == ["x1", "x2", "x3"]

    def test_parse_with_label(self):
        pl = parse_line("loop: addi x1, x0, 1", 1)
        assert pl.label == "loop"
        assert pl.mnemonic == "addi"
        assert pl.operands == ["x1", "x0", "1"]

    def test_parse_strip_comment(self):
        pl = parse_line("add x1, x2, x3  # comment", 1)
        assert pl.operands == ["x1", "x2", "x3"]

    def test_parse_offset_rs1(self):
        off, rs1 = parse_offset_rs1("0(x2)")
        assert off == 0 and rs1 == 2
        off, rs1 = parse_offset_rs1("-4(sp)")
        assert off == -4 and rs1 == 2

    def test_illegal_instruction(self):
        with pytest.raises(ValueError, match="illegal instruction"):
            parse_line("invalid x1, x2", 1)


class TestEncoder:
    def test_encode_add(self):
        from src.assembler.parser import ParsedLine
        pl = ParsedLine(1, "", mnemonic="add", operands=["x1", "x2", "x3"])
        label_to_pc = {}
        bin_str = encode_instruction(pl, 0, label_to_pc)
        assert len(bin_str) == 32
        assert bin_str[-7:] == "0110011"

    def test_encode_addi(self):
        from src.assembler.parser import ParsedLine
        pl = ParsedLine(1, "", mnemonic="addi", operands=["x1", "x0", "10"])
        bin_str = encode_instruction(pl, 0, {})
        assert len(bin_str) == 32
        # addi x1, x0, 10
        assert int(bin_str, 2) == 0x00A00093  # 10 in imm, x0=0, x1=1, opcode 0010011

    def test_encode_halt(self):
        from src.assembler.parser import ParsedLine
        pl = ParsedLine(1, "", mnemonic="halt", operands=[])
        bin_str = encode_instruction(pl, 0, {})
        assert bin_str == "000000000000" + "00000" + "000" + "00000" + "1110011"
        assert int(bin_str, 2) == 0x00000073


class TestAssembleIntegration:
    def test_assemble_requires_halt(self, tmp_path):
        (tmp_path / "no_halt.asm").write_text("addi x1, x0, 1\n")
        with pytest.raises(ValueError, match="Missing virtual halt"):
            assemble(str(tmp_path / "no_halt.asm"), str(tmp_path / "out.bin"))

    def test_assemble_halt_must_be_last(self, tmp_path):
        (tmp_path / "bad.asm").write_text("halt\naddi x1, x0, 1\n")
        with pytest.raises(ValueError, match="halt must be at the end"):
            assemble(str(tmp_path / "bad.asm"), str(tmp_path / "out.bin"))

    def test_assemble_success(self, tmp_path):
        (tmp_path / "p.asm").write_text("addi x1, x0, 1\naddi x2, x0, 2\nhalt\n")
        assemble(str(tmp_path / "p.asm"), str(tmp_path / "out.bin"))
        lines = (tmp_path / "out.bin").read_text().strip().splitlines()
        assert len(lines) == 3
        assert all(len(l) == 32 for l in lines)
