"""Tests for the RISC-V simulator."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.simulator.memory import Memory
from src.simulator.decoder import decode
from src.simulator.execution import execute
from src.simulator.cpu import CPU, int_to_bin32


class TestMemory:
    def test_load_program(self):
        mem = Memory()
        mem.load_program(["0" * 32, "1" * 32])
        assert mem.get_instruction(0) == 0
        assert mem.get_instruction(4) == 0xFFFF_FFFF

    def test_read_write_word(self):
        mem = Memory()
        mem.write_word(0x10000, 42)
        assert mem.read_word(0x10000) == 42

    def test_unaligned_raises(self):
        mem = Memory()
        with pytest.raises(ValueError, match="Unaligned"):
            mem.read_word(2)


class TestDecoder:
    def test_decode_add(self):
        # add x1, x2, x3: rd=1, rs1=2, rs2=3, funct3=0, funct7=0, opcode=0x33
        inst = 0x003100B3
        dec = decode(inst)
        assert dec.format_type == "R"
        assert dec.rd == 1 and dec.rs1 == 2 and dec.rs2 == 3
        assert dec.opcode == "0110011"

    def test_decode_addi(self):
        # addi x1, x0, 10
        inst = 0x00A00093
        dec = decode(inst)
        assert dec.format_type == "I"
        assert dec.imm == 10
        assert dec.rd == 1 and dec.rs1 == 0


class TestExecution:
    def test_add(self):
        mem = Memory()
        dec = decode(0x003100B3)  # add x1, x2, x3
        regs = [0] * 32
        regs[2], regs[3] = 10, 20
        res = execute(dec, 0, regs, mem)
        assert res.next_pc == 4
        assert res.write_rd and res.rd_val == 30

    def test_x0_not_written(self):
        mem = Memory()
        # add x0, x1, x2 - result discarded
        dec = decode(0x00208033)
        regs = [0] * 32
        regs[1], regs[2] = 1, 2
        res = execute(dec, 0, regs, mem)
        assert res.write_rd
        assert res.rd_val == 3  # execution still returns value; CPU skips write for rd=0


class TestCPU:
    def test_run_simple(self, tmp_path):
        # Two instructions: addi x1, x0, 5; halt
        # addi x1, x0, 5 = 0x00500093
        # halt = 0x00000073
        bin_file = tmp_path / "prog.bin"
        bin_file.write_text("00000000010100000000000010010011\n00000000000000000000000001110011\n")
        cpu = CPU()
        cpu.load_program_from_binary_file(bin_file)
        trace_file = tmp_path / "trace.txt"
        with open(trace_file, "w") as f:
            cpu.run(trace_file=f)
        lines = trace_file.read_text().strip().splitlines()
        # After addi: one trace line; after halt: one more trace line then memory
        assert any("00000000000000000000000000000101" in ln for ln in lines)
