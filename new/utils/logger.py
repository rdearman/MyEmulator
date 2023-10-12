# logger.py

import logging

log_file_path = "emlog.log"
log_format = "%(asctime)s [%(levelname)s]: %(message)s"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format=log_format,  filemode='w')

# You can define custom loggers if needed
# logger = logging.getLogger('my_logger')
