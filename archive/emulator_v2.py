#!/usr/bin/python
#!/usr/bin/env python

import os
import datetime
import traceback
import sys
import logging
import threading

END_MARKER_ADDRESS = 0xFFFF  # Define an address as the end marker


class Emulator:
    def __init__(self):
        # Memory Data Structures
        self.ram_memory = [0x00] * 65536  # Initialize with zeros (64KB of RAM)
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

        # Define a dictionary that maps opcodes to their corresponding functions
        self.instruction_set = {
            0x0000: self.load_data,       # LD
            0x0001: self.load_immediate, # LI
            0x0010: self.store_data,     # ST
            0x0011: self.add,            # ADD
            0x0100: self.subtract,       # SUB
            0x0101: self.jump,           # JMP
            0x0110: self.branch_equal,   # BEQ
            0x0111: self.branch_not_equal, # BNE
            0x1000: self.compare,        # CMP
            0x1001: self.logical_and,    # AND
            0x1010: self.logical_or,     # OR
            0x1011: self.logical_xor,    # XOR
            0x1100: self.shift_left,     # SHL
            0x1101: self.shift_right,    # SHR
            0x1110: self.push,           # PUSH
            0x1111: self.pop             # POP
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
                return address

        # If no empty slot is found, return -1 to indicate an error
        return -1

    def read_memory(self, address):
        # Implement memory read function here
        pass

    def write_memory(self, address, data):
        # Implement memory write function here
        pass

    def load_program(self, program_binary):
        # Load the program into memory, starting from a specified address
        pass

    def execute_instruction(self, opcode, operands):
        # Check if the opcode is in the instruction set dictionary
        if opcode in self.instruction_set:
            # Call the corresponding function for the opcode
            self.instruction_set[opcode](operands)
        else:
            # Handle unsupported or undefined opcode
            print(f"Unsupported opcode: 0x{opcode:04X}")

    def load_data(self, operands):
        # Implement LD instruction logic
        pass

    def load_immediate(self, operands):
        # Extract the destination register and immediate value
        destination_register = (operands >> 4) & 0x03  # Extract 2 bits for the destination register
        immediate_value = operands & 0xFF  # Extract 8 bits for the immediate value

        # Load the immediate value into the destination register
        self.registers[destination_register] = immediate_value

        # Update the program counter (PC) for the next instruction
        self.pc_register += 1


    def store_data(self, operands):
        # Implement ST instruction logic
        pass

    def add(self, operands):
        # Extract the storage register, first register to add, and second register to add
        storage_register = (operands >> 4) & 0x03  # Extract 2 bits for storage register
        source_register_1 = (operands >> 2) & 0x03  # Extract 2 bits for first register to add
        source_register_2 = operands & 0x03  # Extract 2 bits for second register to add

        # Perform the addition and store the result in the storage register
        result = self.registers[source_register_1] + self.registers[source_register_2]
        self.registers[storage_register] = result

        # Set the zero flag if the result is zero
        if result == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        # Check for overflow and set the overflow flag accordingly
        if result > 255:  # Assuming 8-bit registers
            self.overflow_flag = True
        else:
            self.overflow_flag = False

        # Check for carry and set the carry flag accordingly
        if result > 255:  # Assuming 8-bit registers
            self.carry_flag = True
        else:
            self.carry_flag = False

        # Update the program counter (PC) for the next instruction
        self.pc_register += 1

    def subtract(self, operands):
        # Implement SUB instruction logic
        pass

    def jump(self, operands):
        # Extract the target address from the operands
        target_address = operands & 0x3FFF  # Mask the two redundant bits to the left
        # Set the program counter (PC) to the target address
        self.pc_register = target_address

    def branch_equal(self, operands):
        # Implement BEQ instruction logic
        pass

    def branch_not_equal(self, operands):
        # Implement BNE instruction logic
        pass

    def compare(self, operands):
        # Implement CMP instruction logic
        pass

    def logical_and(self, operands):
        # Implement AND instruction logic
        pass

    def logical_or(self, operands):
        # Implement OR instruction logic
        pass

    def logical_xor(self, operands):
        # Implement XOR instruction logic
        pass

    def shift_left(self, operands):
        # Implement SHL instruction logic
        pass

    def shift_right(self, operands):
        # Implement SHR instruction logic
        pass

    def push(self, operands):
        # Implement PUSH instruction logic
        pass

    def pop(self, operands):
        # Implement POP instruction logic
        pass



    def fetch_and_execute(self):
        # Fetch the instruction from memory at the PC address
        instruction = self.read_memory(self.pc_register)

        # Decode the instruction to extract opcode and operands
        opcode = (instruction >> 12) & 0xF  # Extract the opcode (4 bits)
        operands = instruction & 0xFFF     # Extract the operands (12 bits)

        # Execute the instruction using the execute_instruction function
        self.execute_instruction(opcode, operands)

        # Increment the program counter (PC) for the next instruction
        self.pc_register += 1


    def run(self):
        # Emulator main loop
        while True:
            # Fetch and execute instructions until a halt condition is met
            self.fetch_and_execute()

            # Check for the halt condition (end of program)
            if self.pc_register == END_MARKER_ADDRESS:
                break


class CPU:
    def __init__(self):
        # General-purpose registers (R1-R4)
        self.registers = [0, 0, 0, 0]
        self.SP = 0xFFFF  # Stack Pointer initialized to 0xFFFF
        self.PC = 0x0000  # Program Counter initialized to 0x0000

    def execute_instruction(self, instruction):
        # Implement instruction execution logic here
        pass

class Memory:
    def __init__(self):
        # RAM banks (Bank 1-3)
        self.ram_banks = [bytearray(256) for _ in range(3)]
        # EPROM (Bank 0)
        self.eprom = bytearray(256)

    def read(self, address, bank):
        # Implement memory read logic here
        pass

    def write(self, address, data, bank):
        # Implement memory write logic here
        pass

class CommandLineInterface:
    def __init__(self, emulator):
        self.emulator = emulator  # Store the emulator instance
        # Initialize the CLI interface
        self.create_harddrive_directory()  # Check and create the "harddrive" directory
        self.current_directory = "./"  # Set the root directory as "./harddrive"
        self.registers = [0, 0, 0, 0]  # Initialize all registers to zero
        # Change the current working directory to "./harddrive"
        os.chdir(self.current_directory)
        # Change the prompt to reflect the current directory
        os.environ['PWD'] = self.current_directory

    def create_harddrive_directory(self):
        # Check if the "harddrive" folder exists in the current working directory
        if not os.path.exists("harddrive"):
            # If it doesn't exist, create it
            os.makedirs("harddrive")


    def start(self):
        while True:
            command = input(f"{self.current_directory} $ ")
            if command == "mem":
                self.display_memory_info()
            elif command == "registers":
                self.display_register_info()
            elif command == "sysinfo":
                self.display_system_info()
            elif command.startswith("load "):
                filename = command.split(" ")[1]
                success = self.load_binary_file(filename)
                if success is not None:
                    # If loading was successful, set the PC to the starting address and run the program
                    self.emulator.pc_register = success  # Set PC to the desired starting address 
                    self.emulator.run()
            elif command.startswith("cd "):
                directory = command.split(" ")[1]
                self.change_directory(directory)
            elif command == "ls":
                self.list_files()
            elif command == "help":
                self.display_help()
            elif command == "shutdown" or command == "exit":
                self.exit()
            else:
                print("Invalid command.")

    def display_help(self):
        print("Available commands:")
        print("mem - Display memory information")
        print("registers - Display register information")
        print("sysinfo - Display system information")
        print("load <filename> - Load a binary file into memory and run it")
        print("cd <directory> - Change the current directory")
        print("ls - List files in the current directory")
        print("help - Display this help message")
        print("shutdown or exit - Exit the emulator")


    def display_memory_info(self):
        # Implement memory information display here
        pass

    def display_register_info(self):
        print("Register Info:")
        for i, value in enumerate(self.registers):
            print(f"R{i}  0x{value:02X}  {value}")

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
            None
        """
        if self.emulator is None:
            print("Emulator instance not set. Please set the emulator instance before using.")
            return

        # Check if the filename exists on the "hard drive"
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return

        try:
            # Open the binary file in binary read mode
            with open(filename, "rb") as file:
                # Read the binary data from the file
                binary_data = file.read()

            # Determine the memory location where you want to load the binary data
            # For dynamic allocation, find the first available memory slot in RAM
            memory_address = self.emulator.find_empty_memory_slot(len(binary_data))

            # Print some debugging information
            print(f"Loading binary file '{filename}' into memory at address 0x{memory_address - len(binary_data):04X}")
            print(f"Emulator RAM Memory Size: {len(self.emulator.ram_memory)}")

            # Load the binary data into the emulator's memory using the emulator instance
            for byte in binary_data:
                self.emulator.ram_memory[memory_address] = byte
                memory_address += 1

            print(f"Loaded binary file '{filename}' into memory at address 0x{memory_address - len(binary_data):04X}")
            return memory_address
        except Exception as e:
            print(f"Error loading binary file '{filename}': {str(e)}")


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

    def exit(self):
        # Add cleanup logic here if needed
        sys.exit(0)

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


