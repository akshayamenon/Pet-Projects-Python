import logging
from colorlog import ColoredFormatter

# Create logger
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.DEBUG)

# Formatters
log_format = "%(asctime)s - %(log_color)s%(levelname)s - %(filename)s:%(lineno)d - %(message)s"
file_format = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

# Colored formatter for console
color_formatter = ColoredFormatter(
    log_format,
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# File handler (no color)
file_handler = logging.FileHandler("logger.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(file_format))

# Console handler (with color)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(color_formatter)

# Avoid duplicate handlers
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Logging function shortcuts
def info(message): logger.info(message)
def debug(message): logger.debug(message)
def warning(message): logger.warning(message)
def error(message): logger.error(message, stacklevel=2)
def critical(message): logger.critical(message)
