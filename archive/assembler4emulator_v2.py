#!/usr/bin/python
#!/usr/bin/env python

import os
import traceback
import sys
import logging


class Assembler:
    def __init__(self):
        # Define the instruction set with opcode mappings
        self.instruction_set = {
            'ld': '0000',  # Load Data
            'li': '0001',  # Load Immediate
            'st': '0010',  # Store Data
            'add': '0011',  # Add
            'sub': '0100',  # Subtract
            'jmp': '0101',  # Jump
            'beq': '0110',  # Branch if Equal
            'bne': '0111',  # Branch if Not Equal
            'cmp': '1000',  # Compare
            'and': '1001',  # Logical AND
            'or': '1010',   # Logical OR
            'xor': '1011',  # Logical XOR
            'shl': '1100',  # Shift Left
            'shr': '1101',  # Shift Right
            'push': '1110', # Push
            'pop': '1111',  # Pop (Same opcode as PUSH)
        }


        # Define a set of recognized directives
        self.directives = {
            '.global',
            '.text',
            '.data',
            '.org',
            '.asciz',
            '.include',
            '.section',
            '.align',
        }

        # Convert opcodes and directives to lowercase for case-insensitive comparison
        self.instruction_set = {opcode.lower(): binary for opcode, binary in self.instruction_set.items()}
        self.directives = {directive.lower() for directive in self.directives}

        # Create an empty dictionary to store labels and their addresses
        self.labels = {}

        # Initialize the memory address to 0
        self.memory_address = 0

    def process_directive(self, directive, operands):
        # Handle different directives here
        if directive == '.global':
            # Process .global directive
            pass  # Implement your logic here

        elif directive == '.text':
            # Process .text directive
            pass  # Implement your logic here

        elif directive == '.data':
            # Process .data directive
            pass  # Implement your logic here

        elif directive == '.org':
            # Update the current memory address
            self.memory_address = int(operands[0], 16)

        elif directive == '.asciz':
            # Process .asciz directive
            pass  # Implement your logic here

        elif directive == '.include':
            # Process .include directive
            pass  # Implement your logic here

        elif directive == '.section':
            # Process .section directive
            pass  # Implement your logic here

        elif directive == '.align':
            # Process .align directive
            pass  # Implement your logic here

    def assemble(self, input_file):
        # Get the base name of the input file
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Create the output file name with .bin extension
        output_file = f"{base_name}.bin"

        # Open the input file in read mode
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # Convert all input to lowercase
        lines = [line.strip().lower() for line in lines]

        # Create an empty list to store machine code instructions
        machine_code = []

        # Iterate through the lines of the assembly program
        for line in lines:
            # Split the line into tokens based on whitespace
            tokens = line.split()

            # Check if the line is empty or a comment
            if not tokens or tokens[0].startswith('#'):
                continue

            # Check if the line defines a label
            if tokens[0].endswith(':'):
                # Remove the colon from the label
                label = tokens[0][:-1]

                # Store the label and its address in the dictionary
                self.labels[label] = self.memory_address

            else:
                # Check if it's a directive
                if tokens[0] in self.directives:
                    # Handle the directive
                    self.process_directive(tokens[0], tokens[1:])
                    continue

                # Extract the opcode and operands
                opcode = tokens[0]
                operands = tokens[1:]

                # Check if the opcode is valid
                if opcode not in self.instruction_set:
                    raise ValueError(f"Invalid opcode: {opcode}")

                # Check if it's a jump instruction and handle label references
                if opcode == 'jmp' or opcode == 'beq' or opcode == 'bne':
                    # Check if the operand is a label
                    if operands[0] in self.labels:
                        # Calculate the relative address
                        target_address = self.labels[operands[0]] - self.memory_address - 1
                        operands[0] = str(target_address)

                # Check if it's a .org directive
                if opcode == '.org':
                    # Update the memory address
                    self.memory_address = int(operands[0], 16)
                    continue

                # Lookup the opcode binary representation
                opcode_binary = self.instruction_set[opcode]

                # Construct the full machine code instruction
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{' '.join(operands)}"

                # Append the machine code to the list
                machine_code.append(machine_instruction)

                # Increment the memory address
                self.memory_address += 1
##############################################################
## OK, there is a difference in output from this assembler
## and the text to binary converter program. The assembler(A)
## output and the binconverter(B) are different. The binconverter
## takes the machine code in a text file:
## 0001000000100000
## 0101111111111111
## and outputs this (hexdump)
## 0000000 2010 ff5f                              
## 0000004
## which is the correct conversion of the machine code (big-endian)
## into a binary file. 
################
## However the assembler outputs this hexdump
## 0000: 0001r0, 0xfe
## 0001: 01010xff
## 
## THe machine code and the assembly program are doing the same thing
## load a value into the R0 register, then JMP to 0xFF to halt the
## emulator. 
##################################################################
#        # (A) Write the machine code to the output file with .bin extension
#        with open(output_file, 'w') as f:
#            for instruction in machine_code:
#                print (instruction + '\n')
#                f.write(instruction + '\n')
##################################################################
#        # (B) Open the binary file for writing in binary mode
#        with open(output_file, "wb") as binary_f:
#            # Write the binary data as bytes to the binary file
#            for binary_integer in binary_data:
#                binary_f.write(binary_integer.to_bytes(2, byteorder="big"))
##################################################################
## What needs to happen is this assembler must convert everything 
## to big-endian binary, and then write it out like the 
## binconverter program does. 
##################################################################

        print(f"Assembly complete. Output written to '{output_file}'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler4emulator.py <input_file.s>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: The input file '{input_file}' does not exist.")
        sys.exit(1)

    assembler = Assembler()
    assembler.assemble(input_file)

