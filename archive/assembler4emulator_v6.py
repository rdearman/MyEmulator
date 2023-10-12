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
            'r2': '10',
            'r3': '11',  # Updated value for R3
            # Add more registers as needed
        }

        # Convert opcodes and directives to lowercase for case-insensitive comparison
        self.instruction_set = {opcode.lower(): binary for opcode, binary in self.instruction_set.items()}
        self.directives = {directive.lower() for directive in self.directives}

        # Create an empty dictionary to store labels and their addresses
        self.labels = {}

        # Initialize the memory address to 0
        self.memory_address = 0

        # Initialize the current line number to 0
        self.current_line_number = 0

        # Create a dictionary to store the current values of registers
        register_values = {reg: 0 for reg in self.register_map}

    def immediate_to_binary(self, operand):
        if operand.startswith('#'):
            # Remove the '#' symbol
            operand = operand[1:]

            # Check if it's a hexadecimal immediate value (e.g., '#0x10')
            if operand.startswith('0x'):
                # Convert hexadecimal immediate value to binary (8 bits)
                hex_value = int(operand, 16)
                binary_value = format(hex_value, '08b')
                print(f"Hex Value: {hex_value}")
                print(f"Binary Value: {binary_value}")
                return binary_value

            # Check if it's a binary immediate value (e.g., '#0b1010')
            elif operand.startswith('0b'):
                binary_text = operand[2:]  # Remove the '0b' prefix
                binary_value = binary_text
                # Ensure the binary value is 8 bits long
                while len(binary_value) < 8:
                    binary_value = '0' + binary_value
                print(f"Binary Value: {binary_value}")
                return binary_value

            # Treat it as a decimal immediate value (e.g., '#10')
            else:
                # Convert decimal immediate value to binary (8 bits)
                dec_value = int(operand)
                binary_value = format(dec_value, '08b')
                print(f"Decimal Value: {dec_value}")
                print(f"Binary Value: {binary_value}")
                return binary_value

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

        # Create a dictionary to store the current values of registers
        register_values = {reg: 0 for reg in self.register_map}

        # Iterate through the lines of the assembly program
        for line in lines:
            # Increment the current line number
            self.current_line_number += 1

            # Split the line into tokens based on whitespace
            tokens = line.split(';')  # Use ';' as the comment character

            # Check if the line is empty
            line = tokens[0].strip()  # Only consider the part before the comment character

            # Skip empty lines
            if not line:
                continue

            # Check if the line defines a label
            if line.endswith(':'):
                # Remove the colon from the label
                label = line[:-1]

                # Store the label and its address in the dictionary
                self.labels[label] = self.memory_address

            else:
                # Split the remaining line into tokens based on whitespace
                tokens = line.split()

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
                    raise ValueError(f"Invalid opcode: {opcode} (Line {self.current_line_number})")

                # Lookup the opcode binary representation
                opcode_binary = self.instruction_set[opcode]

                # Strip commas from operands
                operands = [operand.replace(',', '') for operand in operands]

                # Print values for debugging
                print(f"In Assemble A Opcode: {opcode}")
                print(f"Opcode: {opcode}")
                print(f"Operands: {operands}")

                # Handle operand resolution for ld and st instructions
                for i in range(len(operands)):
                    if operands[i].startswith('[') and operands[i].endswith(']'):
                        mem_operand = operands[i][1:-1]
                        if mem_operand in self.register_map:
                            # This is a register reference inside brackets
                            operands[i] = f'#{register_values[mem_operand]}'
                        else:
                            try:
                                # Attempt to convert the memory address to an integer
                                mem_address = int(mem_operand, 16)
                                operands[i] = f'#{mem_address}'  # Replace [rx] with the resolved address
                            except ValueError:
                                # Operand is not a valid memory address
                                raise ValueError(f"Invalid memory address: {mem_operand} (Line {self.current_line_number})")
                    else:
                        # If it's not in brackets, it's a regular register reference
                        if operands[i] in self.register_map:
                            operands[i] = f'#{register_values[operands[i]]}'


                # Categorize instructions into two groups
                if opcode in ['add', 'li', 'st', 'cmp', 'sub', 'and', 'or', 'xor', 'shl', 'shr']:
                    # Instructions that affect registers (Group 1)
                    # Construct the machine code instruction for this group
                    machine_instruction = self.process_group_1(opcode, operands, opcode_binary)
                elif opcode in ['beq', 'bne', 'jmp', 'push', 'pop']:
                    # Instructions that don't affect registers (Group 2)
                    # Construct the machine code instruction for this group
                    machine_instruction = self.process_group_2(opcode, operands, opcode_binary)
                else:
                    raise ValueError(f"Invalid opcode: {opcode} (Line {self.current_line_number})")


                # Convert the machine code instruction to a big-endian binary integer
                binary_instruction = int(''.join(machine_instruction.split()[1:]), 2)

                # Reverse the byte order (little-endian to big-endian)
                reversed_binary_instruction = ((binary_instruction & 0xFF) << 8) | ((binary_instruction >> 8) & 0xFF)

                # Append the reversed binary instruction to the list
                binary_data.append(reversed_binary_instruction)

                # Print values for debugging
                print(f"In Assemble B Opcode: {opcode}")
                print(f"Operands: {operands}")
                print(f"Machine Instruction: {machine_instruction}")

                # Update register values if needed
                if opcode in self.register_map:
                    reg_dest = self.register_map[opcode]
                    if reg_dest in register_values:
                        # Check if the instruction updates the register value
                        if opcode == 'li':
                            # For "li" instruction, update with the immediate value
                            register_values[reg_dest] = int(operands[0][1:], 16)
                        elif opcode == 'add':
                            # For "add" instruction, update with the result
                            register_values[reg_dest] = (register_values[operands[0]] + register_values[operands[1]]) & 0xFFFF
                        # Add similar handling for other instructions as needed



    def process_group_1(self, opcode, operands, opcode_binary):
        print(f"Inside Process Group Opcode: {opcode}")
        print(f"Operands: {operands}")
        # Instructions that affect registers (Group 1)
        if len(operands) == 2:
            if operands[1].startswith('#'):
                # Handle the "li" instruction with an immediate value
                immediate_binary = self.immediate_to_binary(operands[1])
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{self.register_map[operands[0]]}{immediate_binary}"
            elif operands[1].startswith('[') and operands[1].endswith(']'):
                # Memory access instruction with square brackets
                # Parse the register inside the square brackets
                mem_operand = operands[1][1:-1]
                if mem_operand in self.register_map:
                    # Calculate the memory address
                    mem_address = self.labels[mem_operand] if mem_operand in self.labels else int(mem_operand, 16)
                    mem_address_binary = format(mem_address, '016b')  # Update to 16 bits binary
                    machine_instruction = f"{opcode_binary}{self.register_map[operands[0]]}{mem_address_binary}"
                else:
                    raise ValueError(f"Invalid register in memory access: {mem_operand} (Line {self.current_line_number})")
            else:
                # Instructions with two registers
                if operands[1] in self.register_map:
                    machine_instruction = f"{opcode_binary}{self.register_map[operands[0]]}{self.register_map[operands[1]]}{'0000000000000000'}"
                else:
                    raise ValueError(f"Invalid register: {operands[1]} (Line {self.current_line_number})")
        elif len(operands) == 1:
            # Handle instructions with one operand (e.g., push, pop, jmp)
            if operands[0].startswith('#'):
                # Handle the "jmp" instruction with an immediate value
                immediate_binary = self.immediate_to_binary(operands[0])
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{immediate_binary}{'00'}{'00'}"
            elif operands[0].startswith('[') and operands[0].endswith(']'):
                # Memory access instruction with square brackets
                # Parse the register inside the square brackets
                mem_operand = operands[0][1:-1]
                if mem_operand in self.register_map:
                    # Calculate the memory address
                    mem_address = self.labels[mem_operand] if mem_operand in self.labels else int(mem_operand, 16)
                    mem_address_binary = format(mem_address, '08b')
                    machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{'00'}{mem_address_binary}{'00'}"
                else:
                    raise ValueError(f"Invalid register in memory access: {mem_operand} (Line {self.current_line_number})")
            else:
                # Instructions with one register (push, pop)
                if operands[0] in self.register_map:
                    machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{self.register_map[operands[0]]}{'00'}{'00'}"
                else:
                    raise ValueError(f"Invalid operand: {operands[0]} (Line {self.current_line_number})")
        elif len(operands) == 3:
            # Instructions with three operands (CMP)
            if all(operand in self.register_map for operand in operands):
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{self.register_map[operands[0]]}{self.register_map[operands[1]]}{self.register_map[operands[2]]}"
            else:
                raise ValueError(f"Invalid register in operands (Line {self.current_line_number})")
        else:
            raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")
        return machine_instruction




    def process_group_2(self, opcode, operands, opcode_binary):
        # Instructions that don't affect registers (Group 2)
        if opcode in ['jmp', 'push', 'pop']:
            if len(operands) != 1:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")

            if opcode == 'jmp':
                # Handle the "jmp" instruction
                if operands[0].startswith('#'):
                    # Immediate value
                    immediate_text = operands[0][1:]  # Remove the '#' character
                    immediate_binary = format(int(immediate_text, 16), '08b')  # Convert hex to binary
                else:
                    # Label
                    if operands[0] in self.labels:
                        target_address = self.labels[operands[0]]
                    else:
                        raise ValueError(f"Undefined label: {operands[0]} (Line {self.current_line_number})")
                    # Calculate the relative address
                    relative_address = target_address - self.memory_address - 1
                    if relative_address < 0:
                        raise ValueError(f"Label '{operands[0]}' is located before the current address (Line {self.current_line_number})")
                    immediate_binary = format(relative_address, '08b')  # Update to 8 bits binary
            else:
                # Handle "push" and "pop" instructions
                immediate_text = operands[0]
                immediate_binary = format(int(immediate_text, 16), '08b')  # Convert hex to binary

            # Construct the machine instruction as text
            machine_instruction_text = f"{opcode_binary}0000{immediate_binary}"

            # Return the machine instruction as a formatted string
            return f"{self.memory_address:04X}: {machine_instruction_text}"

        elif opcode in ['beq', 'bne']:
            # Branch instructions
            if len(operands) != 1:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")

            if operands[0] in self.labels:
                # Calculate the relative address
                target_address = self.labels[operands[0]] - self.memory_address - 1
                immediate_binary = format(target_address, '08b')  # Update to 8 bits binary
            else:
                # Operand is an immediate value
                immediate_text = operands[0]
                immediate_binary = format(int(immediate_text, 16), '08b')  # Convert hex to binary

            # Construct the machine instruction as text
            machine_instruction_text = f"{opcode_binary}0000{immediate_binary}"

            # Return the machine instruction as a formatted string
            return f"{self.memory_address:04X}: {machine_instruction_text}"

        else:
            raise ValueError(f"Invalid opcode: {opcode} (Line {self.current_line_number})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler4emulator.py <input_file.s>")
        sys.exit(1)  # Exit with error code 1

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: The input file '{input_file}' does not exist.")
        sys.exit(1)  # Exit with error code 1

    assembler = Assembler()
    try:
        assembler.assemble(input_file)
    except ValueError as e:
        print(f"Error (Line {assembler.current_line_number}): {str(e)}")
        sys.exit(1)  # Exit with error code 1
