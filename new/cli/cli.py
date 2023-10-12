
import os
import datetime
import traceback
import sys
import logging
import threading
import signal
import sys
import queue  # Import the queue module
from utils import logger

VERSION = '8.0.0'

# Define system call constants as class attributes
SYS_PRINT = 1
SYS_EXIT = 0

# File I/O
SYS_OPEN = 2
SYS_READ = 3
SYS_WRITE = 4
SYS_CLOSE = 5
SYS_SEEK = 8

# Memory Management
SYS_MALLOC = 92
SYS_FREE = 93

# Time and Date
SYS_GETTIMEOFDAY = 96
SYS_SLEEP = 11

# File and Directory Operations
SYS_MKDIR = 83
SYS_RMDIR = 84
SYS_RENAME = 82

# System Information
SYS_UNAME = 63

END_MARKER_ADDRESS = 0xFF # Define an address as the end marker

# Define the exit_program() function
def exit_program():
    print("Exiting the emulator.")
    sys.exit(0)  # You can specify the exit code as needed (0 for success)

class CommandLineInterface:

    def __init__(self, emulator):
        self.auto_run = True  # Add an auto_run flag, default to True
        self.logging_enabled = False  # Initialize logging as disabled
        self.emulator = None  # Initialize emulator attribute
        # Initialize the CLI interface
        self.create_harddrive_directory()  # Check and create the "harddrive" directory
        self.current_directory = "./"  # Set the root directory as "./harddrive"
        self.registers = [0, 0, 0, 0]  # Initialize all registers to zero
        # Change the current working directory to "./harddrive"
        os.chdir(self.current_directory)
        # Change the prompt to reflect the current directory
        os.environ['PWD'] = self.current_directory
        self.step_mode = False  # Initialize step mode as False
        self.system_call_queue = queue.Queue()  # Create a queue for system call requests

    def handle_syscalls(self):
        # This function runs in a separate thread and handles system call requests
        while not self.emulator.exit_event.is_set():
            try:
                syscall_number, args = self.system_call_queue.get(timeout=1)
                self.handle_syscall(syscall_number, args)
            except queue.Empty:
                pass

    def handle_syscall(self, syscall_number, args):
        # Process the system call request received from the emulator
        if syscall_number == SYS_PRINT:
            #print(f"CLI SYS_PRINT =>{syscall_number}")
            # Execute the print system call
            decoded_args = args.encode().decode('unicode_escape')
            print(decoded_args, end='')
            return 0  # Success
        elif syscall_number == SYS_EXIT:
            #print(f"CLI SYS_EXIT =>{syscall_number}")
            # Execute the exit system call
            self.emulator.pc_register = END_MARKER_ADDRESS
            return sys.exit()  # Terminate the CLI
        elif syscall_number == SYS_UNAME:
            #print(f"CLI SYS_UNAME =>{syscall_number}")
            print(f"Rick's Amazing Emulator version: {VERSION}")
            return 0

    def create_harddrive_directory(self):
        # Check if the "harddrive" folder exists in the current working directory
        if not os.path.exists("harddrive"):
            # If it doesn't exist, create it
            os.makedirs("harddrive")

    def start(self):
        breakpoints = set()  # Store user-defined breakpoints

        # Start a separate thread to handle system call requests
        syscall_handler_thread = threading.Thread(target=self.handle_syscalls)
        syscall_handler_thread.daemon = True  # Make the thread a daemon so it exits with the program
        syscall_handler_thread.start()

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
            elif command.startswith("store "):
                try:
                    parts = command.split()
                    address_str = parts[1]
                    data_strs = parts[2:]

                    # Function to convert a hexadecimal string to an integer
                    def parse_hexadecimal(hex_str):
                        return int(hex_str, 16)

                    address = address_str  # No need to convert, it's already in hexadecimal format
                    data = [parse_hexadecimal(data_str) for data_str in data_strs]

                    if 0 <= int(address, 16) < len(self.emulator.ram_memory):
                        self.store(address, *data)  # Call the store method
                    else:
                        print("Invalid memory address specified.")
                except ValueError as e:
                    print(f"Invalid store command format: {e}. Usage: store <address> <data1> [<data2> ...]")



            elif command == "registers":
                self.display_register_info()
            elif command == "sysinfo":
                self.display_system_info()
            elif command.startswith("load "):
                filename = command.split(" ")[1]
                success = self.load_hex_file(filename)
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

    def store(self, address_str, *data_strs):
        try:
            # Parse the address as hexadecimal
            address = int(address_str, 16)

            # Ensure the address is within valid bounds
            if 0 <= address < len(self.emulator.ram_memory):
                # Convert data values to integers (hexadecimal)
                data_values = []
                for data_str in data_strs:
                    if isinstance(data_str, str):
                        if data_str.startswith("0x"):
                            data_values.append(int(data_str, 16))
                        else:
                            raise ValueError("Invalid hexadecimal format")
                    else:
                        data_values.append(data_str)

                # Store each data value at the specified address
                for i, value in enumerate(data_values):
                    self.emulator.write_memory(address + i, value)

                print(f"Stored data at memory address {hex(address)}.")
            else:
                print("Invalid memory address specified.")
        except ValueError:
            print("Invalid store command format. Usage: store <address> <data1> [<data2> ...]")



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


    def load_hex_file(self, filename):
        if self.emulator is None:
            print("Emulator instance not set. Please set the emulator instance before using.")
            return -1

        # Check if the filename exists on the "hard drive"
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return -1

        # Determine the memory location where you want to load the binary data
        memory_address = self.emulator.find_empty_memory_slot(128 // 2)  # Divide by 2 for 16-bit instructions

        try:
            # Open the Intel Hex file in text mode for reading
            with open(filename, "r") as hex_file:
                for line in hex_file:
                    line = line.strip()  # Remove leading/trailing whitespace
                    if line.startswith(":"):
                        # Remove the start code ':' from the line
                        line = line[1:]
                        # Parse the Intel Hex record
                        byte_count = int(line[0:2], 16)
                        address = int(line[2:6], 16)
                        record_type = int(line[6:8], 16)
                        #print(f"byte_count = {byte_count}")
                        #print(f"address = {address}")
                        #print(f"record_type = {record_type}")

                        # Check if it's an end-of-file record
                        if record_type == 1:
                            #print("EOF")
                            break  # End of file, exit the loop

                        if record_type == 0:
                            # Data record (00)
                            #print("Data record (00)")
                            data_bytes = [int(line[i:i+2], 16) for i in range(8, len(line), 2)]
                            # Load data into the specified memory address
                            for data_byte in data_bytes:
                                self.emulator.ram_memory[address] = data_byte
                                #print(f"data_byte:{hex(data_byte)} => {hex(address)}")
                                address += 1

                        elif record_type == 17:
                            # Instruction record (11)
                            # print("Instruction record (11)")
                            instructions_hex = line[8:]
                            # Split the instructions into 16-bit chunks and load them into memory
                            for i in range(0, len(instructions_hex), 4):  # Change the range to 4 characters
                                instruction_chunk = instructions_hex[i:i + 4]  # Change to 4 characters
                                instruction = int(instruction_chunk, 16)
                                self.emulator.ram_memory[memory_address] = instruction
                                #print(f"instruction = {instruction}")
                                memory_address += 1

            print(f"Loaded Intel Hex file '{filename}' into memory.")
            return 0  # Success

        except Exception as e:
            print(f"Error loading Intel Hex file '{filename}': {str(e)}")
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

