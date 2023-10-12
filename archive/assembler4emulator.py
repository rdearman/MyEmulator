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
            'LI': '0001',  # Load Immediate
            'LD': '0010',  # Load Data
            'ST': '0011',  # Store Data
            'ADD': '0100',  # Add
            'SUB': '0101',  # Subtract
            'JMP': '0110',  # Jump
            'BEQ': '0111',  # Branch if Equal
            'BNE': '1000',  # Branch if Not Equal
            'CMP': '1001',  # Compare
            'AND': '1010',  # Logical AND
            'OR': '1011',   # Logical OR
            'XOR': '1100',  # Logical XOR
            'SHL': '1101',  # Shift Left
            'SHR': '1110',  # Shift Right
            'PUSH': '1111', # Push
            'POP': '1111',  # Pop (Same opcode as PUSH)
        }

        # Create an empty dictionary to store labels and their addresses
        self.labels = {}

    def assemble(self, input_file):
        # Open the input file in read mode
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # Remove leading and trailing whitespace from each line
        lines = [line.strip() for line in lines]

        # Create an empty list to store machine code instructions
        machine_code = []

        # Initialize the address counter
        address = 0

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
                self.labels[label] = address

            else:
                # Extract the opcode and operands
                opcode = tokens[0]
                operands = tokens[1:]

                # Check if the opcode is valid
                if opcode not in self.instruction_set:
                    raise ValueError(f"Invalid opcode: {opcode}")

                # Lookup the opcode binary representation
                opcode_binary = self.instruction_set[opcode]

                # Check if it's a jump instruction and handle label references
                if opcode == 'JMP' or opcode == 'BEQ' or opcode == 'BNE':
                    # Check if the operand is a label
                    if operands[0] in self.labels:
                        # Calculate the relative address
                        target_address = self.labels[operands[0]] - address - 1
                        operands[0] = str(target_address)

                # Construct the full machine code instruction
                machine_instruction = opcode_binary + ''.join(operands)

                # Append the machine code to the list
                machine_code.append(machine_instruction)

                # Increment the address counter
                address += 1

        # Write the machine code to the output file (a.out.txt)
        with open("a.out.txt", 'w') as f:
            for instruction in machine_code:
                f.write(instruction + '\n')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler4emulator.py <input_file.s>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: The input file '{input_file}' does not exist.")
        sys.exit(1)

    assembler = Assembler()
    output_file = "a.out.txt"
    assembler.assemble(input_file)

    print(f"Assembly complete. Output written to '{output_file}'")

