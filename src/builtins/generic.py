import dataclasses
import time
import typing as t

from src.exceptions import PyLoxTypeError
from src.internals.array import LoxArray
from src.internals.hash import LoxHash
from src.internals.http import LoxRequest
from src.internals.string import LoxString

from . import BuiltInCallable

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter


NUMERIC = t.Union[int, float]


@dataclasses.dataclass
class Array(BuiltInCallable):
    _short_name = "array"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> LoxArray:
        return LoxArray()

    @property
    def arity(self) -> int:
        return 0


@dataclasses.dataclass
class Clock(BuiltInCallable):
    _short_name = "clock"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> float:
        return time.time()

    @property
    def arity(self) -> int:
        return 0


@dataclasses.dataclass
class Length(BuiltInCallable):
    _short_name = "len"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> int:
        try:
            return len(arguments[0])
        except TypeError:
            raise PyLoxTypeError("Argument must be a string or an array.")


@dataclasses.dataclass
class Max(BuiltInCallable):
    _short_name = "max"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[NUMERIC], /) -> NUMERIC:
        return max(arguments)


@dataclasses.dataclass
class Min(BuiltInCallable):
    _short_name = "min"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[NUMERIC], /) -> NUMERIC:
        return min(arguments)


@dataclasses.dataclass
class Ord(BuiltInCallable):
    _short_name = "ord"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[str], /) -> int:
        try:
            return ord(str(arguments[0]))
        except TypeError:
            raise PyLoxTypeError("Argument must be a string.")


@dataclasses.dataclass
class Str(BuiltInCallable):
    _short_name = "str"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> LoxString:
        try:
            return LoxString(arguments[0])
        except TypeError:
            raise PyLoxTypeError("Argument must be a string or an array.")


@dataclasses.dataclass
class Int(BuiltInCallable):
    _short_name = "int"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> int:
        try:
            return int(arguments[0])
        except TypeError:
            raise PyLoxTypeError("Argument must be a string or an array.")


@dataclasses.dataclass
class Float(BuiltInCallable):
    _short_name = "float"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> float:
        try:
            return float(arguments[0])
        except TypeError:
            raise PyLoxTypeError("Argument must be a string or an array.")


@dataclasses.dataclass
class Type(BuiltInCallable):
    _short_name = "type"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> str:
        return type(arguments[0]).__name__


@dataclasses.dataclass
class Request(BuiltInCallable):
    _short_name = "requests"
    _setup = True

    @property
    def arity(self) -> int:
        return 0

    def __call__(
        self, interpreter: t.Optional["Interpreter"] = None, arguments: t.Optional[list[str]] = None, /
    ) -> LoxRequest:
        return LoxRequest()


@dataclasses.dataclass
class Hash(BuiltInCallable):
    _short_name = "hash"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> LoxHash:
        return LoxHash()
