#!/usr/bin/python
#!/usr/bin/env python

import os
import datetime
import traceback
import sys
import logging
import threading
import logging
import signal

# Define the exit_program() function
def exit_program():
    print("Exiting the emulator.")
    sys.exit(0)  # You can specify the exit code as needed (0 for success)

# Configure logging
log_file_path = "emlog.log"
log_format = "%(asctime)s [%(levelname)s]: %(message)s"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format=log_format)

END_MARKER_ADDRESS = 0xFFFF # Define an address as the end marker

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
        # Implement memory write function here
        pass

    def load_program(self, program_binary):
        # Load the program into memory, starting from a specified address
        pass



    def execute_instruction(self, opcode, operands):
        logging.info(f"execute_instruction: {opcode , operands}")
        # Convert opcode to binary string for dictionary lookup
        opcode_binary = bin(opcode)[2:].zfill(4)
        logging.info(f"execute_instruction (opcode_binary)): {opcode_binary}")

        for a in self.instruction_set:
            if opcode_binary == a:
                instruction_function = self.instruction_set[a]
                if opcode_binary == '0101':
                    logging.info(f"JMP: 0x{operands:X}")
                instruction_function(operands)
                return

        logging.error(f"Unsupported opcode: {opcode_binary}")


    def handle_unsupported_opcode(self, opcode, operands):
        # Log unsupported opcode in binary format
        logging.error(f"Unsupported opcode: {bin(opcode)[2:].zfill(16)}")

        # Example: Halt the CPU
        self.interrupt_flag = True  # Set the interrupt flag to halt the CPU

    def load_data(self, operands):
        # Implement LD instruction logic
        pass

    def load_immediate(self, operands):
        # Extract the destination register (2 bits) and immediate value (8 bits)
        destination_register = (operands >> 8) & 0x03  # Extract 2 bits for the destination register
        immediate_value = operands & 0xFF  # Extract 8 bits for the immediate value

        # Load the immediate value into the destination register with logging
        self.registers[destination_register] = immediate_value
        logging.info(f"LOAD_IMMEDIATE: R{destination_register} <- 0x{immediate_value:02X}")

        # Update the program counter (PC) for the next instruction
        self.pc_register += 1

    def store_data(self, operands):
        # Implement ST instruction logic
        pass

    def add(self, operands):
        logging.info(f"Inside ADD")
        # Extract the destination and source registers from operands
        destination_register = (operands >> 8) & 0x03
        source_register = operands & 0x03

        # Perform addition and store the result in the destination register
        self.registers[destination_register] += self.registers[source_register]

        # Update flags as needed (e.g., zero flag, overflow flag, carry flag)
        if self.registers[destination_register] == 0:
            self.zero_flag = True
        else:
            self.zero_flag = False

        # Update the program counter (PC) for the next instruction
        self.pc_register += 1


    def subtract(self, operands):
        # Implement SUB instruction logic
        pass

    def jump(self, operands):
        # Extract the target address from the operands
        target_address = operands

        # Log the target address
        logging.info(f"JMP instruction reached. Target address: 0x{target_address:04X}")

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
        # Fetch and execute instructions only if the interrupt flag is unset
        if not self.interrupt_flag:
            # Fetch the high byte and low byte of the instruction from memory
            high_byte = self.read_memory(self.pc_register + 1)
            low_byte = self.read_memory(self.pc_register)

            # Combine the high and low bytes to form a 16-bit instruction (little-endian)
            instruction = (high_byte << 8) | low_byte

            # Check if the instruction is not None (indicating a valid memory read)
            if instruction is not None:
                # Decode the instruction to extract opcode, registers, and operands
                opcode = (instruction >> 12) & 0xF  # Extract the opcode (4 bits)
                registers = (instruction >> 8) & 0xF  # Extract the register bits (4 bits)
                operands = instruction & 0xFF  # Extract the operands (8 bits)


                # Log opcode and operands in binary
                logging.info(f"Opcode: {bin(opcode)[2:].zfill(4)}, Operands: {bin(operands)[2:].zfill(12)}")

                # Execute the instruction using the execute_instruction function
                self.execute_instruction(opcode, operands)

                # Increment the program counter (PC) for the next instruction by 2 since it's a 16-bit instruction
                self.pc_register += 2

            # Check if the PC has reached the end marker address and set the interrupt flag to halt the emulator
            logging.error(f"{self.pc_register} == {END_MARKER_ADDRESS}")
            if self.pc_register == END_MARKER_ADDRESS:  # Use END_MARKER_ADDRESS directly here
                self.interrupt_flag = True
                logging.error(f"self.pc_register == END_MARKER_ADDRESS")
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

            if command == "start" and self.emulator.interrupt_flag:
                self.emulator.interrupt_flag = False
            elif command == "step" or command == "s":
                self.step_mode = not self.step_mode
                if self.step_mode:
                    print("Step-by-step mode enabled. Press Enter to execute each instruction.")
                else:
                    print("Step-by-step mode disabled.")
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
            elif command == "breakpoints":
                print("User-defined breakpoints:")
                for bp in breakpoints:
                    print(f"0x{bp:04X}")
            elif command.startswith("break "):
                try:
                    breakpoint_address = int(command.split(" ")[1], 16)
                    breakpoints.add(breakpoint_address)
                    print(f"Breakpoint set at 0x{breakpoint_address:04X}")
                except ValueError:
                    print("Invalid breakpoint address.")
            elif command == "clear":
                breakpoints.clear()
                print("All breakpoints cleared.")
            elif command == "sysinfo":
                self.display_system_info()
            elif command.startswith("load "):
                filename = command.split(" ")[1]
                success = self.load_binary_file(filename)
                print("PC: {}".format(success))
                if success is not None:
                    # If loading was successful, set the PC to the starting address and run the program
                    self.emulator.pc_register = success  # Set PC to the desired starting address
                    self.emulator.interrupt_flag = False  # Unset the interrupt flag to start the emulator
            elif command.startswith("cd "):
                directory = command.split(" ")[1]
                self.change_directory(directory)
            elif command == "ls":
                self.list_files()
            elif command == "help" or command == "?" :
                self.display_help()
            elif command == "shutdown" or command == "exit":
                self.emulator.stop()  # Signal the emulator to stop
                exit_program()
            else:
                print("Invalid command.")

            # Check if step mode is enabled and not in the middle of execution
            if self.step_mode and not self.emulator.interrupt_flag:
                # Execute one instruction
                self.emulator.fetch_and_execute()
                # Pause and wait for user input to continue
                input("Press Enter to continue...")

        # If the loop exits, clean up and exit the program
        sys.exit()  # Exit the program


    def display_help(self):
        print("Available commands:")
        print("\tstart - Start the emulator")
        print("\tstep or s - Toggle step-by-step mode")
        print("\tlog or l - Toggle logging mode")
        print("\tmem <start_address> <end_address> - Display memory information for the specified region")
        print("\tregisters - Display register information")
        print("\tbreakpoints - List user-defined breakpoints")
        print("\tbreak <address> - Set a breakpoint at the specified address")
        print("\tclear - Clear all breakpoints")
        print("\tsysinfo - Display system information")
        print("\tload <filename> - Load a binary file into memory and run it")
        print("\tcd <directory> - Change the current directory")
        print("\tls - List files in the current directory")
        print("\thelp - Display this help message")
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
            # For dynamic allocation, find the first available memory slot in RAM
            memory_address = self.emulator.find_empty_memory_slot(len(binary_data) // 2)  # Divide by 2 for 16-bit instructions
            # Load the binary data into the emulator's memory using the emulator instance
            for i in range(0, len(binary_data), 2):
                # Combine two bytes into a 16-bit value (little-endian)
                instruction = (binary_data[i] << 8) | binary_data[i + 1]  # Corrected order
                # Store the 16-bit instruction in memory
                self.emulator.ram_memory[memory_address] = instruction
                print(f"Loaded instruction 0x{instruction:04X} at memory address 0x{memory_address:04X}")
                memory_address += 1

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

