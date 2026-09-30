import logging
import os
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
        message = f"{PURPLE}[ Z ]{RESET} - {color}{level_name}{RESET} - {WHITE}{record.getMessage()}{RESET}"
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            message = f"{message}\n{record.exc_text}"
        if record.stack_info:
            message = f"{message}\n{self.formatStack(record.stack_info)}"
        return message


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomFormatter())

# discord.py internals worth reading when a command silently does nothing
DEBUG_LOGGERS = (
    "discord",
    "discord.app_commands",
    "discord.client",
    "discord.ext.commands",
    "discord.interactions",
    "discord.ui",
    "asyncio",
)

# these log full webhook urls (which embed interaction tokens) or are pure noise
QUIET_LOGGERS = ("discord.http", "aiohttp", "websockets")


def _to_level(value, default: int) -> int:
    level = getattr(logging, str(value).upper(), None)
    return level if isinstance(level, int) else default


def setup_logger(name: str = "zneraid", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(console_handler)
    logger.propagate = False
    return logger


def setup_logging(config: dict | None = None) -> tuple[logging.Logger, bool]:
    """Configure root logging so discord.py/asyncio errors are no longer swallowed."""
    settings = (config or {}).get("logging", {})
    debug = bool(settings.get("debug", False))
    root_level = _to_level(settings.get("level", "DEBUG" if debug else "INFO"), logging.INFO)
    library_level = logging.DEBUG if debug else logging.INFO

    root = logging.getLogger()
    root.setLevel(root_level)
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.addHandler(console_handler)

    log_file = settings.get("file")
    if log_file:
        log_path = os.path.abspath(log_file)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
        )
        root.addHandler(file_handler)

    logging.getLogger("zneraid").setLevel(root_level)
    for name in DEBUG_LOGGERS:
        logging.getLogger(name).setLevel(library_level)
    for name in QUIET_LOGGERS:
        logging.getLogger(name).setLevel(max(root_level, logging.INFO))

    return setup_logger(level=root_level), debug
