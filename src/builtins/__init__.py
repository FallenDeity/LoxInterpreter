import dataclasses
import typing as t

from src.internals.callables import LoxCallable

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter


@dataclasses.dataclass
class BuiltInCallable(LoxCallable):
    _short_name: str

    def __str__(self) -> str:
        return f"<Built-in function '{self._short_name}'>"

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        raise NotImplementedError

    @property
    def arity(self) -> int:
        raise NotImplementedError
