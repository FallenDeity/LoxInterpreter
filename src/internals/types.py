import dataclasses
import typing as t

from src.exceptions import PyLoxAttributeError, PyLoxIndexError

from .callables import LoxCallable, LoxInstance

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = (
    "LoxContainer",
    "GetContainer",
    "SetContainer",
)


@dataclasses.dataclass
class SetContainer(LoxCallable):
    parent: "LoxContainer"
    token: "Token"

    @property
    def arity(self) -> int:
        return 2

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        idx, value = arguments
        try:
            self.parent.fields[idx] = value
        except IndexError:
            raise PyLoxIndexError(interpreter.error(self.token, "Index out of range."))


@dataclasses.dataclass
class GetContainer(LoxCallable):
    parent: "LoxContainer"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        try:
            return self.parent.fields[arguments[0]]
        except IndexError:
            raise PyLoxIndexError(interpreter.error(self.token, "Index out of range."))


@dataclasses.dataclass
class LoxContainer(LoxInstance):
    def __len__(self) -> int:
        return len(self.fields)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.fields})"

    def get(self, name: "Token", /) -> t.Any:
        match name.lexeme:
            case "get":
                return GetContainer(self, name)
            case "set":
                return SetContainer(self, name)
            case _:
                raise PyLoxAttributeError(f"Unknown attribute '{name.lexeme}'.")

    def set(self, name: "Token", value: t.Any, /) -> None:
        raise PyLoxAttributeError(f"Cannot set attribute '{name.lexeme}' on {self.__class__.__name__}.")
