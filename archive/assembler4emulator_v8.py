#!/usr/bin/python
#!/usr/bin/env python

import os
import traceback
import sys
import logging
import re

log_file_path = "assemblerparse.log"
log_format = "%(asctime)s [%(levelname)s]: %(message)s"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format=log_format,  filemode='w')


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
        self.register_values = {reg: 0 for reg in self.register_map}


    def immediate_to_binary(self, operand):
        if operand.startswith('#'):
            # Remove the '#' symbol
            operand = operand[1:]

            # Check if it's a hexadecimal immediate value (e.g., '#0x10')
            if operand.startswith('0x'):
                # Convert hexadecimal immediate value to binary (8 bits)
                hex_value = int(operand, 16)
                binary_value = format(hex_value, '08b')
                logging.info(f"Hex Value: {hex_value}")
                logging.info(f"Binary Value: {binary_value}")
                return binary_value

            # Check if it's a binary immediate value (e.g., '#0b1010')
            elif operand.startswith('0b'):
                binary_text = operand[2:]  # Remove the '0b' prefix
                binary_value = binary_text
                # Ensure the binary value is 8 bits long
                while len(binary_value) < 8:
                    binary_value = '0' + binary_value
                logging.info(f"Binary Value: {binary_value}")
                return binary_value

            # Treat it as a decimal immediate value (e.g., '#10')
            else:
                # Convert decimal immediate value to binary (8 bits)
                dec_value = int(operand)
                binary_value = format(dec_value, '08b')
                logging.info(f"Decimal Value: {dec_value}")
                logging.info(f"Binary Value: {binary_value}")
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
            logging.info(f"Memory Address Updated: {self.memory_address}")

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

    def pre_pass(self, lines):
        # Create an empty dictionary to store labels and their addresses
        self.labels = {}
        current_address = 0  # Initialize the address

        for line in lines:
            # Check if the line defines a label
            if line.endswith(':'):
                # Remove the colon from the label
                label = line[:-1]

                # Store the label in the dictionary with the current address -1 (previous instruction)
                self.labels[label] = current_address - 1
            elif line.strip():  # Check if the line is not empty or contains only whitespace characters
                # Increment the address for non-label, non-blank lines
                current_address += 1

    def assemble(self, input_file):

        # Get the base name of the input file
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        # logging.info(f"base_name = {base_name}")

        # Get the directory of the input file
        input_dir = os.path.dirname(input_file)

        # Create the output file path in the same directory
        output_file = os.path.join(input_dir, f"{base_name}.bin")
        # Open the input file in read mode

        with open(input_file, 'r') as f:
            lines = f.readlines()

        # Convert all input to lowercase
        lines = [line.strip().lower() for line in lines]

        # Call the pre-pass function to load labels
        self.pre_pass(lines)

        # Create an empty list to store binary data
        binary_data = []

        # Create a dictionary to store the current values of registers
        register_values = {reg: 0 for reg in self.register_map}

        # Iterate through the lines of the assembly program
        for line in lines:
            # Increment the current line number
            self.current_line_number += 1

            # Split the line into tokens based on whitespace and remove the comment
            tokens = line.split(';')
            line_content = tokens[0].strip()  # Remove leading and trailing whitespace

            # Check if the line content is empty
            if not line_content:
                continue

            # Check if the line defines a label
            if line.endswith(':'):
                # Remove the colon from the label
                label = line[:-1]

                # Store the label and its address in the dictionary
                self.labels[label] = self.memory_address -1
                logging.info(f"Label Defined: {label} at Address: {self.memory_address}")
                
            else:
                # Split the remaining line into tokens based on whitespace
                tokens = line.split()

                # Check if it's a directive
                if tokens[0] in self.directives:
                    # Handle the directive
                    self.process_directive(tokens[0], tokens[1:])
                    continue

                # Extract the opcode and operands and convert opcode to lowercase
                opcode = tokens[0].lower()
                operands = tokens[1:]

                # Check if the opcode is valid
                if opcode not in self.instruction_set:
                    raise ValueError(f"Invalid opcode: {opcode} (Line {self.current_line_number})")

                # Lookup the opcode binary representation
                opcode_binary = self.instruction_set[opcode]

                # Split operands by commas and spaces, and remove empty elements
                operands = [operand.strip() for operand in re.split(r'[,\s]+', ' '.join(operands))]

                # Categorize instructions into two groups
                if opcode in ['add', 'li', 'st', 'sub', 'and', 'or', 'xor', 'shl', 'shr', 'ld']:
                    # Instructions that affect registers (Group 1)
                    # Construct the machine code instruction for this group
                    logging.info(f"Passing Operands: {operands}") 
                    machine_instruction = self.process_group_1(opcode, operands, opcode_binary)
                    if len(machine_instruction) != 22:
                        print(f"MACHINE INSTRUCTION IS NOT EQUAL TO 22: {len(machine_instruction)}")
                    logging.info(f"machine_instruction {machine_instruction}")
                elif opcode in ['beq', 'bne', 'jmp', 'cmp', 'push', 'pop']:
                    # Instructions that don't affect registers (Group 2)
                    # Construct the machine code instruction for this group
                    logging.info(f"Passing Operands: {operands}") 
                    
                    # In the second pass, when you encounter labels used as branch targets, look up their addresses
                    # print(f"operands==>{operands}")
                    if operands[0] in self.labels:
                        target_address = self.labels[operands[0]]
                        logging.info(f"target_address {target_address}")

                    machine_instruction = self.process_group_2(opcode, operands, opcode_binary)
                    if len(machine_instruction) != 22:
                        print(f"MACHINE INSTRUCTION IS NOT EQUAL TO 22: {len(machine_instruction)}")
                    logging.info(f"machine_instruction {machine_instruction}")
                else:
                    raise ValueError(f"Invalid opcode: {opcode} (Line {self.current_line_number})")


                # Split machine_instruction on ":" to separate memory address and binary instruction
                memory_address_str, binary_instruction = machine_instruction.split(":")
                #print(f"memory_address_str {memory_address_str}") 
                #print(f"binary_instruction {binary_instruction}") 
                
                # Convert memory_address_str to an integer (hexadecimal to decimal)
                memory_address = int(memory_address_str, 16)
                #print(f"memory_address {memory_address}") 

                # Append the memory address (as an integer) and binary instruction (as a string) to binary_data
                binary_data.append((memory_address, binary_instruction))  # Strip any leading/trailing whitespace
                
                self.memory_address += 1

        # Sort binary_data based on memory addresses
        binary_data.sort(key=lambda x: x[0])


        # Open the binary file for writing in binary mode
        # need to figure out how to do memory addresses. 
        with open(output_file, "wb") as binary_f:
            for memory_address, machine_instruction in binary_data:
                binary_f.write(int(machine_instruction, 2).to_bytes(2, byteorder="big"))

        print(f"Assembly complete. Output written to '{output_file}'.")

