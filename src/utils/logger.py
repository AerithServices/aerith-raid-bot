import logging
import sys

RESET = "\033[0m"
PURPLE = "\033[35m"
BLUE = "\033[94m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[97m"

LEVEL_COLORS = {
    "INFO": BLUE,
    "ERROR": RED,
    "WARNING": YELLOW,
    "DEBUG": WHITE,
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        level_name = record.levelname
        color = LEVEL_COLORS.get(level_name, WHITE)
        return f"{PURPLE}[ Z ]{RESET} - {color}{level_name}{RESET} - {WHITE}{record.getMessage()}{RESET}"


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomFormatter())


def setup_logger(name: str = "zneraid", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(console_handler)
    logger.propagate = False
    return logger
