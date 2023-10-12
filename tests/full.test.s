; This is a sample assembly program that uses all instructions (excluding directives)

.global main

.text
main:
    ; Load Immediate
    li r0, #10
    li r1, #0x0A
    li r2, #0b1010   ; Use "0b" prefix for binary
    li r3, #42

    ; Load Data
    ld r0, [r1]
    ld r1, [r2]

    ; Store Data
    st r3, [r0]
    st r3, [r1]

    ; Add
    add r0, r1, r3
    add r3, r1, r2

    ; Subtract
    sub r0, r1, r2
    sub r3, r1, r2

    ; Jump
    jmp #0x08
    jmp label2

    ; Branch if Equal
    beq label1

    ; Branch if Not Equal
    bne label2

    ; Compare
    cmp r1, r2

    ; Logical AND
    and r1, r2
    and r1, r2

    ; Logical OR
    or r1, r2
    or r1, r2

    ; Logical XOR
    xor r1, r2
    xor r1, r2

    ; Shift Left
    shl r1, #2
    shl r1, #2

    ; Shift Right
    shr r1, #2
    shr r1, #2

    ; Push
    push {r0}
    push {r0,r1, r2, r3, lr}

    ; Pop
    pop {r1}
    pop {r0,r1, r2, r3, lr}

label1:
    ; Branch Target 1
    li r0, #1
    jmp #0x14

label2:
    ; Branch Target 2
    li r0, #2
    jmp #0x14

.data
; Data section (if needed)
