#!/usr/bin/env python3
"""
RISC-V RV32I Assembler and Simulator — CLI entry point.

Usage:
  python main.py assemble <input.asm> <output.bin>
  python main.py simulate <input.bin> <trace.txt>
"""

import sys
import argparse
from pathlib import Path

# Allow running from repo root or from src
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.assembler import assemble as do_assemble
from src.assembler.encoder import AssemblerError
from src.simulator import simulate as do_simulate


def cmd_assemble(args: argparse.Namespace) -> int:
    """Run assembler: input.asm -> output.bin."""
    try:
        do_assemble(args.input, args.output)
        print(f"Assembled: {args.input} -> {args.output}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Assembler error: {e}", file=sys.stderr)
        return 1
    except AssemblerError as e:
        print(f"Assembler error: {e}", file=sys.stderr)
        return 1


def cmd_simulate(args: argparse.Namespace) -> int:
    """Run simulator: input.bin -> trace.txt."""
    try:
        do_simulate(args.input, args.output)
        print(f"Simulation complete: {args.output}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Simulator error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RISC-V RV32I Assembler and Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py assemble examples/program.asm examples/program.bin
  python main.py simulate examples/program.bin trace.txt
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_assemble = sub.add_parser("assemble", help="Assemble .asm to binary")
    p_assemble.add_argument("input", help="Input assembly file (.asm)")
    p_assemble.add_argument("output", help="Output binary file (.bin)")
    p_assemble.set_defaults(func=cmd_assemble)

    p_simulate = sub.add_parser("simulate", help="Simulate binary and write trace")
    p_simulate.add_argument("input", help="Input binary file (.bin)")
    p_simulate.add_argument("output", help="Output trace file (.txt)")
    p_simulate.set_defaults(func=cmd_simulate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
