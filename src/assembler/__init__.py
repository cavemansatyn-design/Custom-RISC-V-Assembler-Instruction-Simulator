"""
RISC-V RV32I Assembler.

Converts assembly source (.asm) to 32-bit binary instructions with full
support for labels, immediates, and PC-relative branches.
"""

from .parser import parse_file, parse_line, ParsedLine
from .encoder import encode_instruction, AssemblerError, resolve_labels
from .instruction_set import INSTRUCTIONS, get_instruction, is_valid_instruction
from .registers import parse_register, is_valid_register


def assemble(source_path: str, output_path: str) -> None:
    """
    Assemble an .asm file to a binary instruction file.

    Each line of output is one 32-bit binary instruction (32 chars, no 0b).

    Raises:
        ValueError: parse errors (illegal instruction, invalid register, invalid syntax).
        AssemblerError: encode errors (immediate out of range, undefined label).
    """
    from pathlib import Path
    from .parser import parse_file
    from .encoder import encode_instruction, AssemblerError

    path = Path(source_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {source_path}")

    parsed = parse_file(path)

    # First pass: build label -> PC (byte address) for instruction lines only
    label_to_pc: dict[str, int] = {}
    pc = 0
    instruction_lines: list[tuple[int, ParsedLine]] = []
    for pl in parsed:
        if pl.label is not None:
            label_to_pc[pl.label] = pc
        if pl.mnemonic is not None:
            instruction_lines.append((pc, pl))
            pc += 4

    # Check for halt
    if not instruction_lines:
        raise ValueError("No instructions in file")
    mnemonics = [pl.mnemonic for _, pl in instruction_lines]
    if "halt" not in mnemonics:
        raise ValueError("Missing virtual halt instruction")
    halt_index = mnemonics.index("halt")
    if halt_index != len(mnemonics) - 1:
        raise ValueError("Virtual halt must be at the end of the program")

    # Second pass: encode
    binary_lines: list[str] = []
    for pc_val, pl in instruction_lines:
        try:
            bin_inst = encode_instruction(pl, pc_val, label_to_pc)
            binary_lines.append(bin_inst)
        except AssemblerError as e:
            raise e
        except ValueError as e:
            raise AssemblerError(f"Line {pl.line_no}: {e}") from e

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(binary_lines) + "\n", encoding="utf-8")
