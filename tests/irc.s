.data
message1: .asciz "Hello World\n"
message2: .asciz "Goodbye Cruel World\n"

.text

    ld r0, =message1
    syscall 1
    ld r0, =message2
    syscall 1
    syscall 0


