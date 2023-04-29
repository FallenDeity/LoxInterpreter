import dataclasses
import typing as t

import requests

from src.exceptions import PyLoxAttributeError, PyLoxRuntimeError

from .callables import LoxCallable
from .types import LoxContainer

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = ("LoxRequest",)


# pyright: reportIncompatibleVariableOverride=false


@dataclasses.dataclass
class RequestCallable(LoxCallable):
    parent: "LoxRequest"
    token: "Token"

    @property
    def arity(self) -> int:
        raise NotImplementedError

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        raise NotImplementedError


class LoxRequestModel(LoxContainer):
    parent: t.Type["LoxRequestModel"]

    def __init__(self, fields: requests.models.Response, /) -> None:
        self.parent = LoxRequestModel
        try:
            self.fields = fields.json()
        except ValueError:
            self.fields = {}
        for key in dir(fields):
            if not key.startswith("_") and not callable(getattr(fields, key)):
                self.fields[key] = getattr(fields, key)


@dataclasses.dataclass
class Get(RequestCallable):
    parent: "LoxRequest"
    token: "Token"

    @property
    def arity(self) -> int:
        return 1

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> LoxRequestModel:
        try:
            return LoxRequestModel(requests.get(str(arguments[0])))
        except requests.exceptions.RequestException as e:
            raise PyLoxRuntimeError(interpreter.error(self.token, f"Request failed: {e}"))


class LoxRequest(LoxContainer):
    parent: t.Type["LoxRequest"]
    fields: t.Optional[dict[str, t.Any]] = None
    _methods: dict[str, t.Type[RequestCallable]] = {
        "get": Get,
    }

    def __init__(self, /) -> None:
        self.parent = LoxRequest

    def get(self, name: "Token", /) -> t.Any:
        try:
            return self._methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise PyLoxAttributeError(f"Attribute {name.lexeme} not found.")
