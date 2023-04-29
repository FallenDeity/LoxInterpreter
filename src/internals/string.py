import dataclasses
import typing as t

from src.exceptions import PyLoxAttributeError

from .array import LoxArray
from .callables import LoxCallable
from .types import LoxContainer

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = ("LoxString",)


# pyright: reportIncompatibleVariableOverride=false


@dataclasses.dataclass
class StringCallable(LoxCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        raise NotImplementedError

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        raise NotImplementedError


@dataclasses.dataclass
class Lower(StringCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> str:
        return self.parent.fields.lower()


@dataclasses.dataclass
class Upper(StringCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> str:
        return self.parent.fields.upper()


@dataclasses.dataclass
class Replace(StringCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> str:
        self.parent.fields = self.parent.fields.replace(str(arguments[0]), str(arguments[1]))
        return self.parent.fields


@dataclasses.dataclass
class Split(StringCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> LoxArray:
        return LoxArray([LoxString(s) for s in self.parent.fields.split(str(arguments[0]))])


@dataclasses.dataclass
class Check(StringCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> bool:
        check = getattr(self.parent.fields, self.token.lexeme)
        if check is None:
            raise PyLoxAttributeError(interpreter.error(self.token, f"String has no attribute {self.token.lexeme!r}."))
        return check()


@dataclasses.dataclass
class Contains(StringCallable):
    parent: "LoxString"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> bool:
        return str(arguments[0]) in str(self.parent.fields)


class LoxString(LoxContainer):
    parent: t.Type["LoxString"]
    fields: str
    methods: dict[str, t.Type[StringCallable]] = {
        "lower": Lower,
        "upper": Upper,
        "replace": Replace,
        "split": Split,
        "isalnum": Check,
        "isalpha": Check,
        "isdecimal": Check,
        "isdigit": Check,
        "isidentifier": Check,
        "islower": Check,
        "isnumeric": Check,
        "isprintable": Check,
        "isspace": Check,
        "istitle": Check,
        "isupper": Check,
        "isascii": Check,
        "contains": Contains,
    }

    def __init__(self, fields: str, /) -> None:
        self.fields = str(fields)
        self.parent = LoxString

    def __str__(self) -> str:
        return str(self.fields)

    def __repr__(self) -> str:
        return f"LoxString({self.fields!r})"

    def __int__(self) -> int:
        return int(self.fields)

    def __float__(self) -> float:
        return float(self.fields)

    def __bool__(self) -> bool:
        return bool(self.fields)

    def __len__(self) -> int:
        return len(self.fields)

    def __getitem__(self, index: int, /) -> str:
        return self.fields[index]

    def __hash__(self) -> int:
        return hash(self.fields)

    def __eq__(self, other: t.Any) -> bool:
        if isinstance(other, LoxString):
            return self.fields == other.fields
        return False

    def get(self, name: "Token", /) -> t.Any:
        try:
            return super().get(name)
        except PyLoxAttributeError:
            pass
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise PyLoxAttributeError(f"String has no method '{name.lexeme}'.")
