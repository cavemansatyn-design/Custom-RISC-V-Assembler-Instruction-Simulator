# Architecture

## Data flow

```
Assembly (.asm)  →  Parser  →  Encoder (with label resolution)  →  Binary (.bin)
                                                                        ↓
Trace (.txt)  ←  CPU (trace + memory dump)  ←  Memory + Decoder + Execution  ←  Binary
```

## Module roles

- **parser**: Tokenize and parse lines; validate instructions and operands; output `ParsedLine` with optional label, mnemonic, operands.
- **encoder**: Two-pass: build label→PC, then encode each instruction to 32-bit binary; check immediates and branch ranges.
- **memory**: Program (from 0), data segment, stack; word load/store with alignment checks.
- **decoder**: Split 32-bit instruction into opcode, rd, rs1, rs2, funct3, funct7, immediate (per format).
- **execution**: Given decoded instruction and current regs/PC/memory, compute next PC and any rd write; handle halt/rst.
- **cpu**: Load binary into memory, loop fetch–decode–execute, write trace line after each step, dump memory on halt.
