#!/usr/bin/python
#!/usr/bin/env python

import os
import datetime
import traceback
import sys
import logging
import threading
import signal

# Define the exit_program() function
def exit_program():
    print("Exiting the emulator.")
    sys.exit(0)  # You can specify the exit code as needed (0 for success)

# Configure logging
log_file_path = "emlog.log"
log_format = "%(asctime)s [%(levelname)s]: %(message)s"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format=log_format)
# Set the logging level to INFO for production (or a higher level like WARNING or ERROR)
logging.basicConfig(level=logging.INFO)

END_MARKER_ADDRESS = 0xFF # Define an address as the end marker

class Emulator:
    def __init__(self):
        self.exit_event = threading.Event()  # Event to signal emulator to exit

        # Memory Data Structures
        self.ram_memory = [0x0000] * 65536 # Initialize with zeros (64KB of RAM)
        self.eprom_memory = [0] * 4096  # 4KB of EPROM

        # Bank Selection
        self.current_ram_bank = 0  # Initialize to the first RAM bank
        self.boot_eprom_bank = 60   # Set to the boot EPROM bank during bootup

        # CPU Registers
        self.registers = [0] * 4  # General-purpose registers (R0, R1, R2, R3)
        self.sp_register = 0xFFFF  # Initialize Stack Pointer to 0xFFFF
        self.pc_register = 0x0000  # Initialize Program Counter to 0x0000

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
                print(f"Found empty slot at address 0x{address:04X}")
                return address  # Return the starting address where the empty slot was found

        # If no empty slot is found, return -1 to indicate an error
        print("No empty slot found.")
        return -1



    def read_memory(self, address):
        """
        Read a byte from memory at the specified address.

        Args:
            address (int): The memory address to read from.

        Returns:
            int: The byte read from memory at the specified address, or 0 if the address is invalid.
        """
        # Check if the address is within the valid range of memory
        if 0 <= address < len(self.ram_memory):
            return self.ram_memory[address]
        else:
            # Handle the case where the address is out of bounds by returning 0
            print(f"Error: Attempted to read from invalid memory address 0x{address:04X}.")
            return 0  # Return a default value (0) for invalid addresses

    def write_memory(self, address, data):
        """
        Write a byte of data to memory at the specified address.

        Args:
            address (int): The memory address to write to.
            data (int): The byte of data to write.

        Returns:
            None
        """
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
                logging.info(f"execution for loop a & opcode_binary: {a}, {opcode_binary}")
                instruction_function = self.instruction_set[a]
                logging.info(f"instruction_function(Rd, Rn, Operands): {Rd}, {Rn}, {operands}")
                instruction_function(Rd, Rn, operands)
                logging.info("Register Info:")
                for i, value in enumerate(self.registers):
                    logging.info(f"R{i}  0x{value:02X}  {value}")
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

    def load_data(self, Rd, Rn, operands):
        # Extract the memory address from the operands
        memory_address = operands

        # Read the data from memory at the specified address
        data_from_memory = self.read_memory(memory_address)

        # Load the data into the destination register (Rd)
        self.registers[Rd] = data_from_memory

        # Update flags as needed (e.g., zero flag)
        if self.registers[Rd] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

    def load_immediate(self, Rd, Rn, operands):
        logging.info(f"Immediate Load: {Rd}, {operands}")
        # Load the immediate value into the destination register with logging
        self.registers[Rd] = operands

    def store_data(self, Rd, Rn, operands):
        # Extract the memory address from the operands
        memory_address = operands

        # Get the data from the source register (Rd)
        data_to_store = self.registers[Rd]

        # Write the data to memory at the specified address
        self.write_memory(memory_address, data_to_store)

        # Update flags or perform any other necessary operations

    def add(self, Rd, Rn, operands):
        logging.info(f"Inside ADD")
        # Inside the add function
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


    def subtract(self, Rd, Rn, operands):
        logging.info(f"Inside SUB")

        # Calculate the result without masking to preserve overflow bits
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
        # Extract the target address from the operands
        target_address = operands

        # Log the target address
        logging.info(f"JMP instruction reached. Target address: 0x{target_address:04X}")

        # Set the program counter (PC) to the target address
        self.pc_register = target_address


    def branch_equal(self, Rd, Rn, operands):
        logging.info(f"Inside BEQ")
        # Extract the target address from operands
        target_address = operands

        # Check if the zero flag is set (indicating that the values in the destination and source registers are equal)
        if self.zero_flag:
            # Set the program counter (PC) to the target address
            self.pc_register = target_address
            logging.info(f"BEQ instruction: Branching to address 0x{target_address:04X}")
        else:
            logging.info(f"BEQ instruction: Not branching, zero flag is not set")

    def branch_not_equal(self, Rd, Rn, operands):
        logging.info(f"Inside BNE")
        # Extract the target address from operands
        target_address = operands

        # Check if the zero flag is not set (indicating that the values in the destination and source registers are not equal)
        if not self.zero_flag:
            # Set the program counter (PC) to the target address
            self.pc_register = target_address
            logging.info(f"BNE instruction: Branching to address 0x{target_address:04X}")
        else:
            logging.info(f"BNE instruction: Not branching, zero flag is set")


    def compare(self, Rd, Rn, operands):
        logging.info(f"Inside CMP")
        # Get the values in the destination (Rd) and source (Rn) registers
        destination_value = self.registers[Rd]
        source_value = self.registers[Rn]

        # Compare the values without modifying any registers
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
        destination_value = self.registers[Rd]
        source_value = self.registers[Rn]

        # Perform logical AND operation and store the result in the destination register
        self.registers[Rd] = destination_value & source_value

        # Update flags as needed (e.g., zero flag)
        if self.registers[Rd] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        logging.info(f"AND result: {self.registers[Rd]}")
        logging.info(f"AND result: 0x{self.registers[Rd]:02X}")

    def logical_or(self, Rd, Rn, operands):
        logging.info(f"Inside LOGICAL OR")
        # Get the values in the destination (Rd) and source (Rn) registers
        destination_value = self.registers[Rd]
        source_value = self.registers[Rn]

        # Perform logical OR operation and store the result in the destination register
        self.registers[Rd] = destination_value | source_value

        # Update flags as needed (e.g., zero flag)
        if self.registers[Rd] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        logging.info(f"OR result: {self.registers[Rd]}")
        logging.info(f"OR result: 0x{self.registers[Rd]:02X}")

    def logical_xor(self, Rd, Rn, operands):
        logging.info(f"Inside LOGICAL XOR")
        # Get the values in the destination (Rd) and source (Rn) registers
        destination_value = self.registers[Rd]
        source_value = self.registers[Rn]

        # Perform logical XOR operation and store the result in the destination register
        self.registers[Rd] = destination_value ^ source_value

        # Update flags as needed (e.g., zero flag)
        if self.registers[Rd] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        logging.info(f"XOR result: {self.registers[Rd]}")


    def shift_left(self, Rd, Rn, operands):
        logging.info(f"Inside SHL")
        # Get the value in the source (Rn) register
        source_value = self.registers[Rn]

        # Calculate the result without masking to preserve overflow bits
        result = (source_value << 1)

        # Set the overflow flag if the result has overflowed (bit 8 is set)
        if result & 0x100:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Perform left shift operation and store the result in the destination register (Rd)
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
        # Get the value in the source (Rn) register
        source_value = self.registers[Rn]

        # Calculate the result without masking to preserve overflow bits
        result = (source_value >> 1)

        # Set the overflow flag if the source_value has the most significant bit set
        if source_value & 0x80:
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Perform right shift operation and store the result in the destination register (Rd)
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

        # Extract the source registers from the first 8 bits of operands
        source_registers = operands & 0xFF

        # Initialize a list to store the values of the pushed registers
        pushed_values = []

        # Push the values of Rd and Rn
        self.sp_register -= 1  # Decrement the stack pointer for Rd
        self.write_memory(self.sp_register, self.registers[Rd])  # Push Rd onto the stack
        pushed_values.append(("Rd", self.registers[Rd]))

        # Check if Rn should be pushed based on the next bit
        push_rn = operands & 0x100 != 0
        if push_rn:
            self.sp_register -= 1  # Decrement the stack pointer for Rn
            self.write_memory(self.sp_register, self.registers[Rn])  # Push Rn onto the stack
            pushed_values.append(("Rn", self.registers[Rn]))

        # Push the remaining general-purpose registers
        for i in range(1, 5):
            if source_registers & (1 << (i - 1)):
                self.sp_register -= 1  # Decrement the stack pointer
                self.write_memory(self.sp_register, self.registers[i])  # Push the register onto the stack
                pushed_values.append((f"R{i}", self.registers[i]))

        # Update flags or perform any other necessary operations

        # Log the pushed registers and their values
        for reg, val in pushed_values:
            logging.info(f"PUSH: Register {reg}, Value: 0x{val:04X}")


    def pop(self, Rd, Rn, operands):
        logging.info(f"Inside POP")

        # Extract the destination registers from the first 8 bits of operands
        destination_registers = operands & 0xFF

        # Initialize a list to store the values of the popped registers
        popped_values = []

        # Pop the values into Rd and Rn if they are specified in operands
        if destination_registers & 0x01:
            self.registers[Rd] = self.read_memory(self.sp_register)  # Pop into Rd
            self.sp_register += 1  # Increment the stack pointer
            popped_values.append(("Rd", self.registers[Rd]))

        if destination_registers & 0x02:
            self.registers[Rn] = self.read_memory(self.sp_register)  # Pop into Rn
            self.sp_register += 1  # Increment the stack pointer
            popped_values.append(("Rn", self.registers[Rn]))

        # Pop the remaining general-purpose registers based on the bits in operands
        for i in range(1, 5):
            if destination_registers & (1 << i):
                self.registers[i] = self.read_memory(self.sp_register)  # Pop into R{i}
                self.sp_register += 1  # Increment the stack pointer
                popped_values.append((f"R{i}", self.registers[i]))

        # Update flags or perform any other necessary operations

        # Log the popped registers and their values
        for reg, val in popped_values:
            logging.info(f"POP: Register {reg}, Value: 0x{val:04X}")


    def fetch_and_execute(self):
        # Fetch and execute instructions only if the interrupt flag is unset
        if not self.interrupt_flag:
            # Log the current PC value before fetching the instruction
            logging.info(f"PC = 0x{self.pc_register:04X}")

            instruction = self.read_memory(self.pc_register)

            # Log the memory address from which the instruction was read
            logging.info(f"fetch_and_execute() Read instruction from memory address 0x{self.pc_register:04X}: 0x{instruction:04X}")

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
                logging.info(f"Opcode: {bin(opcode)[2:].zfill(4)}, Operands: {bin(operands)[2:].zfill(12)}")
                logging.info(f"Rd: {bin(Rd)[2:].zfill(4)}, Rn: {bin(Rn)[2:].zfill(4)}")

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


