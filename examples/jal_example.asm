# JAL: jump and link to target
    addi  x1, x0, 0
    jal   x5, target
    addi  x1, x0, 99
target:
    addi  x2, x0, 42
    halt
