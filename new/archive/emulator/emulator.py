
import os
import datetime
import traceback
import sys
import logging
import threading
import signal
import queue  # Import the queue module
from utils import logger


# Define system call constants as class attributes
SYS_PRINT = 0
SYS_EXIT = 1
END_MARKER_ADDRESS = 0xFF # Define an address as the end marker

class Emulator:



    def __init__(self, cli):
        self.exit_event = threading.Event()  # Event to signal emulator to exit
        self.cli = cli  # Store a reference to the CommandLineInterface instance


        # Memory Data Structures
        self.ram_memory = [0x0000] * 65536 # Initialize with zeros (64KB of RAM)
        self.eprom_memory = [0] * 4096  # 4KB of EPROM

        # Bank Selection
        self.current_ram_bank = 0  # Initialize to the first RAM bank
        self.boot_eprom_bank = 60   # Set to the boot EPROM bank during bootup

        # CPU Registers
        self.registers = [0] * 5  # General-purpose registers (R0, R1, R2, R3, LR)
        self.sp_register = 0xFFFF  # Initialize Stack Pointer to 0xFFFF
        self.pc_register = 0x0000  # Initialize Program Counter to 0x0000
        self.icr_register = 0x0000  # Initialize interrupt control register, or ICR to 0x0000

        # Flags
        self.zero_flag = False
        self.overflow_flag = False
        self.carry_flag = False
        # Initialize the emulator in a halted state
        self.interrupt_flag = True

        # Define a dictionary that maps opcodes to their corresponding functions
        self.instruction_set = {
            '0000': self.load_data,       # LD
            '0001': self.load_immediate, # LI
            '0010': self.store_data,     # ST
            '0011': self.add,            # ADD
            '0100': self.subtract,       # SUB
            '0101': self.jump,           # JMP
            '0110': self.branch_equal,   # BEQ
            '0111': self.branch_not_equal, # BNE
            '1000': self.compare,        # CMP
            '1001': self.logical_and,    # AND
            '1010': self.logical_or,     # OR
            '1011': self.logical_xor,    # XOR
            '1100': self.shift_left,     # SHL
            '1101': self.shift_right,    # SHR
            '1110': self.push,           # PUSH
            '1111': self.pop             # POP
        }

    def syscall_dispatcher(self, syscall_number, register0, register1, register2, register3):
        if syscall_number == SYS_PRINT:
            args = get_string_from_memory(register0)
            self.cli.system_call_queue.put((syscall_number, args))
        elif syscall_number == SYS_EXIT:
            args = None
            self.cli.system_call_queue.put((syscall_number, args))  

        return


    def find_empty_memory_slot(self, size):
        """
        Find an empty memory slot in RAM to load a binary file.

        Args:
            size (int): The size (in bytes) of the binary data to be loaded.

        Returns:
            int: The starting memory address for loading the binary data.
        """
        # Iterate through the RAM memory to find the first available slot
        for address in range(len(self.ram_memory) - size + 1):
            # Check if the memory slot is empty (contains zeros)
            if all(byte == 0 for byte in self.ram_memory[address:address + size]):
                # print(f"Found empty slot at address 0x{address:04X}")
                return address  # Return the starting address where the empty slot was found

        # If no empty slot is found, return -1 to indicate an error
        print("No empty slot found.")
        return -1

    def get_string_from_memory(self, address):
        # Initialize an empty string to store the characters of the string
        result = ""
        # Read characters from memory until a null terminator (0x00) is encountered
        while True:
            # Read a character from memory at the current address
            char = self.read_memory(address)
            # Check if the character is a null terminator
            if char == 0x00:
                break  # Exit the loop if a null terminator is found
            # Append the character to the result string
            result += chr(char)
            # Increment the address to read the next character
            address += 1
        return result



    def read_memory(self, address):
        # Check if the address is within the valid range of memory
        if 0 <= address < len(self.ram_memory):
            return self.ram_memory[address]
        else:
            # Handle the case where the address is out of bounds by returning 0
            print(f"Error: Attempted to read from invalid memory address 0x{address:04X}.")
            return 0  # Return a default value (0) for invalid addresses

    def write_memory(self, address, data):
        # Check if the address is within the valid range of memory
        if 0 <= address < len(self.ram_memory):
            # Ensure that the data is within the byte range (0x00 to 0xFF)
            data &= 0xFF
            # Write the data to the specified memory address
            self.ram_memory[address] = data
            print(f"Memory write: Address 0x{address:04X} set to 0x{data:02X}")
        else:
            # Handle the case where the address is out of bounds
            print(f"Error: Attempted to write to invalid memory address 0x{address:04X}.")


    def execute_instruction(self, opcode, Rd, Rn, operands):
        logging.info(f"execute_instruction: {opcode, Rd, Rn, operands}")
        # Convert opcode to binary string for dictionary lookup
        opcode_binary = bin(opcode)[2:].zfill(4)
        #logging.info(f"execute_instruction (opcode_binary)): {opcode_binary}")

        for a in self.instruction_set:
            if opcode_binary == a:
                #logging.info(f"execution for loop a & opcode_binary: {a}, {opcode_binary}")
                instruction_function = self.instruction_set[a]
                #logging.info(f"instruction_function(Rd, Rn, Operands): {Rd}, {Rn}, {operands}")
                instruction_function(Rd, Rn, operands)
                logging.info("Register Info:")
                for i, value in enumerate(self.registers):
                    if i < 4:
                        logging.info(f"R{i}  0x{value:02X}  {value}")
                    elif i == 4 :
                        logging.info(f"LR  0x{value:02X}  {value}")
                # Display Stack Pointer (SP) and Program Counter (PC)
                logging.info(f"SP   0x{self.sp_register:04X}  {self.sp_register}")
                logging.info(f"PC   0x{self.pc_register:04X}  {self.pc_register}")
                # Display flags
                logging.info("Flags:")
                logging.info(f"Zero Flag: {self.zero_flag}")
                logging.info(f"Overflow Flag: {self.overflow_flag}")
                logging.info(f"Carry Flag: {self.carry_flag}")
                logging.info(f"Interrupt Flag: {self.interrupt_flag}")
                return

        # Update the program counter (PC) for the next instruction
        self.pc_register += 1
        logging.error(f"Unsupported opcode: {opcode_binary}")

    def handle_unsupported_opcode(self, opcode, operands):
        # Log unsupported opcode in binary format
        logging.error(f"Unsupported opcode: {bin(opcode)[2:].zfill(16)}")

        # Example: Halt the CPU
        self.interrupt_flag = True  # Set the interrupt flag to halt the CPU


    def load_immediate(self, Rd, Rn, operands):
        logging.info(f"Immediate Load: {Rd}, {Rn} {operands}")
        # Load the immediate value into the destination register with logging
        self.registers[Rd] = operands


    def load_data(self, Rd, Rn, operands):
        logging.info(f"Data Load: {Rd}, {Rn}, {operands}")
        # Get the memory address from Rn
        memory_address = self.registers[Rn]

        # Read the data from memory at the specified address
        data_from_memory = self.read_memory(memory_address)

        # Load the data into the destination register (Rd)
        self.registers[Rd] = data_from_memory

        # Update flags as needed (e.g., zero flag)
        if self.registers[Rd] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

    def store_data(self, Rd, Rn, operands):
        logging.info(f"Data Store: {Rd}, {Rn}, {operands}")
        # Get the memory address from Rn
        memory_address = self.registers[Rn]

        # Get the data from the source register (Rd)
        data_to_store = self.registers[Rd]

        # Write the data to memory at the specified address
        self.write_memory(memory_address, data_to_store)

        # Update flags or perform any other necessary operations


    def add(self, Rd, Rn, Operand):
        logging.info(f"Inside ADD")

        # Check if Operand is an immediate value
        if Operand is not None:
            # Add Rn and Operand and store the result in Rd
            result = self.registers[Rn] + Operand
        else:
            # Add Rn to Rd and store the result in Rd
            result = self.registers[Rd] + self.registers[Rn]

        # Set the carry flag if there is a carry-out (8-bit behavior)
        if result > 255:
            self.carry_flag = True
        else:
            self.carry_flag = False

        # Set the overflow flag if there is overflow in signed arithmetic (8-bit behavior)
        # Overflow occurs when the result is outside the signed 8-bit range (-128 to 127).
        if result > 127 or result < -128:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Perform addition and store the result in the destination register (8-bit behavior)
        self.registers[Rd] = result & 0xFF

        # Set the zero flag if the result is zero
        self.zero_flag = self.registers[Rd] == 0

        logging.info(f"Result: 0x{self.registers[Rd]:02X} ({self.registers[Rd]})")



    def subtract(self, Rd, Rn, Operand):
        logging.info(f"Inside SUB")

        # Check if Operand is not None (i.e., an immediate value)
        if Operand is not None:
            # Subtract Operand from Rn and store the result in Rd
            result = self.registers[Rn] - Operand
        else:
            # Subtract Rn from Rd and store the result in Rd
            result = self.registers[Rd] - self.registers[Rn]

        # Set the overflow flag if there is overflow in signed arithmetic (8-bit behavior)
        # Overflow occurs when subtracting two positive numbers and getting a negative result, or vice versa.
        if result > 127 or result < -128:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Perform subtraction and store the result in the destination register (8-bit behavior)
        self.registers[Rd] = result & 0xFF

        # Update flags as needed (e.g., zero flag, carry flag)
        result = self.registers[Rd]

        # Set the zero flag if the result is zero
        self.zero_flag = result == 0

        # Set the carry flag if there is a borrow during subtraction (8-bit behavior)
        # Carry occurs when subtracting a smaller number from a larger one.
        if self.registers[Rd] < self.registers[Rn]:
            self.carry_flag = True
        else:
            self.carry_flag = False

        logging.info(f"Result: 0x{result:02X} ({result})")


    def jump(self, Rd, Rn, operands):
        logging.info(f"Inside JMP")
        # Save the return address in LR
        self.registers[4] = self.pc_register

        # Set the program counter (PC) to the target address (8-bit binary)
        self.pc_register = operands
        logging.info(f"JMP instruction reached. Target address: 0x{operands}")


    def return_from_subroutine(self):
        # Load the return address from LR back into the PC
        self.pc_register = self.registers[LR]


    def branch_equal(self, Rd, Rn, operands):
        logging.info(f"Inside BEQ")
        # Check if the zero flag is set (indicating that the values in the destination and source registers are equal)
        if self.zero_flag:
            # Set the program counter (PC) to the target address (8-bit binary)
            self.pc_register = operands
            logging.info(f"BEQ instruction: Branching to address 0x{operands}")
        else:
            logging.info(f"BEQ instruction: Not branching, zero flag is not set")


    def branch_not_equal(self, Rd, Rn, operands):
        logging.info(f"Inside BNE")
        # Check if the zero flag is not set (indicating that the values in the destination and source registers are not equal)
        if not self.zero_flag:
            # Set the program counter (PC) to the target address (8-bit binary)
            self.pc_register = operands
            logging.info(f"BNE instruction: Branching to address 0x{operands}")
        else:
            logging.info(f"BNE instruction: Not branching, zero flag is set")


    def compare(self, Rd, Rn, operands):
        logging.info("Inside CMP")

        # if both Rd & Rn are zero then it is an immediate check. 
        if Rd == 0 and Rn == 0:
            source_value = operands
            destination_value = self.registers[Rd]
            result = destination_value - source_value
        else:
            # Get the values in the destination (Rd) and source (Rn) registers
            destination_value = self.registers[Rd]
            source_value = self.registers[Rn]
            result = destination_value - source_value

        # Update flags based on the comparison result
        if result == 0:
            self.zero_flag = True  # Set zero flag if the values are equal
        else:
            self.zero_flag = False

        # Check for overflow (signed comparison)
        if result > 32767 or result < -32768:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Check for carry (unsigned comparison)
        if destination_value < source_value:
            self.carry_flag = True
        else:
            self.carry_flag = False

        logging.info(f"CMP instruction result: {result}")


    def logical_and(self, Rd, Rn, operands):
        logging.info(f"Inside LOGICAL AND")
        # Get the values in the destination (Rd) and source (Rn) registers
        destination_value = self.registers[0]
        primary_value = self.registers[Rd]

        # Check if Rn is zero, indicating an immediate value
        if Rn == 0:
            # In this case, operands should contain the immediate value
            immediate_value = operands  # Assuming operands already contains the immediate value
            # Perform logical AND operation with the immediate value and store the result in the destination register
            self.registers[0] = primary_value & immediate_value
        else:
            # Rn is not zero, indicating another register as the source
            secondary_value = self.registers[Rn]
            # Perform logical AND operation and store the result in the destination register
            self.registers[0] = primary_value & secondary_value

        # Update flags as needed (e.g., zero flag)
        if self.registers[0] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        logging.info(f"AND result: {self.registers[Rd]}")
        logging.info(f"AND result: 0x{self.registers[Rd]:02X}")



    def logical_or(self, Rd, Rn, operands):
        logging.info(f"Inside LOGICAL OR")
        # Get the values in the destination (Rd) and source (Rn) registers
        destination_value = self.registers[0]
        primary_value = self.registers[Rd]

        # Check if Rn is zero, indicating an immediate value
        if Rn == 0:
            # In this case, operands should contain the immediate value
            immediate_value = operands  # Assuming operands already contains the immediate value
            # Perform logical OR operation with the immediate value and store the result in the destination register
            self.registers[0] = primary_value | immediate_value
        else:
            # Rn is not zero, indicating another register as the source
            secondary_value = self.registers[Rn]
            # Perform logical OR operation and store the result in the destination register
            self.registers[0] = primary_value | secondary_value

        # Update flags as needed (e.g., zero flag)
        if self.registers[0] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        logging.info(f"OR result: {self.registers[Rd]}")
        logging.info(f"OR result: 0x{self.registers[Rd]:02X}")

    def logical_xor(self, Rd, Rn, operands):
        logging.info(f"Inside LOGICAL XOR")
        # Get the values in the destination (Rd) and source (Rn) registers
        destination_value = self.registers[0]
        primary_value = self.registers[Rd]

        # Check if Rn is zero, indicating an immediate value
        if Rn == 0:
            # In this case, operands should contain the immediate value
            immediate_value = operands  # Assuming operands already contains the immediate value
            # Perform logical XOR operation with the immediate value and store the result in the destination register
            self.registers[0] = primary_value ^ immediate_value
        else:
            # Rn is not zero, indicating another register as the source
            secondary_value = self.registers[Rn]
            # Perform logical XOR operation and store the result in the destination register
            self.registers[0] = primary_value ^ secondary_value

        # Update flags as needed (e.g., zero flag)
        if self.registers[0] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        logging.info(f"XOR result: {self.registers[Rd]}")


    def shift_left(self, Rd, Rn, operands):
        logging.info(f"Inside SHL")