class CommandLineInterface:
    def __init__(self, emulator):
        self.auto_run = True  # Add an auto_run flag, default to True
        self.logging_enabled = False  # Initialize logging as disabled
        self.emulator = emulator  # Store the emulator instance
        # Initialize the CLI interface
        self.create_harddrive_directory()  # Check and create the "harddrive" directory
        self.current_directory = "./"  # Set the root directory as "./harddrive"
        self.registers = [0, 0, 0, 0]  # Initialize all registers to zero
        # Change the current working directory to "./harddrive"
        os.chdir(self.current_directory)
        # Change the prompt to reflect the current directory
        os.environ['PWD'] = self.current_directory
        self.step_mode = False  # Initialize step mode as False


    def create_harddrive_directory(self):
        # Check if the "harddrive" folder exists in the current working directory
        if not os.path.exists("harddrive"):
            # If it doesn't exist, create it
            os.makedirs("harddrive")

    def start(self):
        breakpoints = set()  # Store user-defined breakpoints

        # Register a handler to exit cleanly when pressing Ctrl+C
        def handle_interrupt(sig, frame):
            self.emulator.stop()  # Signal the emulator to stop
            exit_program()

        signal.signal(signal.SIGINT, handle_interrupt)

        while not self.emulator.exit_event.is_set():
            command = input(f"{self.current_directory} $ ")
            if (command == "start" or command == "run"):
                self.emulator.interrupt_flag = False
            elif command == "auto":
                self.auto_run = not self.auto_run
                print(f"Auto run {'enabled' if self.auto_run else 'disabled'}.")
            elif command == "log" or command == "l":
                self.logging_enabled = not self.logging_enabled
                if self.logging_enabled:
                    print("Logging mode enabled.")
                else:
                    print("Logging mode disabled.")
            elif command.startswith("mem "):
                try:
                    # Parse the user input for memory region (start and end addresses)
                    _, start_address, end_address = command.split(" ")
                    start_address = int(start_address, 16)
                    end_address = int(end_address, 16)

                    # Ensure the addresses are within valid bounds
                    if 0 <= start_address <= end_address < len(self.emulator.ram_memory):
                        self.display_memory_info(start_address, end_address)
                    else:
                        print("Invalid memory region specified.")
                except ValueError:
                    print("Invalid memory region format. Usage: mem <start_address> <end_address>")
            elif command == "registers":
                self.display_register_info()
            elif command == "sysinfo":
                self.display_system_info()
            elif command.startswith("load "):
                filename = command.split(" ")[1]
                success = self.load_binary_file(filename)
                print("PC: {}".format(success))
                if success is not None:
                    # If loading was successful and auto_run is True, set the PC to the starting address and run the program
                    if self.auto_run:
                        self.emulator.pc_register = success  # Set PC to the desired starting address
                        self.emulator.interrupt_flag = False  # Unset the interrupt flag to start the emulator
                    else:
                        print("Program loaded. To run, type 'start' or 'run'.")
            elif command.startswith("cd "):
                directory = command.split(" ")[1]
                self.change_directory(directory)
            elif command == "ls":
                self.list_files()
            elif command == "help" or command == "?":
                self.display_help()
            elif command == "shutdown" or command == "exit":
                self.emulator.stop()  # Signal the emulator to stop
                exit_program()
            else:
                print("Invalid command.")

        # If the loop exits, clean up and exit the program
        sys.exit()  # Exit the program

    def display_help(self):
        print("Available commands:")
        print("\tstart - Start the emulator")
        print("\tlog or l - Toggle logging mode")
        print("\tmem <start_address> <end_address> - Display memory information for the specified region")
        print("\tregisters - Display register information")
        print("\tsysinfo - Display system information")
        print("\tload <filename> - Load a binary file into memory and run it")
        print("\tcd <directory> - Change the current directory")
        print("\tls - List files in the current directory")
        print("\thelp or ? - Display this help message")
        print("\tshutdown or exit - Exit the emulator")


    def display_memory_info(self, start_address=None, end_address=None):
        if start_address is None:
            start_address = 0
        if end_address is None:
            end_address = len(self.emulator.ram_memory) - 1

        print("Memory Info:")
        # Display memory contents within the specified range
        for address in range(start_address, end_address + 1):
            data = self.emulator.read_memory(address)
            print(f"Address 0x{address:04X}: 0x{data:04X}")



    def display_register_info(self):
        print("Register Info:")
        for i, value in enumerate(self.registers):
            print(f"R{i}  0x{value:02X}  {value}")

        # Display Stack Pointer (SP) and Program Counter (PC)
        print(f"SP   0x{self.emulator.sp_register:04X}  {self.emulator.sp_register}")
        print(f"PC   0x{self.emulator.pc_register:04X}  {self.emulator.pc_register}")

        # Display flags
        print("Flags:")
        print(f"Zero Flag: {self.emulator.zero_flag}")
        print(f"Overflow Flag: {self.emulator.overflow_flag}")
        print(f"Carry Flag: {self.emulator.carry_flag}")
        print(f"Interrupt Flag: {self.emulator.interrupt_flag}")
 

    def display_system_info(self):
        now = datetime.datetime.now()
        print("System Info:")
        for i, value in enumerate(self.registers):
            print(f"R{i}  0x{value:02X}  {value}")
        print(now.strftime("%Y-%m-%d %H:%M"))


    def load_binary_file(self, filename):
        """
        Load a binary file from the "hard drive" into the emulator's memory.

        Args:
            filename (str): The name of the binary file to load.

        Returns:
            int: The starting memory address where the program is loaded, or -1 on failure.
        """
        if self.emulator is None:
            print("Emulator instance not set. Please set the emulator instance before using.")
            return -1

        # Check if the filename exists on the "hard drive"
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return -1

        try:
            # Open the binary file in binary read mode
            with open(filename, "rb") as file:
                # Read the binary data from the file
                binary_data = file.read()

            # Determine the memory location where you want to load the binary data
            memory_address = self.emulator.find_empty_memory_slot(len(binary_data) // 2)  # Divide by 2 for 16-bit instructions
            index = 0  # Track the current index in the binary data

            # Load the binary data into the emulator's memory using the emulator instance
            while index < len(binary_data):
                # Read the high byte and low byte in big-endian order
                high_byte = binary_data[index]
                low_byte = binary_data[index + 1]
                # Combine the bytes into a 16-bit instruction (big-endian order)
                instruction = (high_byte << 8) | low_byte
                # Store the 16-bit instruction in memory
                self.emulator.ram_memory[memory_address] = instruction
                binary_instruction = bin(instruction)[2:].zfill(16)  # Convert to binary and format to 16 bits
                print(f"Loaded instruction 0x{instruction:04X} ({binary_instruction}) at memory address 0x{memory_address:04X}")
                
                memory_address += 1
                index += 2  # Move to the next pair of bytes

            print(f"Loaded binary file '{filename}' into memory at address 0x{memory_address - len(binary_data) // 2:04X}")
            print(f"Returning memory address: 0x{memory_address - len(binary_data) // 2:04X}")
            return memory_address - len(binary_data) // 2

        except Exception as e:
            print(f"Error loading binary file '{filename}': {str(e)}")
            return -1

    def change_directory(self, directory):
        # Implement changing directories here
        new_directory = os.path.join(self.current_directory, directory)
        # Check if the new directory is still within the "harddrive" directory
        if new_directory.startswith("./harddrive"):
            self.current_directory = new_directory
        else:
            print("Cannot go higher than the 'root' directory.")

    def list_files(self):
        # Get the list of files in the current directory (harddrive)
        try:
            files = os.listdir(self.current_directory)
            print("Files in current directory:")
            for file in files:
                file_path = os.path.join(self.current_directory, file)
                if os.path.isfile(file_path) or os.path.isdir(file_path):
                    if file_path.startswith("./harddrive"):
                        print(file)
        except OSError as e:
            print(f"Error listing files: {str(e)}")


if __name__ == "__main__":
    try:
        # Create an instance of the emulator
        emulator = Emulator()

        # Create a thread for the emulator and start it
        emulator_thread = threading.Thread(target=emulator.run)
        emulator_thread.start()

        # Create an instance of the CLI and pass the emulator instance
        cli = CommandLineInterface(emulator)

        # Start the CLI
        cli.start()
    except Exception:
        traceback.print_exc()
        logging.error("Exception occurred", exc_info=True)
        exit_code = 1
    sys.exit(exit_code)

