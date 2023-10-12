#!/usr/bin/python
#!/usr/bin/env python

import os
import datetime
import traceback
import sys
import logging
import threading

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
        # Implement instruction execution here based on opcode and operands
        pass

    def fetch_and_execute(self):
        # Fetch an instruction from memory based on the program counter (PC)
        # Decode the instruction, extract opcode and operands
        # Execute the instruction using the execute_instruction function
        pass

    def run(self):
        # Set the PC to the specified boot address in EPROM
        self.pc_register = 0x0000FFFF
        
        # Emulator main loop
        while True:
            # Fetch and execute instructions until a halt condition is met
            self.fetch_and_execute()
            # Implement halt condition (e.g., end of program) and exit the loop
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
    def __init__(self):
        # Initialize the CLI interface
        self.root_directory = Directory("/")  # Create a virtual root directory
        self.current_directory = self.root_directory  # Set the current directory to the root
        self.registers = [0x12, 0xFF, 0x00, 0x42]  # Sample register values

    def start(self):
        while True:
            command = input(f"{self.current_directory.get_path()} $ ")
            if command == "mem":
                self.display_memory_info()
            elif command == "registers":
                self.display_register_info()
            elif command == "sysinfo":
                self.display_system_info()
            elif command.startswith("load "):
                filename = command.split(" ")[1]
                success = self.load_binary_file(filename)
                if success:
                    # If loading was successful, set the PC to the starting address and run the program
                    self.pc_register = success  # Set PC to the desired starting address
                    self.run_loaded_program()
            elif command.startswith("cd "):
                directory = command.split(" ")[1]
                self.change_directory(directory)
            elif command == "ls":
                self.list_files()
            elif command == "shutdown" or command == "exit":
                self.exit()
            else:
                print("Invalid command.")


    def run_loaded_program(self):
        # Implement run here
        pass

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
        # Check if the filename exists on the "hard drive"
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return

        # Determine the memory location where you want to load the binary data
        # For dynamic allocation, find the first available memory slot in RAM
        memory_address = self.find_empty_memory_slot(len(binary_data))

        try:
            # Open the binary file in binary read mode
            with open(filename, "rb") as file:
                # Read the binary data from the file
                binary_data = file.read()

            # Load the binary data into the emulator's memory
            for byte in binary_data:
                self.ram_memory[memory_address] = byte
                memory_address += 1

            print(f"Loaded binary file '{filename}' into memory at address 0x{memory_address - len(binary_data):04X}")
            return memory_address
        except Exception as e:
            print(f"Error loading binary file '{filename}': {str(e)}")

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

    def change_directory(self, directory):
        # Implement changing directories here
        new_directory = os.path.join(self.current_directory, directory)
        # Check if the new directory is still within the "harddrive" directory
        if new_directory.startswith("/harddrive"):
            self.current_directory = new_directory
        else:
            print("Cannot go higher than the 'root' directory.")

    def list_files(self):
        # Get the list of files in the current directory
        files = self.current_directory.list_files()
        print(f"Files in current directory {self.current_directory.get_path()}:")
        for file in files:
            print(file)

    def exit(self):
        # Add cleanup logic here if needed
        sys.exit(0)


class Directory:
    def __init__(self, path):
        self.path = path
        self.contents = {}

    def get_path(self):
        return self.path

    def list_files(self):
        return list(self.contents.keys())

if __name__ == "__main__":
    try:
        # Create an instance of the emulator
        emulator = Emulator()

        # Create a thread for the emulator and start it
        emulator_thread = threading.Thread(target=emulator.run)
        emulator_thread.start()

        # Create an instance of the CLI and start it
        cli = CommandLineInterface()
        cli.start()
    except Exception:
        traceback.print_exc()
        logging.error("Exception occurred", exc_info=True)
        exit_code = 1
    sys.exit(exit_code)


