import datetime
import enum
import logging
import os
import pathlib
import sys
import typing as t

__all__: tuple[str, ...] = ("Logger",)
FLAIR: int = 95


class LogLevelColors(enum.Enum):
    """Colors for the log levels."""

    DEBUG = "\033[96m"
    INFO = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[33m"
    CRITICAL = "\033[91m"
    ENDC = "\033[0m"
    FLAIR = "\033[95m"


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the log record."""
        record.pathname = record.pathname.replace(os.getcwd(), "~")
        return True


class Formatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(
            "[%(asctime)s] | %(pathname)s:%(lineno)d | %(levelname)s | %(message)s",
        )

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        color, end = LogLevelColors.ENDC.value, LogLevelColors.ENDC.value
        return f"{color}{super().format(record)}{end}"


class FileHandler(logging.FileHandler):
    _last_entry: datetime.datetime = datetime.datetime.today()

    def __init__(self, *, ext: str, folder: pathlib.Path | str = "logs") -> None:
        """Create a new file handler."""
        self.folder = pathlib.Path(folder)
        self.ext = ext
        self.folder.mkdir(exist_ok=True)
        super().__init__(
            self.folder / f"{datetime.datetime.today().strftime('%Y-%m-%d')}_log.{ext}",
            encoding="utf-8",
        )

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        if self._last_entry.date() != datetime.datetime.today().date():
            self._last_entry = datetime.datetime.today()
            self.close()
            self.baseFilename = (self.folder / f"{self._last_entry.strftime('%Y-%m-%d')}_log.{self.ext}").as_posix()
            self.stream = self._open()
        super().emit(record)


class Logger(logging.Logger):
    _file_handler: t.Optional[logging.FileHandler] = None

    def __init__(self, *, name: str, level: int = logging.INFO, extention: str = "log", file: bool = False) -> None:
        super().__init__(name, level)
        self._handler = logging.StreamHandler(stream=sys.stdout)
        self.file_logger = file
        self.extention = extention
        self._setup()

    def _setup(self) -> None:
        """Setup the logger."""
        self._handler.addFilter(RelativePathFilter())
        self._handler.setFormatter(Formatter())
        self.addHandler(self._handler)
        if self.file_logger:
            self._file_handler = FileHandler(ext=self.extention)
            self._file_handler.addFilter(RelativePathFilter())
            self._file_handler.setFormatter(Formatter())
            self.addHandler(self._file_handler)
        logging.addLevelName(FLAIR, "FLAIR")

    def set_formatter(self, formatter: logging.Formatter) -> None:
        """Set the formatter."""
        self._handler.setFormatter(formatter)
        if self.file_logger:
            assert self._file_handler is not None
            self._file_handler.setFormatter(formatter)

    def flair(self, message: str, *args: t.Any, **kwargs: t.Any) -> None:
        """Record a flair log."""
        self.log(FLAIR, message, *args, **kwargs)
