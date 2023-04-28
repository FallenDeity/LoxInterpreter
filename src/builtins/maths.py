import dataclasses
import math
import statistics
import typing as t

from src.internals.array import LoxArray

from . import BuiltInCallable

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter


NUMERIC = t.Union[int, float]


class SupportsIndex(t.Protocol):
    def __index__(self) -> int:
        ...

    def __round__(self, ndigits: int = 0) -> int:
        ...


@dataclasses.dataclass
class Absolute(BuiltInCallable):
    _short_name: str = "abs"

    def __call__(self, interpreter: "Interpreter", arguments: list[NUMERIC], /) -> NUMERIC:
        return abs(arguments[0])

    @property
    def arity(self) -> int:
        return 1


@dataclasses.dataclass
class Ceil(BuiltInCallable):
    _short_name: str = "ceil"

    def __call__(self, interpreter: "Interpreter", arguments: list[NUMERIC], /) -> int:
        return math.ceil(arguments[0])

    @property
    def arity(self) -> int:
        return 1


@dataclasses.dataclass
class Floor(BuiltInCallable):
    _short_name: str = "floor"

    def __call__(self, interpreter: "Interpreter", arguments: list[NUMERIC], /) -> int:
        return math.floor(arguments[0])

    @property
    def arity(self) -> int:
        return 1


@dataclasses.dataclass
class Pow(BuiltInCallable):
    _short_name: str = "pow"

    def __call__(self, interpreter: "Interpreter", arguments: list[NUMERIC], /) -> float:
        return math.pow(*arguments)

    @property
    def arity(self) -> int:
        return 2


@dataclasses.dataclass
class Round(BuiltInCallable):
    _short_name: str = "round"

    def __call__(self, interpreter: "Interpreter", arguments: list[SupportsIndex], /) -> NUMERIC:
        return round(*arguments)

    @property
    def arity(self) -> int:
        return 2


@dataclasses.dataclass
class DivMod(BuiltInCallable):
    _short_name: str = "divmod"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> LoxArray:
        return divmod(*arguments)

    @property
    def arity(self) -> int:
        return 2


@dataclasses.dataclass
class Median(BuiltInCallable):
    _short_name: str = "median"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> float:
        return statistics.median(arguments)

    @property
    def arity(self) -> int:
        return 1


@dataclasses.dataclass
class Mean(BuiltInCallable):
    _short_name: str = "mean"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> float:
        return statistics.mean(arguments)

    @property
    def arity(self) -> int:
        return 1


@dataclasses.dataclass
class Mode(BuiltInCallable):
    _short_name: str = "mode"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> float:
        return statistics.mode(arguments)

    @property
    def arity(self) -> int:
        return 1
