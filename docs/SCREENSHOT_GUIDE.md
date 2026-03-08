# Screenshot Guide for GitHub README

Use this guide to capture screenshots that showcase your RISC-V Assembler and Simulator.

---

## Prerequisites

1. Open **PowerShell** or **Command Prompt**
2. Navigate to project root: `cd "d:\Downloads\Group_010 (1)"`
3. Ensure Python is installed: `python --version`

---

## 10 Example Inputs & How to Run Them

### Example 1: Basic Arithmetic (program.asm)
**What it does:** Adds 10+20, stores result, tests ADD/ADDI/SW/LW

```powershell
python main.py assemble examples/program.asm examples/program.bin
python main.py simulate examples/program.bin trace.txt
```

### Example 2: Branch and Jump (branch_example.asm)
**What it does:** Tests BEQ, BNE, JAL with labels

```powershell
python main.py assemble examples/branch_example.asm examples/branch_example.bin
python main.py simulate examples/branch_example.bin trace_branch.txt
```

### Example 3: Simple Addition Only
Create `examples/simple_add.asm`:
```asm
    addi  x1, x0, 5
    addi  x2, x0, 3
    add   x3, x1, x2
    halt
```

```powershell
python main.py assemble examples/simple_add.asm examples/simple_add.bin
python main.py simulate examples/simple_add.bin trace_simple.txt
```

### Example 4: Load and Store
Create `examples/load_store.asm`:
```asm
    addi  x1, x0, 100
    addi  x2, x0, 0
    sw    x1, 0(x2)
    lw    x3, 0(x2)
    halt
```

```powershell
python main.py assemble examples/load_store.asm examples/load_store.bin
python main.py simulate examples/load_store.bin trace_load.txt
```

### Example 5: SLT (Set Less Than)
Create `examples/slt_example.asm`:
```asm
    addi  x1, x0, 7
    addi  x2, x0, 15
    slt   x3, x1, x2
    slt   x4, x2, x1
    halt
```

```powershell
python main.py assemble examples/slt_example.asm examples/slt_example.bin
python main.py simulate examples/slt_example.bin trace_slt.txt
```

### Example 6: OR and AND
Create `examples/logic.asm`:
```asm
    addi  x1, x0, 12
    addi  x2, x0, 5
    or    x3, x1, x2
    and   x4, x1, x2
    halt
```

```powershell
python main.py assemble examples/logic.asm examples/logic.bin
python main.py simulate examples/logic.bin trace_logic.txt
```

### Example 7: SRL (Shift Right Logical)
Create `examples/shift.asm`:
```asm
    addi  x1, x0, 16
    addi  x2, x0, 2
    srl   x3, x1, x2
    halt
```

```powershell
python main.py assemble examples/shift.asm examples/shift.bin
python main.py simulate examples/shift.bin trace_shift.txt
```

### Example 8: SUB (Subtraction)
Create `examples/sub_example.asm`:
```asm
    addi  x1, x0, 50
    addi  x2, x0, 23
    sub   x3, x1, x2
    halt
```

```powershell
python main.py assemble examples/sub_example.asm examples/sub_example.bin
python main.py simulate examples/sub_example.bin trace_sub.txt
```

### Example 9: JAL (Jump and Link)
Create `examples/jal_example.asm`:
```asm
    addi  x1, x0, 0
    jal   x5, target
    addi  x1, x0, 99
target:
    addi  x2, x0, 42
    halt
```

```powershell
python main.py assemble examples/jal_example.asm examples/jal_example.bin
python main.py simulate examples/jal_example.bin trace_jal.txt
```

### Example 10: Full Featured (All Instructions)
Use `examples/program.asm` — it exercises ADD, SUB, ADDI, LW, SW, SLT, OR, AND, SRL.

```powershell
python main.py assemble examples/program.asm examples/program.bin
python main.py simulate examples/program.bin trace.txt
```

---

