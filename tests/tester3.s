

	LI R0, 0x10
	LI R1, 0x10
	LI R2, 0x01
	CMP R1, R0
	BEQ zero
	LI R0, 0xFF
	LI R1, 0xFF
	LI R2, 0xFF
	LI R4, 0xFF	

zero:
	JMP 0xFF
