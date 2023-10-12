; Test 1: LI with Decimal Immediate Value
LI #0
; Test 2: LI with Binary Immediate Value
LI #0b0101
; Test 3: LI with Hexadecimal Immediate Value
LI #0x1234
; Test 1: LI with Decimal Immediate Value
LI #0

; Test 2: LI with Binary Immediate Value
LI #0b0101

; Test 3: LI with Hexadecimal Immediate Value
LI #0x1234
; Test 1: LD with Register Operand
LD r0, [r1]

; Test 1: ST with Register Operand
ST r1, [r3]

; Test 1: ADD with Register Operands
ADD r0, r1, r2
; Test 2: ADD with Immediate Value Operand
ADD r3, r1, #0x10


; Test 1: SUB with Register Operands
SUB r0, r1, r2

; Test 2: SUB with Immediate Value Operand
SUB r3, r1, #0x10



; Test 1: JMP with Label Operand
JMP my_label

; Test 2: JMP with Immediate Value Operand
JMP #0x1234
; Test 1: BEQ with Label Operand
BEQ my_label

; Test 1: BNE with Label Operand
BNE my_label

; Test 1: CMP with Register Operands
CMP r0, r1, r2
; Test 1: AND with Register Operands
AND r0, r1, r2

; Test 2: AND with Immediate Value Operand
AND r3, r1, #0b1100

; Test 1: OR with Register Operands
OR r0, r1, r2

; Test 2: OR with Immediate Value Operand
OR r3, r1, #0xFF

; Test 1: XOR with Register Operands
XOR r0, r1, r2

; Test 2: XOR with Immediate Value Operand
XOR r3, r1, #0x55
; Test 1: SHL with Register Operands
SHL r0, r1, r2

; Test 2: SHL with Immediate Value Operand
SHL r3, r1, #0x03
; Test 1: SHR with Register Operands
SHR r0, r1, r2

; Test 2: SHR with Immediate Value Operand
SHR r3, r1, #0x02
; Test 1: PUSH with Register Operand
PUSH r0

; Test 2: PUSH with Immediate Value Operand
PUSH #0xAA
; Test 1: POP with Register Operand
POP r0

; Test 2: POP with Immediate Value Operand
POP #0x55

; Test 1: PUSH with 1 Register Operand
PUSH r0

; Test 2: PUSH with 2 Register Operands
PUSH r1, r2

; Test 3: PUSH with 3 Register Operands
PUSH r0, r1, r2

; Test 4: PUSH with 4 Register Operands
PUSH r1, r2, r3, r4

; Test 1: POP with 1 Register Operand
POP r0

; Test 2: POP with 2 Register Operands
POP r1, r2

; Test 3: POP with 3 Register Operands
POP r0, r1, r2

; Test 4: POP with 4 Register Operands
POP r1, r2, r3, r4



=== Error

; Test 1: Empty PUSH (No Operands)
PUSH

; Test 2: Empty POP (No Operands)
POP
; Test 1: Invalid Register in PUSH
PUSH r0, r5  # r5 is not a valid register

; Test 2: Invalid Register in POP
POP r1, rA  # rA is not a valid register
; Test 1: Invalid Register in PUSH
PUSH r0, r5  # r5 is not a valid register

; Test 2: Invalid Register in PUSH
PUSH r3, rA  # rA is not a valid register
; Test 1: Invalid Register in POP
POP r1, rA  # rA is not a valid register

; Test 2: Invalid Register in POP
POP r2, r6  # r6 is not a valid register
; Test 1: Invalid Register in POP
POP r1, rA  # rA is not a valid register

; Test 2: Invalid Register in POP
POP r2, r6  # r6 is not a valid register
; Test 1: Empty PUSH (No Operands)
PUSH

; Test 2: Empty POP (No Operands)
POP

; Test 1: Invalid Register Operand
LD r0, rA  # rA is not a valid register

; Test 2: Invalid Immediate Operand
LD r1, #xyz  # Invalid immediate format

; Test 3: Missing Operand
LD r2

; Test 4: Incorrect Number of Operands
LD r3, r4, r5  # Too many operands
; Test 1: Invalid Register Operand
LI r0, rA  # rA is not a valid register

; Test 2: Invalid Immediate Operand
LI r1, #xyz  # Invalid immediate format

; Test 3: Missing Operand
LI r2

; Test 4: Incorrect Number of Operands
LI r3, r4, r5  # Too many operands
; Test 1: Invalid Register Operand
ST r0, rA  # rA is not a valid register

; Test 2: Invalid Immediate Operand
ST r1, #xyz  # Invalid immediate format

; Test 3: Missing Operand
ST r2

; Test 4: Incorrect Number of Operands
ST r3, r4, r5  # Too many operands
; Test 1: Invalid Register Operands
ADD r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
ADD r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
ADD r2

; Test 4: Incorrect Number of Operands
ADD r3, r4  # Too few operands
; Test 1: Invalid Register Operands
SUB r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
SUB r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
SUB r2

; Test 4: Incorrect Number of Operands
SUB r3, r4  # Too few operands
; Test 1: Invalid Immediate Operand
JMP #xyz  # Invalid immediate format

; Test 2: Missing Operand
JMP

; Test 3: Incorrect Number of Operands
JMP r0, r1  # Too many operands
; Test 1: Invalid Immediate Operand
BEQ #xyz  # Invalid immediate format

; Test 2: Missing Operand
BEQ

; Test 3: Incorrect Number of Operands
BEQ r0, r1  # Too many operands
; Test 1: Invalid Immediate Operand
BNE #xyz  # Invalid immediate format

; Test 2: Missing Operand
BNE

; Test 3: Incorrect Number of Operands
BNE r0, r1  # Too many operands
; Test 1: Invalid Register Operands
CMP r0, rA  # rA is not a valid register

; Test 2: Invalid Immediate Operand
CMP r1, #xyz  # Invalid immediate format

; Test 3: Missing Operand
CMP r2

; Test 4: Incorrect Number of Operands
CMP r3, r4, r5  # Too many operands
; Test 1: Invalid Register Operands
AND r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
AND r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
AND r2

; Test 4: Incorrect Number of Operands
AND r3, r4  # Too few operands
; Test 1: Invalid Register Operands
OR r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
OR r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
OR r2

; Test 4: Incorrect Number of Operands
OR r3, r4  # Too few operands
; Test 1: Invalid Register Operands
XOR r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
XOR r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
XOR r2

; Test 4: Incorrect Number of Operands
XOR r3, r4  # Too few operands
; Test 1: Invalid Register Operands
SHL r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
SHL r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
SHL r2

; Test 4: Incorrect Number of Operands
SHL r3, r4  # Too few operands
; Test 1: Invalid Register Operands
SHR r0, rA, r1  # rA is not a valid register

; Test 2: Invalid Immediate Operand
SHR r1, r2, #xyz  # Invalid immediate format

; Test 3: Missing Operand
SHR r2

; Test 4: Incorrect Number of Operands
SHR r3, r4  # Too few operands
; Test 1: Invalid Register Operand
PUSH r0, rA  # rA is not a valid register

; Test 2: Invalid Immediate Operand
PUSH r1, #xyz  # Invalid immediate format

; Test 3: Missing Operand
PUSH r2

; Test 4: Incorrect Number of Operands
PUSH r3, r4, r5  # Too many operands
; Test 1: Invalid Register Operand
POP r0, rA  # rA is not a valid register

; Test 2: Invalid Immediate Operand
POP r1, #xyz  # Invalid immediate format

; Test 3: Missing Operand
POP r2

; Test 4: Incorrect Number of Operands
POP


