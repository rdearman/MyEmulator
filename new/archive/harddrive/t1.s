    li r0, #128
loop:
    shr r0, R0, #2
    cmp r0, r1
    bne loop
    jmp #0xFF

