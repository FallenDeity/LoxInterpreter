import enum
import typing as t

__all__: tuple[str, ...] = (
    "PyLoxErrorTypes",
    "PyLoxException",
    "PyLoxRuntimeError",
    "PyLoxSyntaxError",
    "PyLoxNameError",
    "PyLoxTypeError",
    "PyLoxValueError",
    "PyLoxIndexError",
    "PyLoxKeyboardInterrupt",
    "PyLoxParseError",
    "PyLoxReturnError",
    "PyLoxBreakError",
    "PyLoxContinueError",
    "PyLoxResolutionError",
    "PyLoxAttributeError",
    "PyLoxFileNotFoundError",
)


class PyLoxErrorTypes(enum.IntEnum):
    EX_OK = 0
    EX_USAGE = 64
    EX_DATAERR = 65
    EX_NOINPUT = 66
    EX_NOUSER = 67
    EX_NOHOST = 68
    EX_UNAVAILABLE = 69
    EX_SOFTWARE = 70
    EX_OSERR = 71
    EX_OSFILE = 72
    EX_CANTCREAT = 73
    EX_IOERR = 74
    EX_TEMPFAIL = 75
    EX_PROTOCOL = 76
    EX_NOPERM = 77
    EX_CONFIG = 78


class PyLoxException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.error_type.name}: {self.message}"


class PyLoxParseError(PyLoxException):
    """Exception raised for errors in the parse."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_USAGE) -> None:
        super().__init__(message, error_type)


class PyLoxKeyboardInterrupt(PyLoxException):
    """Exception raised for errors in the keyboard."""

    def __init__(self, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        super().__init__("Keyboard Interrupt", error_type)


class PyLoxRuntimeError(PyLoxException, RuntimeError):
    """Exception raised for errors in the runtime."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_USAGE) -> None:
        super().__init__(message, error_type)


class PyLoxSyntaxError(PyLoxException):
    """Exception raised for errors in the syntax."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_USAGE) -> None:
        super().__init__(message, error_type)


class PyLoxNameError(PyLoxException):
    """Exception raised for errors in the name."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_USAGE) -> None:
        super().__init__(message, error_type)


class PyLoxTypeError(PyLoxException):
    """Exception raised for errors in the type."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_USAGE) -> None:
        super().__init__(message, error_type)


class PyLoxValueError(PyLoxException):
    """Exception raised for errors in the value."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_DATAERR) -> None:
        super().__init__(message, error_type)


class PyLoxIndexError(PyLoxException):
    """Exception raised for errors in the index."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_DATAERR) -> None:
        super().__init__(message, error_type)


class PyLoxReturnError(PyLoxRuntimeError):
    def __init__(self, message: str, value: t.Any, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        self.value = value
        super().__init__(message, error_type)


class PyLoxBreakError(PyLoxRuntimeError):
    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        super().__init__(message, error_type)


class PyLoxContinueError(PyLoxRuntimeError):
    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        super().__init__(message, error_type)


class PyLoxResolutionError(PyLoxException):
    """Exception raised for errors in the resolution."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        super().__init__(message, error_type)


class PyLoxAttributeError(PyLoxException):
    """Exception raised for errors in the attribute."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_SOFTWARE) -> None:
        super().__init__(message, error_type)


class PyLoxFileNotFoundError(PyLoxException):
    """Exception raised for errors in the file."""

    def __init__(self, message: str, error_type: PyLoxErrorTypes = PyLoxErrorTypes.EX_NOINPUT) -> None:
        super().__init__(message, error_type)
