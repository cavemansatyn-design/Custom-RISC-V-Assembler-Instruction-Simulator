# SLT: 7 < 15 -> 1, 15 < 7 -> 0
    addi  x1, x0, 7
    addi  x2, x0, 15
    slt   x3, x1, x2
    slt   x4, x2, x1
    halt
