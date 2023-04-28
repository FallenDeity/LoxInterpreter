import enum
import typing as t

from src.exceptions import PyLoxResolutionError
from src.utils.protocol import StmtProtocol, VisitorProtocol

if t.TYPE_CHECKING:
    from src.lexer.tokens import Token
    from src.utils.expr import (
        Assign,
        Binary,
        Block,
        Break,
        Call,
        Class,
        Continue,
        Expr,
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
        Stmt,
        Super,
        This,
        Throw,
        Try,
        Unary,
        Var,
        Variable,
        While,
    )

    from .interpreter import Interpreter


class FunctionType(enum.Enum):
    NONE = enum.auto()
    FUNCTION = enum.auto()
    INITIALIZER = enum.auto()
    METHOD = enum.auto()


class ClassType(enum.Enum):
    NONE = enum.auto()
    CLASS = enum.auto()
    SUBCLASS = enum.auto()


class LoopyType(enum.Enum):
    NONE = enum.auto()
    WHILE = enum.auto()


__all__: tuple[str, ...] = ("Resolver",)


class Resolver(StmtProtocol, VisitorProtocol):
    def __init__(self, interpreter: "Interpreter") -> None:
        self._interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function: FunctionType = FunctionType.NONE
        self.current_class: ClassType = ClassType.NONE
        self.current_loop: LoopyType = LoopyType.NONE

    def _begin_scope(self) -> None:
        self.scopes.append({})

    def _end_scope(self) -> None:
        self.scopes.pop()

    def _resolve_one(self, expr: t.Union["Stmt", "Expr"]) -> None:
        expr.accept(self)

    def _resolve(self, statements: t.Sequence[t.Union["Stmt", "Expr"]]) -> None:
        try:
            for statement in statements:
                self._resolve_one(statement)
        except PyLoxResolutionError as e:
            self._interpreter._logger.error(e)
            raise e

    def _resolve_local(self, expr: "Expr", name: "Token") -> None:
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self._interpreter._resolve(expr, i)
                return

    def _resolve_function(self, function: t.Union["Function", "Lambda"], type_: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = type_

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)

        self._resolve(function.body)
        self._end_scope()

        self.current_function = enclosing_function

    def _declare(self, name: "Token") -> None:
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise PyLoxResolutionError(
                self._interpreter.error(name, f"Variable '{name.lexeme}' already declared in this scope.")
            )
        scope[name.lexeme] = False

    def _define(self, name: "Token") -> None:
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def visit_block_stmt(self, stmt: "Block") -> t.Any:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()
        return None

    def visit_class_stmt(self, stmt: "Class") -> t.Any:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self._declare(stmt.name)
        self._define(stmt.name)
        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                raise PyLoxResolutionError(
                    self._interpreter.error(stmt.superclass.name, "A class cannot inherit from itself.")
                )
            self._resolve_one(stmt.superclass)
            self._begin_scope()
            self.scopes[-1]["super"] = True
        self._begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self._resolve_function(method, declaration)
        self._end_scope()
        if stmt.superclass is not None:
            self._end_scope()
        self.current_class = enclosing_class
        return None

    def visit_var_stmt(self, stmt: "Var") -> t.Any:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve_one(stmt.initializer)
        self._define(stmt.name)
        return None

    def visit_variable_expr(self, expr: "Variable") -> t.Any:
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            raise PyLoxResolutionError(
                self._interpreter.error(expr.name, "Cannot read local variable in its own initializer.")
            )
        self._resolve_local(expr, expr.name)
        return None

    def visit_assign_expr(self, expr: "Assign") -> t.Any:
        self._resolve_one(expr.value)
        self._resolve_local(expr, expr.token)
        return None

    def visit_function_stmt(self, stmt: "Function") -> t.Any:
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def visit_lambda_expr(self, expr: "Lambda") -> t.Any:
        self._resolve_function(expr, FunctionType.FUNCTION)
        return None

    def visit_expression_stmt(self, stmt: "Expression") -> t.Any:
        self._resolve_one(stmt.expression)
        return None

    def visit_if_stmt(self, stmt: "If") -> t.Any:
        self._resolve_one(stmt.condition)
        self._resolve_one(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve_one(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: "Print") -> t.Any:
        self._resolve_one(stmt.expression)
        return None

    def visit_throw_stmt(self, stmt: "Throw") -> t.Any:
        self._resolve_one(stmt.value)
        return None

    def visit_return_stmt(self, stmt: "Return") -> t.Any:
        if self.current_function == FunctionType.NONE:
            raise PyLoxResolutionError(self._interpreter.error(stmt.keyword, "Cannot return from top-level code."))
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                raise PyLoxResolutionError(
                    self._interpreter.error(stmt.keyword, "Cannot return a value from an initializer.")
                )
            self._resolve_one(stmt.value)
        return None

    def visit_while_stmt(self, stmt: "While") -> t.Any:
        enclosing_loop = self.current_loop
        self.current_loop = LoopyType.WHILE
        self._resolve_one(stmt.condition)
        self._resolve_one(stmt.body)
        self.current_loop = enclosing_loop
        return None

    def visit_try_stmt(self, stmt: "Try") -> t.Any:
        self._resolve_one(stmt.try_block)
        if stmt.catch_block is not None:
            self._resolve_one(stmt.catch_block)
        if stmt.finally_block is not None:
            self._resolve_one(stmt.finally_block)
        return None

    def visit_break_stmt(self, stmt: "Break") -> t.Any:
        if self.current_loop == LoopyType.NONE:
            raise PyLoxResolutionError(self._interpreter.error(stmt.keyword, "Cannot break outside of a loop."))
        return None

    def visit_continue_stmt(self, stmt: "Continue") -> t.Any:
        if self.current_loop == LoopyType.NONE:
            raise PyLoxResolutionError(self._interpreter.error(stmt.keyword, "Cannot continue outside of a loop."))
        return None

    def visit_binary_expr(self, expr: "Binary") -> t.Any:
        self._resolve_one(expr.left)
        self._resolve_one(expr.right)
        return None

    def visit_call_expr(self, expr: "Call") -> t.Any:
        self._resolve_one(expr.callee)
        for argument in expr.arguments:
            self._resolve_one(argument)
        return None

    def visit_get_expr(self, expr: "Get") -> t.Any:
        self._resolve_one(expr.object)
        return None

    def visit_grouping_expr(self, expr: "Grouping") -> t.Any:
        self._resolve_one(expr.expression)
        return None

    def visit_literal_expr(self, expr: "Literal") -> t.Any:
        return None

    def visit_logical_expr(self, expr: "Logical") -> t.Any:
        self._resolve_one(expr.left)
        self._resolve_one(expr.right)
        return None

    def visit_set_expr(self, expr: "Set") -> t.Any:
        self._resolve_one(expr.value)
        self._resolve_one(expr.object)
        return None

    def visit_super_expr(self, expr: "Super") -> t.Any:
        if self.current_class == ClassType.NONE:
            raise PyLoxResolutionError(self._interpreter.error(expr.keyword, "Cannot use 'super' outside of a class."))
        elif self.current_class != ClassType.SUBCLASS:
            raise PyLoxResolutionError(
                self._interpreter.error(expr.keyword, "Cannot use 'super' in a class with no superclass.")
            )
        self._resolve_local(expr, expr.keyword)
        return None

    def visit_this_expr(self, expr: "This") -> t.Any:
        if self.current_class == ClassType.NONE:
            raise PyLoxResolutionError(self._interpreter.error(expr.keyword, "Cannot use 'this' outside of a class."))
        self._resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: "Unary") -> t.Any:
        self._resolve_one(expr.right)
        return None

    def visit_for_stmt(self, stmt: "For") -> t.Any:
        ...
