	LI R0, 0x00
	LI R1, 0x10
	LI R2, 0x01
loop:
	SUB R1, R2
	CMP R1, R0
	BNE loop:
	BEQ exit

exit:
	JMP 0xFF
