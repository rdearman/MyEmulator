    li r0, #2
    li r1, #4
    li r2, #6 
    li r3, #40

loop:
    add r0, r0, #1
    sub r3, r3, #1
    cmp r0, r3
    bne loop
;    jmp loop

    jmp #0xFF