#        immediate_value = int(operands, 2)  # Convert the operand to an integer
#        result = (self.registers[Rn] << immediate_value)  # Shift left by the immediate value

        source_value = self.registers[Rn]
        # Shift left by the immediate value (assuming operands is an integer)
        result = (source_value << operands)

        # Set the overflow flag if the result has overflowed (bit 8 is set)
        if result & 0x100:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Store the result in the destination register (Rd)
        self.registers[Rd] = result & 0xFF

        # Update flags as needed (e.g., zero flag, carry flag)
        result = self.registers[Rd]

        # Set the zero flag if the result is zero
        self.zero_flag = result == 0

        # Clear the carry flag (no carry in left shift operations)
        self.carry_flag = False

        logging.info(f"Result: 0x{result:02X} ({result})")


    def shift_right(self, Rd, Rn, operands):
        logging.info(f"Inside SHR")
        
        source_value = self.registers[Rn]
        # Shift right by the immediate value (assuming operands is an integer)
        result = (source_value >> operands)


        # Set the overflow flag if the source_value has the most significant bit set
        if source_value & 0x80:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Store the result in the destination register (Rd)
        self.registers[Rd] = result & 0xFF

        # Update flags as needed (e.g., zero flag, carry flag)
        result = self.registers[Rd]

        # Set the zero flag if the result is zero
        self.zero_flag = result == 0

        # Clear the carry flag (no carry in right shift operations)
        self.carry_flag = False

        logging.info(f"Result: 0x{result:02X} ({result})")




    def push(self, Rd, Rn, operands):
        logging.info(f"Inside PUSH")
        # The 'operands' parameter is a bit mask where each bit represents a register to be popped.
        # Bit 0 (LSB) represents R0, Bit 1 represents R1, Bit 2 represents R2, and so on.
        # If a bit is set (1), it indicates that the corresponding register should be popped from the stack.
        # Additionally, Bit 4 (LR bit) indicates whether LR should be popped (1 for yes, 0 for no).
        # For example, if 'operands' is 0b00011001, it means:
        # - PUSH R0 (Bit 0 is set)
        # - PUSH R1 (Bit 1 is set)
        # - Don't PUSH R2 (Bit 2 is not set)
        # - Don't PUSH R3 (Bit 3 is not set)
        # - PUSH LR (Bit 4 is set)
        ## 
        # bit 8 ()the left most bit) represents the IRC (interupt control register)

        # Initialize a list to store the values of the pushed registers
        pushed_values = []

        # Push the values of Rd and Rn
        self.sp_register -= 1  # Decrement the stack pointer for Rd
        self.write_memory(self.sp_register, self.registers[Rd])  # Push Rd onto the stack
        pushed_values.append(("Rd", self.registers[Rd]))

        # Check if Rn should be pushed based on the next bit
        push_rn = operands & 0x01 != 0
        if push_rn:
            self.sp_register -= 1  # Decrement the stack pointer for Rn
            self.write_memory(self.sp_register, self.registers[Rn])  # Push Rn onto the stack
            pushed_values.append(("Rn", self.registers[Rn]))

        # Push R0 to R3 and LR onto the stack
        for i in range(5):
            if operands & (1 << i):
                self.sp_register -= 1  # Decrement the stack pointer
                self.write_memory(self.sp_register, self.registers[i])  # Push the register onto the stack
                pushed_values.append((f"R{i}", self.registers[i]))

        # Update flags or perform any other necessary operations
        if operands & (1 << 8):
            print(f"IRC Called")

        # Log the pushed registers and their values
        for reg, val in pushed_values:
            logging.info(f"PUSH: Register {reg}, Value: 0x{val:04X}")



    def pop(self, Rd, Rn, operands):
        logging.info(f"Inside POP")
        # The 'operands' parameter is a bit mask where each bit represents a register to be popped.
        # Bit 0 (LSB) represents R0, Bit 1 represents R1, Bit 2 represents R2, and so on.
        # If a bit is set (1), it indicates that the corresponding register should be popped from the stack.
        # Additionally, Bit 4 (LR bit) indicates whether LR should be popped (1 for yes, 0 for no).
        # For example, if 'operands' is 0b00011001, it means:
        # - Pop R0 (Bit 0 is set)
        # - Pop R1 (Bit 1 is set)
        # - Don't pop R2 (Bit 2 is not set)
        # - Don't pop R3 (Bit 3 is not set)
        # - Pop LR (Bit 4 is set)
        # Call return_from_subroutine() if LR Bit 4 is set.
        ## 
        # bit 8 ()the left most bit) represents the IRC (interupt control register)
        
        # First check if the IRC flag has been called!
        if operands & 0x80:
            masked_value = operands & 0x7F  # Mask out the leftmost bit (bit 7)
            syscall_number = int(masked_value)  # Convert the remaining bits to an integer
            #print(f"IRC Called with integer value: {masked_value}")
            # When a syscall instruction is encountered, call syscall_dispatcher
            # syscall_number, args = self.parse_syscall_instruction()
            self.syscall_dispatcher(syscall_number, self.registers[0],self.registers[1],self.registers[2],self.registers[3])
            

        # Initialize a list to store the values of the popped registers
        popped_values = []

        # Pop the values into Rd and Rn if they are specified in operands
        if operands & 0x01:
            self.registers[Rd] = self.read_memory(self.sp_register)  # Pop into Rd
            self.sp_register += 1  # Increment the stack pointer
            popped_values.append(("Rd", self.registers[Rd]))

        if operands & 0x02:
            self.registers[Rn] = self.read_memory(self.sp_register)  # Pop into Rn
            self.sp_register += 1  # Increment the stack pointer
            popped_values.append(("Rn", self.registers[Rn]))

        # Pop R0 to R3 and LR from the stack
        for i in range(5):
            if operands & (1 << i):
                self.registers[i] = self.read_memory(self.sp_register)  # Pop into the register
                self.sp_register += 1  # Increment the stack pointer
                popped_values.append((f"R{i}", self.registers[i]))

        # Check if LR bit (Bit 4) is set in operands
        if operands & 0x10:
            # Pop LR from the stack
            self.registers[4] = self.read_memory(self.sp_register)
            self.sp_register += 1  # Increment the stack pointer

            # Set the PC to the value in LR
            self.pc_register = self.registers[4]

            logging.info(f"POP: Register LR, Value: 0x{self.registers[4]:04X}")



        # Log the popped registers and their values
        for reg, val in popped_values:
            logging.info(f"POP: Register {reg}, Value: 0x{val:04X}")




    def fetch_and_execute(self):
        # Fetch and execute instructions only if the interrupt flag is unset
        if not self.interrupt_flag:
            # Log the current PC value before fetching the instruction
            logging.info(f"fetch_and_execute() PC = 0x{self.pc_register:04X}")

            instruction = self.read_memory(self.pc_register)

            # Log the memory address from which the instruction was read
            logging.info(f"fetch_and_execute() Read instruction from memory address 0x{self.pc_register:04X}: instruction: 0x{instruction:04X}")

            # Check if the instruction is not None (indicating a valid memory read)
            if instruction is not None:
                # Decode the instruction to extract opcode, registers, and operands
                opcode = (instruction >> 12) & 0xF  # Extract the opcode (4 bits)
                registers = (instruction >> 8) & 0xF  # Extract the register bits (4 bits)
                operands = instruction & 0xFF  # Extract the operands (8 bits)

                # Extract Rd and Rn from the registers field (assuming they are 2 bits each)
                Rd = (registers >> 2) & 0x3  # Extract the destination register (Rd)
                Rn = registers & 0x3  # Extract the source register (Rn)

                # Log opcode, operands, Rd, and Rn
                logging.info(f"fetch_and_execute() Opcode: {bin(opcode)[2:].zfill(4)}, Operands: {bin(operands)[2:].zfill(12)}")
                logging.info(f"fetch_and_execute() Rd: {bin(Rd)[2:].zfill(4)}, Rn: {bin(Rn)[2:].zfill(4)}")

                # Execute the instruction using the execute_instruction function
                self.execute_instruction(opcode, Rd, Rn, operands)

                # Increment the program counter (PC) for the next instruction by 2 since it's a 16-bit instruction
                self.pc_register += 1

                # Check if the PC has reached the end marker address and set the interrupt flag to halt the emulator
                if self.pc_register > END_MARKER_ADDRESS:  # Use END_MARKER_ADDRESS directly here
                    self.interrupt_flag = True
                    logging.error(f"Program reached END_MARKER_ADDRESS. Halting the emulator.")
            else:
                # Handle the case where reading from memory fails
                print("Error: Failed to read instruction from memory.")



    def run(self):
        while not self.exit_event.is_set():
            # Fetch and execute instructions until a halt condition is met
            self.fetch_and_execute()

            # Check for the halt condition (end of program)
            if self.pc_register == END_MARKER_ADDRESS:
                break

    def stop(self):
        # Set the exit event to signal the emulator to stop
        self.exit_event.set()


