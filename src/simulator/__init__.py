"""
RISC-V RV32I Simulator.

Executes binary instructions, maintains registers and memory, and produces
execution trace (PC + x0-x31) and memory dump on halt.
"""

from .cpu import CPU, simulate
from .memory import Memory
from .decoder import decode, DecodedInstruction
from .execution import execute, ExecutionResult
