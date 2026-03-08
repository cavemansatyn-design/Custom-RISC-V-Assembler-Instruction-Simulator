# Example RISC-V RV32I program
# Computes a small computation and stores result, then halts.

    addi  x1, x0, 10      # x1 = 10
    addi  x2, x0, 20      # x2 = 20
    add   x3, x1, x2      # x3 = 30
    addi  x4, x0, 0       # x4 = 0 (will use as base for store)
    sw    x3, 0(x4)       # store 30 at address 0 (data region in simulator)
    lw    x5, 0(x4)       # x5 = 30
    slt   x6, x1, x2      # x6 = 1 (10 < 20)
    or    x7, x1, x2     # x7 = 30
    and   x8, x1, x2     # x8 = 0
    addi  x11, x0, 1     # x11 = 1 (shift amount)
    srl   x9, x2, x11    # x9 = 10 (20 >> 1)
    sub   x10, x3, x1    # x10 = 20
    halt
