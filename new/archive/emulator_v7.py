#!/usr/bin/python
#!/usr/bin/env python3.10


import os
import datetime
import traceback
import sys
import logging
import threading
import signal

from emulator.emulator import Emulator
from cli.cli import CommandLineInterface

from utils import logger


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
