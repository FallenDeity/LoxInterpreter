import dataclasses
import typing as t
from abc import ABC, abstractmethod

from src.exceptions import PyLoxReturnError, PyLoxRuntimeError
from src.lexer.tokens import KeywordTokenType, Token
from src.utils.environment import Environment

if t.TYPE_CHECKING:
    from src.interpreter.interpreter import Interpreter
    from src.utils.expr import Function


__all__: tuple[str, ...] = (
    "LoxCallable",
    "LoxFunction",
    "LoxClass",
    "LoxInstance",
)


@dataclasses.dataclass
class LoxCallable(ABC):
    """Base class for callables."""

    @property
    @abstractmethod
    def arity(self) -> int:
        """Get the arity of the callable. (The number of arguments it takes.)"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        """Call the callable."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at {hex(id(self))}>"


@dataclasses.dataclass
class LoxFunction(LoxCallable):
    declaration: "Function"
    closure: Environment
    is_initializer: bool = False

    @property
    def arity(self) -> int:
        return len(self.declaration.params)

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> t.Any:
        environment = Environment(self.closure)
        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param, argument)
        try:
            interpreter._execute_block(self.declaration.body, environment)
        except PyLoxReturnError as e:
            if self.is_initializer:
                return self.closure.get_at(0, str(KeywordTokenType.THIS))
            return e.value
        if self.is_initializer:
            return self.closure.get_at(0, str(KeywordTokenType.THIS))

    def bind(self, instance: "LoxInstance", /) -> "LoxFunction":
        environment = Environment(self.closure)
        environment.define(Token(KeywordTokenType.THIS, "this", None, 0, 0), instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)


@dataclasses.dataclass
class LoxClass(LoxCallable):
    name: str
    superclass: t.Optional["LoxClass"]
    methods: t.Dict[str, LoxFunction]

    @property
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity
        return 0

    def __call__(self, interpreter: "Interpreter", arguments: list[t.Any], /) -> "LoxInstance":
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance)(interpreter, arguments)
        return instance

    def find_method(self, name: str, /) -> t.Optional[LoxFunction]:
        return self.methods.get(name) or self.superclass and self.superclass.find_method(name)


@dataclasses.dataclass
class LoxInstance:
    parent: LoxClass
    fields: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)

    def get(self, name: Token, /) -> t.Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.parent.find_method(name.lexeme)
        if method:
            return method.bind(self)
        raise PyLoxRuntimeError(f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: t.Any, /) -> None:
        self.fields[name.lexeme] = value

    def __repr__(self) -> str:
        return f"<{self.parent.name} instance at {hex(id(self))}>"
