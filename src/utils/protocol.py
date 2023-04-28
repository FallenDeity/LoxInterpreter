import typing as t
from abc import abstractmethod

if t.TYPE_CHECKING:
    from src.utils.expr import (
        Assign,
        Binary,
        Block,
        Break,
        Call,
        Class,
        Continue,
        Expression,
        For,
        Function,
        Get,
        Grouping,
        If,
        Lambda,
        Literal,
        Logical,
        Print,
        Return,
        Set,
        Super,
        This,
        Unary,
        Var,
        Variable,
        While,
    )


__all__: tuple[str, ...] = ("VisitorProtocol", "StmtProtocol")


class VisitorProtocol(t.Protocol):
    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> t.Any:
        ...

    @abstractmethod
    def visit_grouping_expr(self, expr: "Grouping") -> t.Any:
        ...

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> t.Any:
        ...

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> t.Any:
        ...

    @abstractmethod
    def visit_variable_expr(self, expr: "Variable") -> t.Any:
        ...

    @abstractmethod
    def visit_assign_expr(self, expr: "Assign") -> t.Any:
        ...

    @abstractmethod
    def visit_call_expr(self, expr: "Call") -> t.Any:
        ...

    @abstractmethod
    def visit_get_expr(self, expr: "Get") -> t.Any:
        ...

    @abstractmethod
    def visit_logical_expr(self, expr: "Logical") -> t.Any:
        ...

    @abstractmethod
    def visit_set_expr(self, expr: "Set") -> t.Any:
        ...

    @abstractmethod
    def visit_this_expr(self, expr: "This") -> t.Any:
        ...

    @abstractmethod
    def visit_super_expr(self, expr: "Super") -> t.Any:
        ...

    @abstractmethod
    def visit_lambda_expr(self, expr: "Lambda") -> t.Any:
        ...


class StmtProtocol(t.Protocol):
    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> t.Any:
        ...

    @abstractmethod
    def visit_break_stmt(self, stmt: "Break") -> t.Any:
        ...

    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> t.Any:
        ...

    @abstractmethod
    def visit_function_stmt(self, stmt: "Function") -> t.Any:
        ...

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> t.Any:
        ...

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> t.Any:
        ...

    @abstractmethod
    def visit_return_stmt(self, stmt: "Return") -> t.Any:
        ...

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> t.Any:
        ...

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> t.Any:
        ...

    @abstractmethod
    def visit_class_stmt(self, stmt: "Class") -> t.Any:
        ...

    @abstractmethod
    def visit_continue_stmt(self, stmt: "Continue") -> t.Any:
        ...

    @abstractmethod
    def visit_for_stmt(self, stmt: "For") -> t.Any:
        ...
