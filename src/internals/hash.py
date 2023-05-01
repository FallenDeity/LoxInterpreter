import dataclasses
import typing as t

from src.exceptions import PyLoxAttributeError

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
        return self.parent.fields.get(arguments[0]) or self.parent.fields.get(str(arguments[0]))


@dataclasses.dataclass
class Set(HashCallable):
    parent: "LoxHash"
    token: "Token"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        if arguments[0] in self.parent.fields:
            self.parent.fields[arguments[0]] = arguments[1]
            return arguments[1]
        elif str(arguments[0]) in self.parent.fields:
            self.parent.fields[str(arguments[0])] = arguments[1]
            return arguments[1]
        else:
            try:
                self.parent.fields[arguments[0]] = arguments[1]
                return arguments[1]
            except TypeError:
                raise PyLoxAttributeError(f"Undefined property '{arguments[0]}'.")


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

    def __getitem__(self, key: t.Any, /) -> t.Any:
        return self.fields[key]

    def __setitem__(self, key: t.Any, value: t.Any, /) -> None:
        self.fields[key] = value

    def get(self, name: "Token", /) -> t.Any:
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise PyLoxAttributeError(f"Undefined property '{name.lexeme}'.")

    @classmethod
    def from_dict(cls, fields: dict[t.Any, t.Any], /) -> "LoxHash":
        instance = cls()
        instance.fields = fields
        return instance
