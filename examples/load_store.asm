# Load and store: store 100, then load back
    addi  x1, x0, 100
    addi  x2, x0, 0
    sw    x1, 0(x2)
    lw    x3, 0(x2)
    halt
