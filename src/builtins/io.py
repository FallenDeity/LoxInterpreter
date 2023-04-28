import dataclasses
import typing as t

from src.exceptions import PyLoxFileNotFoundError
from src.internals.array import LoxArray

from . import BuiltInCallable

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter


@dataclasses.dataclass
class Input(BuiltInCallable):
    _short_name = "input"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[str], /) -> str:
        return input(arguments[0])


@dataclasses.dataclass
class Read(BuiltInCallable):
    _short_name = "read"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[str], /) -> str:
        try:
            with open(arguments[0], "r") as f:
                return f.read()
        except FileNotFoundError:
            raise PyLoxFileNotFoundError(f"File '{arguments[0]}' not found.")


@dataclasses.dataclass
class ReadLines(BuiltInCallable):
    _short_name = "read_lines"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[str], /) -> LoxArray:
        try:
            with open(arguments[0], "r") as f:
                return LoxArray(f.readlines())
        except FileNotFoundError:
            raise PyLoxFileNotFoundError(f"File '{arguments[0]}' not found.")


@dataclasses.dataclass
class Write(BuiltInCallable):
    _short_name = "write"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[str], /) -> None:
        try:
            with open(arguments[0], "w") as f:
                f.write(arguments[1])
        except FileNotFoundError:
            raise PyLoxFileNotFoundError(f"File '{arguments[0]}' not found.")
