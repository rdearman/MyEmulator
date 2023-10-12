.data
message1: .asciz "Hello World\n"
message2: .asciz "Goodbye Cruel World\n"

.text
    ld r0, =message1
    ld r1, =message2
    ld r2, [r1]
    add r3, r2, #0
    jmp printf
    jmp #0xff
