import dataclasses
import typing as t

from src.exceptions import PyLoxAttributeError
from src.utils.expr import Literal

from .callables import LoxCallable
from .types import LoxContainer

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = ("LoxHash",)

# pyright: reportIncompatibleVariableOverride=false


@dataclasses.dataclass
class HashCallable(LoxCallable):
    parent: "LoxHash"
    token: "Token"

    @property
    def arity(self) -> int:
        raise NotImplementedError

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        raise NotImplementedError


@dataclasses.dataclass
class Get(HashCallable):
    parent: "LoxHash"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        return self.parent.fields.get(arguments[0], Literal(None))


@dataclasses.dataclass
class Set(HashCallable):
    parent: "LoxHash"
    token: "Token"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        self.parent.fields[arguments[0]] = arguments[1]
        return Literal(None)


class LoxHash(LoxContainer):
    parent: t.Type["LoxHash"]
    fields: dict[t.Any, t.Any]
    methods: dict[str, t.Type[HashCallable]] = {"get": Get, "set": Set}

    def __init__(self) -> None:
        self.parent = LoxHash
        self.fields = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.fields})"

    def __str__(self) -> str:
        return str(self.fields)

    def __len__(self) -> int:
        return len(self.fields)

    def get(self, name: "Token", /) -> t.Any:
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise PyLoxAttributeError(f"Undefined property '{name.lexeme}'.")
