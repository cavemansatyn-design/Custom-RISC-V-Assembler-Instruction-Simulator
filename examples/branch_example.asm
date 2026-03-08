# Branch and jump example
    addi  x1, x0, 1
    addi  x2, x0, 2
    beq   x1, x2, skip     # not taken
    addi  x3, x0, 100
skip:
    bne   x1, x2, there    # taken
    addi  x4, x0, 0
there:
    addi  x4, x0, 42
    jal   x5, target       # jump and link
    addi  x6, x0, 1
target:
    addi  x7, x0, 7
    halt
