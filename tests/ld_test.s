; A test for memory storing and loading.

    LI r0, #0x55
    LI r1, #0x66
    LI r2, #1
    LI r3, #2
    ST r2, [r0]
    ST r3, [r1]
    ADD r2, r2, r3
    LD r2, [r0]
    LD r3, [r1]
    CMP r2, r3
    BNE halt

halt:
    JMP #0xFF
