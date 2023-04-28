import dataclasses
import typing as t
from abc import ABC, abstractmethod

from .protocol import StmtProtocol, VisitorProtocol

if t.TYPE_CHECKING:
    from src.lexer.tokens import Token


__all__: tuple[str, ...] = (
    "Expr",
    "Stmt",
    "Assign",
    "Binary",
    "Call",
    "Get",
    "Grouping",
    "Literal",
    "Logical",
    "Set",
    "Super",
    "This",
    "Unary",
    "Variable",
    "Block",
    "Expression",
    "Function",
    "For",
    "If",
    "Lambda",
    "Print",
    "Return",
    "While",
    "Class",
    "Assign",
    "Break",
    "Continue",
    "Var",
    "Throw",
    "Try",
)


class Expr(ABC):
    """Base class for expressions."""

    @abstractmethod
    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        raise NotImplementedError


class Stmt(ABC):
    """Base class for statements."""

    @abstractmethod
    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class Assign(Expr):
    """An assignment expression."""

    token: "Token"
    value: Expr

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_assign_expr(self)


@dataclasses.dataclass(frozen=True)
class Binary(Expr):
    """A binary expression."""

    left: Expr
    operator: "Token"
    right: Expr

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_binary_expr(self)


@dataclasses.dataclass(frozen=True)
class Call(Expr):
    """A call expression."""

    callee: Expr
    paren: "Token"
    arguments: list[Expr]

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_call_expr(self)


@dataclasses.dataclass(frozen=True)
class Get(Expr):
    """A get expression."""

    object: Expr
    name: "Token"

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_get_expr(self)


@dataclasses.dataclass(frozen=True)
class Grouping(Expr):
    """A grouping expression."""

    expression: Expr

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_grouping_expr(self)


@dataclasses.dataclass(frozen=True)
class Literal(Expr):
    """A literal expression."""

    value: t.Any

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_literal_expr(self)


@dataclasses.dataclass(frozen=True)
class Logical(Expr):
    """A logical expression."""

    left: Expr
    operator: "Token"
    right: Expr

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_logical_expr(self)


@dataclasses.dataclass(frozen=True)
class Set(Expr):
    """A set expression."""

    object: Expr
    name: "Token"
    value: Expr

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_set_expr(self)


@dataclasses.dataclass(frozen=True)
class Super(Expr):
    """A super expression."""

    keyword: "Token"
    method: "Token"

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_super_expr(self)


@dataclasses.dataclass(frozen=True)
class This(Expr):
    """A this expression."""

    keyword: "Token"

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_this_expr(self)


@dataclasses.dataclass(frozen=True)
class Unary(Expr):
    """A unary expression."""

    operator: "Token"
    right: Expr

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_unary_expr(self)


@dataclasses.dataclass(frozen=True)
class Variable(Expr):
    """A variable expression."""

    name: "Token"

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_variable_expr(self)


@dataclasses.dataclass(frozen=True)
class Block(Stmt):
    """A block expression."""

    statements: list[Stmt]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_block_stmt(self)


@dataclasses.dataclass(frozen=True)
class Break(Stmt):
    """A break statement."""

    keyword: "Token"

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_break_stmt(self)


@dataclasses.dataclass(frozen=True)
class Class(Stmt):
    """A class expression."""

    name: "Token"
    superclass: t.Optional[Variable]
    methods: list["Function"]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_class_stmt(self)


@dataclasses.dataclass(frozen=True)
class Continue(Stmt):
    """A continue statement."""

    keyword: "Token"

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_continue_stmt(self)


@dataclasses.dataclass(frozen=True)
class Expression(Stmt):
    """An expression statement."""

    expression: Expr

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_expression_stmt(self)


@dataclasses.dataclass(frozen=True)
class For(Stmt):
    """A for statement."""

    initializer: t.Optional[Expr]
    condition: t.Optional[Expr]
    increment: t.Optional[Expr]
    body: Stmt

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_for_stmt(self)


@dataclasses.dataclass(frozen=True)
class Function(Stmt):
    """A function expression."""

    name: "Token"
    params: list["Token"]
    body: list[Stmt]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_function_stmt(self)


@dataclasses.dataclass(frozen=True)
class If(Stmt):
    """An if expression."""

    condition: Expr
    then_branch: Stmt
    else_branch: t.Optional[Stmt]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_if_stmt(self)


@dataclasses.dataclass(frozen=True)
class Lambda(Expr):
    """A lambda expression."""

    params: list["Token"]
    body: list[Stmt]

    def accept(self, visitor: VisitorProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_lambda_expr(self)


@dataclasses.dataclass(frozen=True)
class Print(Stmt):
    """A print statement."""

    expression: Expr

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_print_stmt(self)


@dataclasses.dataclass(frozen=True)
class Return(Stmt):
    """A return statement."""

    keyword: "Token"
    value: t.Optional[Expr]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_return_stmt(self)


@dataclasses.dataclass(frozen=True)
class Throw(Stmt):
    """A throw statement."""

    keyword: "Token"
    value: Expr

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_throw_stmt(self)


@dataclasses.dataclass(frozen=True)
class Var(Stmt):
    """A variable expression."""

    name: "Token"
    initializer: t.Optional[Expr]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_var_stmt(self)


@dataclasses.dataclass(frozen=True)
class While(Stmt):
    """A while statement."""

    condition: Expr
    body: Stmt

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_while_stmt(self)


@dataclasses.dataclass(frozen=True)
class Try(Stmt):
    """A try statement."""

    error: t.Optional["Token"]
    try_block: Stmt
    catch_block: t.Optional[Stmt]
    finally_block: t.Optional[Stmt]

    def accept(self, visitor: StmtProtocol, /) -> t.Any:
        """Accept a visitor."""
        return visitor.visit_try_stmt(self)
