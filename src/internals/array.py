import dataclasses
import typing as t

from src.exceptions import PyLoxAttributeError, PyLoxIndexError, PyLoxRuntimeError

from .callables import LoxCallable
from .types import LoxContainer

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = ("LoxArray",)


# pyright: reportIncompatibleVariableOverride=false


@dataclasses.dataclass
class ArrayCallable(LoxCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        raise NotImplementedError

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        raise NotImplementedError


@dataclasses.dataclass
class Append(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        self.parent.fields.append(arguments[0])


@dataclasses.dataclass
class Insert(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        idx, value = arguments
        try:
            self.parent.fields.insert(idx, value)
        except IndexError:
            raise PyLoxIndexError(interpreter.error(self.token, "Index out of range."))


@dataclasses.dataclass
class Remove(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        try:
            self.parent.fields.remove(arguments[0])
        except ValueError:
            raise PyLoxRuntimeError(interpreter.error(self.token, "Value not found."))


@dataclasses.dataclass
class Contains(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> bool:
        return arguments[0] in self.parent.fields


@dataclasses.dataclass
class Clear(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        self.parent.fields.clear()


@dataclasses.dataclass
class Pop(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        try:
            return self.parent.fields.pop(arguments[0])
        except IndexError:
            raise PyLoxIndexError(interpreter.error(self.token, "Index out of range."))


@dataclasses.dataclass
class Reverse(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        self.parent.fields.reverse()


@dataclasses.dataclass
class Sort(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        self.parent.fields.sort()


@dataclasses.dataclass
class Join(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> str:
        try:
            return arguments[0].join(self.parent.fields)
        except AttributeError:
            raise PyLoxRuntimeError(interpreter.error(self.token, "Invalid separator."))


@dataclasses.dataclass
class Slice(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> "LoxArray":
        start, end = arguments
        try:
            return LoxArray(self.parent.fields[start:end])
        except TypeError:
            raise PyLoxRuntimeError(interpreter.error(self.token, "Invalid slice."))


@dataclasses.dataclass
class Extend(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> None:
        try:
            self.parent.fields.extend(arguments[0])
        except TypeError:
            raise PyLoxRuntimeError(interpreter.error(self.token, "Invalid iterable."))


@dataclasses.dataclass
class Copy(ArrayCallable):
    parent: "LoxArray"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> "LoxArray":
        return LoxArray(self.parent.fields.copy())


class LoxArray(LoxContainer):
    parent: t.Type["LoxArray"]
    fields: list[t.Any]
    methods: dict[str, t.Type[ArrayCallable]] = {
        "append": Append,
        "insert": Insert,
        "remove": Remove,
        "contains": Contains,
        "clear": Clear,
        "pop": Pop,
        "reverse": Reverse,
        "sort": Sort,
        "join": Join,
        "slice": Slice,
        "extend": Extend,
        "copy": Copy,
    }

    def __init__(self, fields: t.Optional[list[t.Any]] = None) -> None:
        self.parent = LoxArray
        self.fields = fields or []

    def __mul__(self, other: int, /) -> "LoxArray":
        return LoxArray(self.fields * other)

    def __str__(self) -> str:
        return f"[{', '.join(map(str, self.fields))}]"

    def get(self, name: "Token", /) -> t.Any:
        try:
            return super().get(name)
        except PyLoxAttributeError:
            pass
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise PyLoxAttributeError(f"Array has no method '{name.lexeme}'.")
