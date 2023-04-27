import typing as t

from .protocol import VisitorProtocol

if t.TYPE_CHECKING:
    from .expr import Assign, Binary, Call, Expr, Get, Grouping, Literal, Logical, Set, Super, This, Unary, Variable


__all__: tuple[str, ...] = ("AstPrinter",)


class AstPrinter(VisitorProtocol):
    def _parenthesize(self, name: str, *exprs: "Expr") -> str:
        """Parenthesize the expressions."""
        builder = [name] + [expr.accept(self) for expr in exprs]
        return f"({' '.join(builder)})"

    def print(self, expr: "Expr") -> str:
        """Print the expression."""
        return expr.accept(self)

    def visit_binary_expr(self, expr: "Binary") -> str:
        """Visit a binary expression."""
        return self._parenthesize(expr.operator.token_type, expr.left, expr.right)

    def visit_grouping_expr(self, expr: "Grouping") -> str:
        """Visit a grouping expression."""
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: "Literal") -> str:
        """Visit a literal expression."""
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: "Unary") -> str:
        """Visit a unary expression."""
        return self._parenthesize(expr.operator.token_type, expr.right)

    def visit_variable_expr(self, expr: "Variable") -> str:
        """Visit a variable expression."""
        return self._parenthesize(expr.name.lexeme)

    def visit_assign_expr(self, expr: "Assign") -> str:
        """Visit an assign expression."""
        return self._parenthesize(expr.token.lexeme, expr.value)

    def visit_call_expr(self, expr: "Call") -> str:
        """Visit a call expression."""
        return self._parenthesize(expr.paren.lexeme, expr.callee, *expr.arguments)

    def visit_get_expr(self, expr: "Get") -> str:
        """Visit a get expression."""
        return self._parenthesize(expr.name.lexeme, expr.object)

    def visit_logical_expr(self, expr: "Logical") -> str:
        """Visit a logical expression."""
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_set_expr(self, expr: "Set") -> str:
        """Visit a set expression."""
        return self._parenthesize(expr.name.lexeme, expr.object, expr.value)

    def visit_this_expr(self, expr: "This") -> str:
        """Visit a this expression."""
        return self._parenthesize(expr.keyword.lexeme)

    def visit_super_expr(self, expr: "Super") -> str:
        """Visit a super expression."""
        return self._parenthesize(f"{expr.keyword.lexeme}.{expr.method.lexeme}")
