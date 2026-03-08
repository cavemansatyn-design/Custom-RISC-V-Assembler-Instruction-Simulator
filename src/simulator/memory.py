"""
RISC-V simulator memory model.

Provides separate regions: program memory (code), stack, and data memory.
All addresses are byte addresses; loads/stores are word-aligned (4 bytes).
"""

from typing import Optional


# Default layout (byte addresses)
# Program: 0x00000000 and up (code)
# Data:    0x00010000 - 0x0001007F (e.g. 32 words)
# Stack:   grows down from 0x00020000
PROGRAM_BASE = 0x0000_0000
DATA_BASE = 0x0001_0000
DATA_SIZE = 128  # bytes
STACK_TOP = 0x0002_0000
STACK_SIZE = 4096


class Memory:
    """
    Unified memory with distinct regions: program, data, stack.
    Words are 32-bit; addresses must be 4-byte aligned for lw/sw.
    """

    def __init__(
        self,
        program_base: int = PROGRAM_BASE,
        data_base: int = DATA_BASE,
        data_size: int = DATA_SIZE,
        stack_top: int = STACK_TOP,
        stack_size: int = STACK_SIZE,
    ) -> None:
        self.program_base = program_base
        self.data_base = data_base
        self.data_size = data_size
        self.stack_top = stack_top
        self.stack_size = stack_size
        self.stack_bottom = stack_top - stack_size

        # program: address -> 32-bit value (as int)
        self._program: dict[int, int] = {}
        # data: address -> 32-bit value
        self._data: dict[int, int] = {}
        # stack: address -> 32-bit value
        self._stack: dict[int, int] = {}

    def _region(self, addr: int) -> str:
        """Return 'program', 'data', or 'stack' for address."""
        if self.program_base <= addr < self.data_base:
            return "program"
        if self.data_base <= addr < self.data_base + self.data_size:
            return "data"
        if self.stack_bottom <= addr < self.stack_top:
            return "stack"
        return "unknown"

    def _get_region_dict(self, addr: int) -> Optional[dict[int, int]]:
        """Return the dict for the region containing addr, or None."""
        r = self._region(addr)
        if r == "program":
            return self._program
        if r == "data":
            return self._data
        if r == "stack":
            return self._stack
        return None

    def load_program(self, instructions: list[str]) -> None:
        """
        Load binary instructions (list of 32-bit binary strings) into program memory.
        Address 0 gets first instruction, 4 gets second, etc.
        """
        self._program.clear()
        for i, inst in enumerate(instructions):
            if not inst or len(inst) != 32:
                continue
            addr = self.program_base + i * 4
            self._program[addr] = int(inst, 2)

    def read_word(self, addr: int) -> int:
        """
        Read 32-bit word at aligned address addr.
        Returns 0 for uninitialized locations.
        """
        if addr & 3:
            raise ValueError(f"Unaligned read at 0x{addr:08X}")
        d = self._get_region_dict(addr)
        if d is None:
            raise ValueError(f"Address 0x{addr:08X} out of range")
        return d.get(addr, 0)

    def write_word(self, addr: int, value: int) -> None:
        """Write 32-bit word at aligned address. Value is masked to 32 bits."""
        if addr & 3:
            raise ValueError(f"Unaligned write at 0x{addr:08X}")
        d = self._get_region_dict(addr)
        if d is None:
            raise ValueError(f"Address 0x{addr:08X} out of range")
        d[addr] = value & 0xFFFF_FFFF

    def get_instruction(self, pc: int) -> Optional[int]:
        """Get instruction word at PC (program region only)."""
        if pc & 3:
            raise ValueError(f"Unaligned PC 0x{pc:08X}")
        return self._program.get(pc)

    def all_memory_sorted(self) -> list[tuple[int, int]]:
        """
        Return all (address, value) pairs from all regions, sorted by address.
        Values are 32-bit integers.
        """
        combined: dict[int, int] = {}
        for d in (self._program, self._data, self._stack):
            for addr, val in d.items():
                combined[addr] = val
        return sorted(combined.items())
