    li r0, #0x0055
    li r2, #0
    li r3, #12 
loop:
    ld r1, [r0]
    add r0, r0, #1
    add r2, r2, #1
    cmp r2, r3
    bne loop 
    jmp #0xFF


