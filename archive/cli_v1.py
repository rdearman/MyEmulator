
import os
import datetime
import traceback
import sys
import logging
import threading
import signal
import sys
from utils import logger



# Define the exit_program() function
def exit_program():
    print("Exiting the emulator.")
    sys.exit(0)  # You can specify the exit code as needed (0 for success)

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
            # Read the low byte and high byte in little-endian order
            low_byte = binary_data[index]
            high_byte = binary_data[index + 1]
            # Combine the bytes into a 16-bit instruction (little-endian order)
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

