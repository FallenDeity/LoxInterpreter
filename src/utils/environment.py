import dataclasses
import typing as t

from src.exceptions import PyLoxRuntimeError

if t.TYPE_CHECKING:
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = ("Environment",)


@dataclasses.dataclass
class Environment:
    enclosing: t.Optional["Environment"] = None
    values: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)

    def define(self, name: "Token", value: t.Any, /) -> None:
        """Define a variable in the environment."""
        self.values[name.lexeme] = value

    def assign(self, name: "Token", value: t.Any, /) -> None:
        """Assign a variable in the environment."""
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise PyLoxRuntimeError(f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: "Token", value: t.Any, /) -> None:
        """Assign a variable in the environment at a given distance."""
        self.ancestor(distance).values[name.lexeme] = value

    def get(self, name: "Token", /) -> t.Any:
        """Get a variable from the environment."""
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise PyLoxRuntimeError(f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: t.Union[str, "Token"], /) -> t.Any:
        """Get a variable from the environment at a given distance."""
        if isinstance(name, str):
            return self.ancestor(distance).values[name]
        return self.ancestor(distance).values[name.lexeme]

    def ancestor(self, distance: int, /) -> "Environment":
        """Get the ancestor of the environment at a given distance."""
        environment: "Environment" = self
        for _ in range(distance):
            assert environment.enclosing is not None
            environment = environment.enclosing
        return environment
