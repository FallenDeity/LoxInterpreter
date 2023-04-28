import inspect
import pathlib
import typing as t

from src.builtins import BuiltInCallable
from src.exceptions import PyLoxBreakError, PyLoxContinueError, PyLoxReturnError, PyLoxRuntimeError, PyLoxTypeError
from src.internals.array import LoxArray
from src.internals.callables import LoxCallable, LoxClass, LoxFunction, LoxInstance
from src.internals.string import LoxString
from src.lexer.tokens import ComplexTokenType, KeywordTokenType, SimpleTokenType, Token
from src.utils.environment import Environment
from src.utils.expr import Block
from src.utils.protocol import StmtProtocol, VisitorProtocol

if t.TYPE_CHECKING:
    from src.logger import Logger
    from src.utils.expr import (
        Assign,
        Binary,
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

    from .lox import PyLox


# pyright: reportUnknownArgumentType=false
__all__: tuple[str, ...] = ("Interpreter",)


class Equals(t.Protocol):
    def __eq__(self, other: t.Any, /) -> bool:
        ...


class Interpreter(VisitorProtocol, StmtProtocol):
    _environment: Environment
    builtins: pathlib.Path = pathlib.Path("src/builtins")

    def __init__(self, lox: "PyLox", logger: "Logger") -> None:
        self._lox = lox
        self._logger = logger
        self._environment = Environment()
        self._locals: t.Dict["Expr", int] = {}
        self._load_builtins()

    def _load_builtins(self) -> None:
        """Load builtins."""
        for file in self.builtins.glob("*.py"):
            self._logger.debug(f"Loading builtin '{file.name}'...")
            methods = inspect.getmembers(__import__(f"src.builtins.{file.stem}", fromlist=["*"]), inspect.isclass)
            for _, method in methods:
                if issubclass(method, BuiltInCallable) and method is not BuiltInCallable:
                    token = Token(KeywordTokenType.FUN, method._short_name, None, 0, 0)
                    self._environment.define(token, method(method._short_name))  # type: ignore

    def error(self, token: "Token", message: str, /) -> str:
        """Raise a runtime error."""
        line = self._lox.lexer._source.splitlines()[token.line - 1]
        error_ = f"\n{line}\n{'~' * token.column}^\n{message}"
        return f"RuntimeError at line {token.line}:{token.column}{error_}"

    @staticmethod
    def is_equal(left: Equals, right: Equals, /) -> bool:
        """Check if two objects are equal."""
        if type(left) != type(right):
            return False
        return left == right

    @staticmethod
    def stringify(obj: t.Any) -> str:
        """Stringify an object."""
        if obj is None:
            return str(KeywordTokenType.NIL)
        if isinstance(obj, bool):
            return str(obj).lower()
        return str(obj)

    @staticmethod
    def is_truthy(obj: t.Any) -> bool:
        """Check if an object is truthy."""
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def _numeric_validation(self, operator: "Token", *operands: t.Any) -> None:
        """Validate numeric operands."""
        for operand in operands:
            if not isinstance(operand, (int, float)):
                raise PyLoxTypeError(
                    self.error(operator, f"Operand must be a number for operator '{operator.lexeme}'.")
                )
        return None

    def interpret(self, statements: list["Stmt"]) -> None:
        """Interpret a list of statements."""
        try:
            for statement in statements:
                self._evaluate(statement)
        except PyLoxRuntimeError as error:
            self._logger.error(str(error))

    @staticmethod
    def _converter(value: t.Any) -> t.Any:
        if isinstance(value, str):
            return LoxString(value)
        elif isinstance(value, list):
            return LoxArray(value)
        return value

    def _evaluate(self, expression: t.Union["Expr", "Stmt"]) -> t.Any:
        """Evaluate an expression."""
        return self._converter(expression.accept(self))

    def _resolve(self, expr: "Expr", depth: int) -> None:
        """Resolve an expression."""
        self._locals[expr] = depth

    def _execute_block(self, statements: list["Stmt"], environment: Environment) -> None:
        """Execute a block of statements."""
        previous: Environment = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self._evaluate(statement)
        finally:
            self._environment = previous

    def _lookup_variable(self, name: "Token", expr: "Expr") -> t.Any:
        """Lookup a variable."""
        distance = self._locals.get(expr)
        if distance is not None:
            return self._environment.get_at(distance, name)
        return self._environment.get(name)

    def visit_block_stmt(self, stmt: "Block") -> None:
        """Visit a block statement."""
        self._execute_block(stmt.statements, Environment(self._environment))

    def visit_class_stmt(self, stmt: "Class") -> None:
        super_class = None
        if stmt.superclass is not None:
            super_class = self._evaluate(stmt.superclass)
            if not isinstance(super_class, LoxClass):
                raise PyLoxRuntimeError(
                    self.error(stmt.name, f"{stmt.superclass.name} must be an instance of LoxClass.")
                )
        self._environment.define(stmt.name, None)
        if stmt.superclass is not None:
            self._environment = Environment(self._environment)
            self._environment.define(Token(KeywordTokenType.SUPER, "super", None, 0, 0), super_class)
        methods: t.Dict[str, LoxFunction] = {}
        for method in stmt.methods:
            function_: LoxFunction = LoxFunction(method, self._environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function_
        new_class: LoxClass = LoxClass(stmt.name.lexeme, super_class, methods)
        if super_class is not None:
            assert isinstance(self._environment.enclosing, Environment)
            self._environment = self._environment.enclosing
        self._environment.assign(stmt.name, new_class)

    def visit_expression_stmt(self, stmt: "Expression") -> None:
        """Visit an expression statement."""
        self._evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: "Function") -> None:
        """Visit a function statement."""
        function_: LoxFunction = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name, function_)

    def visit_lambda_expr(self, expr: "Lambda") -> t.Any:
        """Visit a lambda statement."""
        return LoxFunction(expr, self._environment, False)

    def visit_if_stmt(self, stmt: "If") -> None:
        """Visit an if statement."""
        if self.is_truthy(self._evaluate(stmt.condition)):
            self._evaluate(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._evaluate(stmt.else_branch)

    def visit_try_stmt(self, stmt: "Try") -> t.Any:
        """Visit a try statement."""
        try:
            self._evaluate(stmt.try_block)
        except Exception as error:
            if stmt.catch_block is not None and stmt.error is not None:
                self._environment.define(stmt.error, LoxString(str(error)))
                self._evaluate(stmt.catch_block)
        finally:
            if stmt.finally_block is not None:
                self._evaluate(stmt.finally_block)
        return None

    def visit_print_stmt(self, stmt: "Print") -> None:
        """Visit a print statement."""
        value: t.Any = self._evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt: "Return") -> None:
        """Visit a return statement."""
        value: t.Any = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)
        raise PyLoxReturnError(self.error(stmt.keyword, f"Return {self.stringify(value)}"), value)

    def visit_var_stmt(self, stmt: "Var") -> None:
        """Visit a var statement."""
        value: t.Any = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)
        self._environment.define(stmt.name, value)

    def visit_while_stmt(self, stmt: "While") -> None:
        """Visit a while statement."""
        try:
            while self.is_truthy(self._evaluate(stmt.condition)):
                try:
                    self._evaluate(stmt.body)
                except PyLoxContinueError:
                    if isinstance(stmt.body, Block):
                        self._execute_block([stmt.body.statements[-1]], Environment(self._environment))
                        continue
                    raise PyLoxRuntimeError("Continue must be inside a loop.")
        except PyLoxRuntimeError:
            return

    def visit_break_stmt(self, stmt: "Break") -> t.Any:
        """Visit a break statement."""
        raise PyLoxBreakError(f"Break {self.stringify(None)}")

    def visit_continue_stmt(self, stmt: "Continue") -> t.Any:
        """Visit a continue statement."""
        raise PyLoxContinueError(f"Continue {self.stringify(None)}")

    def visit_for_stmt(self, stmt: "For") -> t.Any:
        raise NotImplementedError

    def visit_literal_expr(self, expr: "Literal") -> t.Any:
        """Visit a literal expression."""
        return expr.value

    def visit_variable_expr(self, expr: "Variable") -> t.Any:
        """Visit a variable expression."""
        return self._lookup_variable(expr.name, expr)

    def visit_grouping_expr(self, expr: "Grouping") -> t.Any:
        """Visit a grouping expression."""
        return self._evaluate(expr.expression)

    def visit_this_expr(self, expr: "This") -> t.Any:
        """Visit a this expression."""
        return self._lookup_variable(expr.keyword, expr)

    def visit_logical_expr(self, expr: "Logical") -> t.Any:
        """Visit a logical expression."""
        left: t.Any = self._evaluate(expr.left)
        if expr.operator.token_type == KeywordTokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self._evaluate(expr.right)

    def visit_set_expr(self, expr: "Set") -> t.Any:
        """Visit a set expression."""
        obj = self._evaluate(expr.object)
        if not isinstance(obj, LoxInstance):
            raise PyLoxRuntimeError(self.error(expr.name, "Only instances have fields."))
        value: t.Any = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_unary_expr(self, expr: "Unary") -> t.Any:
        """Visit a unary expression."""
        right: t.Any = self._evaluate(expr.right)
        match expr.operator.token_type:
            case SimpleTokenType.MINUS:
                self._numeric_validation(expr.operator, right)
                return -right
            case SimpleTokenType.BANG:
                return not self.is_truthy(right)
            case _:
                raise PyLoxRuntimeError(self.error(expr.operator, f"Unknown unary operator {expr.operator.lexeme}."))

    def visit_assign_expr(self, expr: "Assign") -> t.Any:
        """Visit an assign expression."""
        value: t.Any = self._evaluate(expr.value)
        distance: int | None = self._locals.get(expr)
        if distance is not None:
            self._environment.assign_at(distance, expr.token, value)
        else:
            self._environment.assign(expr.token, value)
        return value

    def visit_binary_expr(self, expr: "Binary") -> t.Any:
        """Visit a binary expression."""
        left, right = self._evaluate(expr.left), self._evaluate(expr.right)
        match expr.operator.token_type:
            case SimpleTokenType.MINUS:
                self._numeric_validation(expr.operator, left, right)
                return left - right
            case SimpleTokenType.PLUS:
                if type(left) in (int, float) and type(right) in (int, float):
                    return left + right
                if isinstance(left, LoxString) and isinstance(right, LoxString):
                    return LoxString(str(left) + str(right))
                raise PyLoxRuntimeError(self.error(expr.operator, "Operands must be two numbers or two strings."))
            case SimpleTokenType.SLASH:
                self._numeric_validation(expr.operator, left, right)
                try:
                    return left / right
                except ZeroDivisionError:
                    raise PyLoxRuntimeError(self.error(expr.operator, "Division by zero."))
            case ComplexTokenType.BACKSLASH:
                self._numeric_validation(expr.operator, left, right)
                try:
                    return left // right
                except ZeroDivisionError:
                    raise PyLoxRuntimeError(self.error(expr.operator, "Division by zero."))
            case SimpleTokenType.STAR:
                self._numeric_validation(expr.operator, left, right)
                return left * right
            case SimpleTokenType.MODULO:
                self._numeric_validation(expr.operator, left, right)
                return left % right
            case SimpleTokenType.CARAT:
                self._numeric_validation(expr.operator, left, right)
                return left**right
            case ComplexTokenType.GREATER:
                self._numeric_validation(expr.operator, left, right)
                return left > right
            case ComplexTokenType.GREATER_EQUAL:
                self._numeric_validation(expr.operator, left, right)
                return left >= right
            case ComplexTokenType.LESS:
                self._numeric_validation(expr.operator, left, right)
                return left < right
            case ComplexTokenType.LESS_EQUAL:
                self._numeric_validation(expr.operator, left, right)
                return left <= right
            case ComplexTokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case ComplexTokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case _:
                raise PyLoxRuntimeError(
                    self.error(expr.operator, f"Unexpected binary operator {expr.operator.lexeme}.")
                )

    def visit_call_expr(self, expr: "Call") -> t.Any:
        """Visit a call expression."""
        callee: t.Any = self._evaluate(expr.callee)
        arguments: t.List[t.Any] = [self._evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise PyLoxRuntimeError(self.error(expr.paren, "Can only call functions and classes."))
        if len(arguments) != callee.arity:
            raise PyLoxRuntimeError(
                self.error(expr.paren, f"Expected {callee.arity} arguments but got {len(arguments)}")
            )
        try:
            return callee(self, arguments)
        except Exception as e:
            self._logger.error(f"Error while calling function {expr.paren.line}:{expr.paren.column}: \n{e}")
            raise PyLoxRuntimeError(
                self.error(expr.paren, f"Error while calling function {expr.paren.line}:{expr.paren.column}: \n{e}")
            )

    def visit_get_expr(self, expr: "Get") -> t.Any:
        """Visit a get expression."""
        obj: t.Any = self._evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise PyLoxRuntimeError(self.error(expr.name, "Only instances have properties."))

    def visit_super_expr(self, expr: "Super") -> t.Any:
        """Visit a super expression."""
        distance: int = self._locals.get(expr, 0)
        superclass: LoxClass = self._environment.get_at(distance, "super")
        obj: LoxInstance = self._environment.get_at(distance - 1, "this")
        method: LoxFunction | None = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise PyLoxRuntimeError(self.error(expr.method, f"Undefined property {expr.method.lexeme}."))
        return method.bind(obj)

    def visit_throw_stmt(self, stmt: "Throw") -> t.Any:
        """Visit a throw statement."""
        raise PyLoxRuntimeError(self.error(stmt.keyword, self._evaluate(stmt.value)))
