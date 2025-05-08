import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Optional

from colorama import Fore, Style
from colorama import init as colorama_init


_COLOR_MAP: Final[dict[int, str]] = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT,
}
_DEFAULT_FMT: Final[str] = (
    "%(asctime)s — %(name)s [%(lineno)d] — %(levelname)-8s — %(message)s"
)
_DEFAULT_DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"


class _ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        color = _COLOR_MAP.get(record.levelno, "")
        return f"{color}{message}{Style.RESET_ALL}"


@dataclass(slots=True)
class LoggerConfig:
    name: str = "app"
    level: int = logging.INFO
    log_file: Optional[Path | str] = None
    propagate: bool = False
    fmt: str = _DEFAULT_FMT
    datefmt: str = _DEFAULT_DATEFMT
    colorize: bool = True
    _logger: logging.Logger = field(init=False, repr=False)

    def get(self) -> logging.Logger:
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.level)
        self._logger.propagate = self.propagate
        self._clear_handlers()
        self._configure_stdout()
        if self.log_file:
            self._configure_file()
        return self._logger

    @staticmethod
    def log_banner(
        logger: logging.Logger,
        message: str,
        width: int = 64
    ) -> None:
        border = "#" * width
        middle = f"## {message.center(width - 6)} ##"
        logger.info(border)
        logger.info(middle)
        logger.info(border)

    def _clear_handlers(self) -> None:
        self._logger.handlers.clear()

    def _configure_stdout(self) -> None:
        if sys.platform.startswith("win"):
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)

        colorama_init(autoreset=True)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        formatter_cls = _ColorFormatter if self.colorize else logging.Formatter
        stream_handler.setFormatter(formatter_cls(self.fmt, self.datefmt))
        self._logger.addHandler(stream_handler)

    def _configure_file(self) -> None:
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(self.fmt, self.datefmt))
        self._logger.addHandler(file_handler)


def get_logger(
    name: str = "app",
    *,
    level: int = logging.INFO,
    debug: bool = False,
    log_file: Optional[Path | str] = None,
    color: bool = True,
) -> logging.Logger:
    if debug:
        level = logging.DEBUG
    return LoggerConfig(
        name=name,
        level=level,
        log_file=log_file,
        colorize=color
    ).get()