## What to Screenshot (Step by Step)

### Screenshot 1: Project Structure
- **What:** File explorer showing project folders (`src/`, `examples/`, `tests/`, etc.)
- **How:** Open File Explorer → navigate to project → capture window
- **Save as:** `docs/screenshots/01-project-structure.png`

### Screenshot 2: Assemble Command Success
- **What:** Terminal showing successful assemble
- **How:** Run `python main.py assemble examples/program.asm examples/program.bin`
- **Capture:** The full command + "Assembled: examples/program.asm -> examples/program.bin"
- **Save as:** `docs/screenshots/02-assemble-success.png`

### Screenshot 3: Simulate Command Success
- **What:** Terminal showing successful simulation
- **How:** Run `python main.py simulate examples/program.bin trace.txt`
- **Capture:** The full command + "Simulation complete: trace.txt"
- **Save as:** `docs/screenshots/03-simulate-success.png`

### Screenshot 4: Full Workflow (Assemble + Simulate)
- **What:** Both commands run together in one terminal
- **How:** Run both commands, then capture the full output
- **Save as:** `docs/screenshots/04-full-workflow.png`

### Screenshot 5: Assembly Source Code
- **What:** `examples/program.asm` open in editor
- **How:** Open the file in VS Code/Cursor, capture the code view
- **Save as:** `docs/screenshots/05-assembly-source.png`

### Screenshot 6: Binary Output
- **What:** First few lines of `examples/program.bin` (32-bit binary)
- **How:** Open trace.txt or program.bin, or run `Get-Content examples/program.bin | Select-Object -First 5`
- **Save as:** `docs/screenshots/06-binary-output.png`

### Screenshot 7: Trace Output (Registers)
- **What:** First few lines of `trace.txt` showing PC and register values
- **How:** Open trace.txt or run `Get-Content trace.txt | Select-Object -First 5`
- **Save as:** `docs/screenshots/07-trace-registers.png`

### Screenshot 8: Memory Dump
- **What:** Memory dump section at end of trace.txt
- **How:** Scroll to bottom of trace.txt, capture the address:value lines
- **Save as:** `docs/screenshots/08-memory-dump.png`

### Screenshot 9: Tests Passing
- **What:** All 25 tests passing
- **How:** Run `pytest tests/ -v` and capture the output
- **Save as:** `docs/screenshots/09-tests-passing.png`

### Screenshot 10: Help / Usage
- **What:** `python main.py --help` or `python main.py assemble --help`
- **How:** Run the help command, capture the usage info
- **Save as:** `docs/screenshots/10-help-usage.png`

---

## Quick Screenshot Checklist

| # | Screenshot | Command/Action |
|---|------------|----------------|
| 1 | Project structure | File Explorer |
| 2 | Assemble success | `python main.py assemble examples/program.asm examples/program.bin` |
| 3 | Simulate success | `python main.py simulate examples/program.bin trace.txt` |
| 4 | Full workflow | Both commands in one terminal |
| 5 | Assembly source | Open `examples/program.asm` |
| 6 | Binary output | First lines of `program.bin` |
| 7 | Trace (registers) | First lines of `trace.txt` |
| 8 | Memory dump | Last lines of `trace.txt` |
| 9 | Tests passing | `pytest tests/ -v` |
| 10 | Help/usage | `python main.py --help` |

---

## Taking Screenshots on Windows

- **Full screen:** `Win + PrtScn` (saves to Pictures/Screenshots)
- **Current window:** `Alt + PrtScn` (copies to clipboard)
- **Snipping Tool:** `Win + Shift + S` (select region)
- **PowerToys:** If installed, `Win + Shift + S` for better cropping

---

## Recommended for README

For a clean GitHub README, include at minimum:
1. **Screenshot 4** — Full workflow (shows it works end-to-end)
2. **Screenshot 9** — Tests passing (shows quality)
3. **Screenshot 5** — Assembly source (shows what users write)
