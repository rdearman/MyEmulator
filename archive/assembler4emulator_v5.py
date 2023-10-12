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

        # Define a dictionary to map register names to their binary representations
        self.register_map = {
            'r0': '00',
            'r1': '01',
            'r2': '02',
            'r3': '04',  # Corrected value for R3
            # Add more registers as needed
        }

        # Convert opcodes and directives to lowercase for case-insensitive comparison
        self.instruction_set = {opcode.lower(): binary for opcode, binary in self.instruction_set.items()}
        self.directives = {directive.lower() for directive in self.directives}

        # Create an empty dictionary to store labels and their addresses
        self.labels = {}

        # Initialize the memory address to 0
        self.memory_address = 0

    # Define a function to convert immediate values to 8-bit binary format
    def immediate_to_binary(self, operand):
        if operand.startswith('#0x'):
            # Convert hexadecimal immediate value to binary (8 bits)
            return format(int(operand[3:], 16), '08b')
        elif operand.startswith('#'):
            # Convert decimal immediate value to binary (8 bits)
            return format(int(operand[1:]), '08b')
        else:
            raise ValueError(f"Invalid immediate value: {operand}")

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

        # Create an empty list to store binary data
        binary_data = []

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

                # Lookup the opcode binary representation
                opcode_binary = self.instruction_set[opcode]

                # Strip commas from operands
                operands = [operand.replace(',', '') for operand in operands]

                # Insert the modified code snippet for 'li' instruction here
                if opcode == 'li':
                    # Load immediate
                    immediate_binary = self.immediate_to_binary(operands[1])
                    # Ensure that the immediate value is 8 bits and pad with zeros if necessary
                    immediate_binary = immediate_binary[-8:]
                    machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{'00'}{self.register_map[operands[0]]}{immediate_binary}"
                else:
                    # Construct the full machine code instruction as a string
                    if opcode in ['jmp', 'beq', 'bne', 'shl', 'shr']:
                        # Instructions with no registers
                        machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{'00'}{'00'}{'00'}"
                    else:
                        # For instructions with registers
                        if len(operands) == 2:
                            # Instructions with two registers
                            machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{self.register_map[operands[0]]}{self.register_map[operands[1]]}{'00'}"
                        elif len(operands) == 3:
                            # Instructions with three operands (CMP)
                            machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{self.register_map[operands[0]]}{self.register_map[operands[1]]}{self.register_map[operands[2]]}"

                # Convert the machine code instruction to a big-endian binary integer
                binary_instruction = int(''.join(machine_instruction.split()[1:]), 2)

                # Reverse the byte order (little-endian to big-endian)
                reversed_binary_instruction = ((binary_instruction & 0xFF) << 8) | ((binary_instruction >> 8) & 0xFF)

                # Append the reversed binary instruction to the list
                binary_data.append(reversed_binary_instruction)

                # Increment the memory address
                self.memory_address += 1

        # Open the binary file for writing in binary mode
        with open(output_file, "wb") as binary_f:
            # Write the binary data as bytes to the binary file in little-endian order
            for binary_integer in binary_data:
                binary_f.write(binary_integer.to_bytes(2, byteorder="little"))

        print(f"Assembly complete. Output written to '{output_file}'.")

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

