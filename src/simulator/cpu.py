"""
RISC-V CPU simulator.

Orchestrates program counter, registers x0-x31, and memory. Runs until halt;
outputs trace (PC and registers as 32-bit binary) after each instruction and
memory dump after halt.
"""

from pathlib import Path
from typing import TextIO, Optional

from .memory import Memory
from .decoder import decode, DecodedInstruction
from .execution import execute, ExecutionResult


def int_to_bin32(val: int) -> str:
    """Format integer as 32-bit binary string (no 0b)."""
    return format(val & 0xFFFF_FFFF, "032b")


class CPU:
    """
    Single-cycle CPU: 32 registers, PC, and memory.
    x0 is hardwired to zero.
    """

    def __init__(self, memory: Optional[Memory] = None) -> None:
        self.memory = memory or Memory()
        self.regs = [0] * 32
        self.pc = 0

    def load_program_from_binary_file(self, path: Path) -> None:
        """Load instructions from file (one 32-bit binary line per instruction)."""
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        instructions = [ln.strip() for ln in lines if ln.strip() and len(ln.strip()) == 32]
        self.memory.load_program(instructions)
        self.pc = self.memory.program_base
        self.regs = [0] * 32

    def write_register(self, reg_num: int, value: int) -> None:
        """Write register; x0 is never updated."""
        if reg_num != 0:
            self.regs[reg_num] = value & 0xFFFF_FFFF

    def run(
        self,
        trace_file: Optional[TextIO] = None,
        max_cycles: int = 1_000_000,
    ) -> None:
        """
        Execute until halt (or max_cycles). After each instruction, output
        one line: PC x0 x1 ... x31 (all 32-bit binary). After halt, output
        memory contents.
        """
        cycles = 0
        while cycles < max_cycles:
            inst_word = self.memory.get_instruction(self.pc)
            if inst_word is None:
                raise RuntimeError(f"PC 0x{self.pc:08X}: no instruction (out of program?)")

            dec = decode(inst_word)
            res = execute(dec, self.pc, self.regs, self.memory)

            if res.reset:
                self.pc = 0
                self.regs = [0] * 32
                if trace_file:
                    self._write_trace_line(trace_file)
                cycles += 1
                continue

            if res.write_rd and dec.rd != 0:
                self.write_register(dec.rd, res.rd_val)

            self.pc = res.next_pc
            if trace_file:
                self._write_trace_line(trace_file)

            if res.halt:
                if trace_file:
                    self._write_memory(trace_file)
                return

            cycles += 1

        raise RuntimeError(f"Max cycles ({max_cycles}) exceeded without halt")

    def _write_trace_line(self, f: TextIO) -> None:
        """Output one line: PC x0 x1 ... x31 (32-bit binary each)."""
        parts = [int_to_bin32(self.pc)]
        for i in range(32):
            parts.append(int_to_bin32(self.regs[i]))
        f.write(" ".join(parts) + "\n")

    def _write_memory(self, f: TextIO) -> None:
        """Output all memory contents: address:value (binary or hex). Spec says 'memory contents'."""
        for addr, val in self.memory.all_memory_sorted():
            f.write(f"0x{addr:08X}:{int_to_bin32(val)}\n")


def simulate(binary_path: str, trace_path: str) -> None:
    """
    Load binary from binary_path, run simulation, write trace to trace_path.
    """
    path = Path(binary_path)
    if not path.exists():
        raise FileNotFoundError(f"Binary file not found: {binary_path}")

    mem = Memory()
    cpu = CPU(memory=mem)
    cpu.load_program_from_binary_file(path)

    Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "w", encoding="utf-8") as tf:
        cpu.run(trace_file=tf)