#------------------------------------------------


    def process_group_1(self, opcode, operands, opcode_binary):
        logging.info(f"\tInside Process Group Opcode: {opcode}")
        logging.info(f"\tOperands: {operands}")
        logging.info(f"\tOpcode Binary: {opcode_binary}")
        logging.info(f"\t*** MEMORY ADDRESS FOR THIS INSTRUCTION {opcode}: {self.memory_address:04X}")
        
        # Instructions that affect registers (Group 1)

        # Initialize machine_instruction with a default value

        if opcode == 'li':
            if len(operands) != 2:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")
            if operands[1].startswith('#'):
                immediate_binary = self.immediate_to_binary(operands[1])
                #logging.info(f"immediate_binary: {immediate_binary}")
                #print(f"opcode_binary *** {opcode_binary} ***")
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{self.register_map[operands[0]]}00{immediate_binary}"  
                #print(f"machine_instruction !!!*** {machine_instruction} ***!!!")            
            else:
                raise ValueError(f"Invalid operand for opcode {opcode}: {operands[1]} (Line {self.current_line_number})")
        elif opcode in ['ld', 'st']:
            if len(operands) != 2:
                raise ValueError(f"Invalid number of operands for opcode {opcode}: {', '.join(operands)} (Line {self.current_line_number})")
            
            # Extract Rd and [Rn] from operands
            Rd = operands[0]
            Rn_with_brackets = operands[1]

            # Check if the second operand is in the form [Rn]
            if not Rn_with_brackets.startswith('[') or not Rn_with_brackets.endswith(']'):
                raise ValueError(f"Invalid operand format for opcode {opcode}: {Rn_with_brackets} (Line {self.current_line_number})")

            # Extract Rn from [Rn]
            Rn = Rn_with_brackets[1:-1]

            # Ensure that Rd and Rn are valid registers
            if Rd not in self.register_map or Rn not in self.register_map:
                raise ValueError(f"Invalid register(s) for opcode {opcode}: {', '.join([Rd, Rn])} (Line {self.current_line_number})")

            # Convert Rd and Rn to binary representation
            Rd_binary = self.register_map[Rd]
            Rn_binary = self.register_map[Rn]

            # Generate the machine instruction
            machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}{Rn_binary}00000000"

        elif opcode in ['add', 'sub']:
            Rd = operands[0]
            Rn = operands[1]

            # Check the length of operands before accessing operands[2]
            if len(operands) == 2:
                operands.append('0')  # If there's no third operand, set it to '0'

            immediate_value = 0  # Default value if operands[2] is '0' or contains a register

            if operands[2].startswith('#'):
                # Handle immediate value operand
                immediate_value = int(operands[2][1:], 16)

            immediate_binary = self.immediate_to_binary(f"#{immediate_value}")
            Rd_binary = self.register_map[Rd]
            Rn_binary = self.register_map[Rn]

            machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}{Rn_binary}{immediate_binary}"

        elif opcode in ['and', 'or', 'xor']:
            if len(operands) != 2:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")

            # Extract Rn and Rm_or_immediate from operands
            Rn = operands[0]
            Rm_or_immediate = operands[1]

            # Ensure that Rn is a valid register
            if Rn not in self.register_map:
                raise ValueError(f"Invalid register for opcode {opcode}: {Rn} (Line {self.current_line_number})")

            # Check if the second operand is an immediate value (starts with '#')
            if Rm_or_immediate.startswith('#'):
                if Rm_or_immediate.startswith('#0b'):
                    # Handle binary immediate value
                    binary_value = Rm_or_immediate[3:]  # Remove '#0b' prefix
                    immediate_binary = binary_value.zfill(8)  # Pad to 8 bits
                    immediate_binary = immediate_binary[-8:]  # Take the last 8 bits in case it's longer
                    immediate_binary = f"{immediate_binary}00"  # Add two zeros at the end
                else:
                    # Handle hexadecimal immediate value
                    immediate_value = int(Rm_or_immediate[1:], 16)
                    immediate_binary = self.immediate_to_binary(f"#{immediate_value}")
                Rd_binary = self.register_map[Rn]
                # Generate the machine instruction
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}00{immediate_binary}"
            else:
                # We are passing two registers to compare and the operand is all zeros.
                Rd_binary = self.register_map[Rn]
                Rm_binary = self.register_map[Rm_or_immediate]
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}{Rm_binary}00000000"

        elif opcode in ['shl', 'shr']:
            if len(operands) < 2 or len(operands) > 3:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")

            # Initialize Rd_binary and Rn_binary to default values
            Rd_binary = "0000"
            Rn_binary = "0000"

            # Extract Rd and Rn from operands
            Rd = operands[0]
            Rn = operands[1]


            # Ensure that Rd is a valid register
            if Rd not in self.register_map:
                raise ValueError(f"Invalid register for opcode {opcode}: {Rd} (Line {self.current_line_number})")

            if len(operands) == 3:
                # Immediate value is provided
                immediate_value = operands[2]

                # Check if the second operand is an immediate value (starts with '#')
                if immediate_value.startswith('#'):
                    if immediate_value.startswith('#0b'):
                        # Handle binary immediate value
                        binary_value = immediate_value[3:]  # Remove '#0b' prefix
                        immediate_binary = binary_value.zfill(8)  # Pad to 8 bits
                        immediate_binary = immediate_binary[-8:]  # Take the last 8 bits in case it's longer
                        immediate_binary = f"{immediate_binary}00"  # Add two zeros at the end
                    else:
                        # Handle hexadecimal immediate value
                        immediate_value = int(immediate_value[1:], 16)
                        immediate_binary = self.immediate_to_binary(f"#{immediate_value}")
                    Rd_binary = self.register_map[Rd]
                    Rn_binary = self.register_map[Rn]
                    # Generate the machine instruction
                    
                else:
                    immediate_binary = format(0, '04b')
            else:
                immediate_binary = format(0, '04b')

            machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}{Rn_binary}{immediate_binary}"

        return machine_instruction


    def process_group_2(self, opcode, operands, opcode_binary):
        # Instructions that don't affect registers (Group 2)
        logging.info(f"\tInside Process Group 2 Opcode: {opcode}")
        logging.info(f"\tPassed Operands: {operands}")
        logging.info(f"\tOpcode Binary: {opcode_binary}")

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

                # Convert the target address to binary using 8 bits
                target_address_binary = format(target_address, '08b')

            # Construct the machine instruction as text
            machine_instruction_text = f"{opcode_binary}0000{immediate_binary if operands[0].startswith('#') else target_address_binary}"

            # Return the machine instruction as a formatted string
            return f"{self.memory_address:04X}: {machine_instruction_text}"

        elif opcode in ['push', 'pop']:
            # Handle "push" and "pop" instructions
            immediate_text = operands[0]

            immediate_text = re.sub(r'[{}]', '', immediate_text)
            operand_list = [operand.strip() for operand in immediate_text.split(',')]
            # Define a dictionary to map register names to their bit positions
            register_mapping = {
                'R0': 0b00000001,
                'R1': 0b00000010,
                'R2': 0b00000100,
                'R3': 0b00001000,
                'LR': 0b00010000  # LR is represented by the 5th bit
            }

            # Initialize the register bit representation as all zeros (8 bits)
            register_binary = '00000000'

            # Process each operand and set the corresponding bit in the register binary
            for operand in operand_list:
                #logging.info(f"operand -- {operand} --")
                # Ensure that the operand is in uppercase
                operand = operand.upper()
                if operand in register_mapping:
                    register_bit = register_mapping[operand]
                    register_binary = bin(int(register_binary, 2) | register_bit)[2:].zfill(8)
                else:
                    raise ValueError(f"Invalid register: {operand} (Line {self.current_line_number})")

            # Construct the machine instruction as text
            machine_instruction_text = f"{opcode_binary}0000{register_binary}"

            # Return the machine instruction as a formatted string
            return f"{self.memory_address:04X}: {machine_instruction_text}"

        elif opcode in ['beq', 'bne']:
            # Branch instructions
            if len(operands) != 1:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")

            # Label
            if operands[0] in self.labels:
                target_address = self.labels[operands[0]]
                logging.info(f"target_address {target_address}")
            else:
                raise ValueError(f"Undefined label: {operands[0]} (Line {self.current_line_number})")

            # Convert the target address to binary using 8 bits
            target_address_binary = format(target_address, '08b')

            # Construct the machine instruction as text
            machine_instruction_text = f"{opcode_binary}0000{target_address_binary}"

            # Return the machine instruction as a formatted string
            return f"{self.memory_address:04X}: {machine_instruction_text}"

        elif opcode == 'cmp':
            if len(operands) != 2:
                raise ValueError(f"Invalid number of operands for opcode {opcode} (Line {self.current_line_number})")

            # Extract Rd and Rn from operands
            Rd = operands[0].lower()
            Rn = operands[1].lower()

            # Check if the first operand is an immediate value (starts with '#')
            if Rn.startswith('#'):
                immediate_value = int(Rn[1:], 16)
                immediate_binary = self.immediate_to_binary(f"#{immediate_value}")
                Rd_binary = self.register_map[Rd]  # Set Rd to R0 in the binary representation
                Rn_binary = "00"  # Clear Rn since it's not used for immediate comparisons
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}{Rn_binary}{immediate_binary}"
            else:
                # Convert Rd and Rn to binary representation
                Rd_binary = self.register_map[Rd]
                Rn_binary = self.register_map[Rn]
                machine_instruction = f"{self.memory_address:04X}: {opcode_binary}{Rd_binary}{Rn_binary}00000000"
            return machine_instruction


        else:
            raise ValueError(f"Invalid opcode: {opcode} (Line {self.current_line_number})")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        p("Usage: python assembler4emulator.py <input_file.s>")
        sys.exit(1)  # Exit with error code 1

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        logging.info(f"Error: The input file '{input_file}' does not exist.")
        sys.exit(1)  # Exit with error code 1

    assembler = Assembler()
    try:
        assembler.assemble(input_file)
    except ValueError as e:
        print(f"Error (Line {assembler.current_line_number}): {str(e)}")
        sys.exit(1)  # Exit with error code 1
