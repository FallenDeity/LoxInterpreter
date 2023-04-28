import typing as t

from src.exceptions import PyLoxParseError
from src.lexer.tokens import ComplexTokenType, EOFTokenType, KeywordTokenType, LiteralTokenType, SimpleTokenType
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
    Function,
    Get,
    Grouping,
    If,
    Literal,
    Logical,
    Print,
    Return,
    Set,
    Stmt,
    Super,
    This,
    Unary,
    Var,
    Variable,
    While,
)

if t.TYPE_CHECKING:
    from src.lexer.tokens import Token, TokenType
    from src.logger import Logger


__all__: tuple[str, ...] = ("Parser",)


class Parser:
    def __init__(self, tokens: list["Token"], logger: "Logger", source: str, debug: bool = True) -> None:
        self._tokens = tokens
        self._current = 0
        self._logger = logger
        self._debug = debug
        self._source = source
        self._has_error = False

    def parse(self) -> list["Stmt"]:
        """Parse the tokens."""
        statements: list["Stmt"] = []
        while not self._is_at_end():
            if (decl := self._declaration()) is not None:
                statements.append(decl)
        return statements

    def _previous(self) -> "Token":
        """Get the previous token."""
        return self._tokens[self._current - 1]

    def _peek(self) -> "Token":
        """Get the current token."""
        return self._tokens[self._current]

    def _is_at_end(self) -> bool:
        """Check if the parser is at the end of the tokens."""
        return isinstance(self._peek().token_type, EOFTokenType)

    def _advance(self) -> "Token":
        """Advance the parser."""
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _check(self, token_type: "TokenType") -> bool:
        """Check if the current token is of a certain type."""
        if self._is_at_end():
            return False
        return self._peek().token_type == token_type

    def _match(self, *token_types: "TokenType") -> bool:
        """Check if the current token is of any of the given types."""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _error(self, token: "Token", error: str, message: str) -> None:
        line = self._source.splitlines()[token.line - 1]
        if not self._debug:
            self._logger.error(f"{error}\n{message}\n{line}\n{'~' * (token.column - 1)}^")
        raise PyLoxParseError(f"{error}\n{message}\n{line}\n{'~' * (token.column - 1)}^")

    def _consume(self, token_type: "TokenType", message: str) -> "Token":  # type: ignore
        """Consume a token."""
        token = self._previous()
        if self._check(token_type):
            return self._advance()
        error = f"Expected {str(token_type)} but got {str(token.token_type)} in {token.line}:{token.column}"
        self._error(token, error, message)

    def _synchronize(self) -> None:
        """Synchronize the parser."""
        self._advance()
        while not self._is_at_end():
            if self._previous().token_type == SimpleTokenType.SEMICOLON:
                return
            if self._peek().token_type in (
                KeywordTokenType.CLASS,
                KeywordTokenType.FUN,
                KeywordTokenType.VAR,
                KeywordTokenType.FOR,
                KeywordTokenType.IF,
                KeywordTokenType.WHILE,
                KeywordTokenType.PRINT,
                KeywordTokenType.RETURN,
            ):
                return
            self._advance()

    def _block(self) -> list[Stmt]:
        """Parse a block."""
        statements: list[Stmt] = []
        while not self._check(SimpleTokenType.RIGHT_BRACE) and not self._is_at_end():
            if (decl := self._declaration()) is not None:
                statements.append(decl)
        self._consume(SimpleTokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def _declaration(self) -> Stmt | None:
        """Parse a declaration."""
        try:
            if self._match(KeywordTokenType.VAR):
                return self._var_declaration()
            elif self._match(KeywordTokenType.FUN):
                return self._function_declaration("function")
            elif self._match(KeywordTokenType.CLASS):
                return self._class_declaration()
            return self._statement()
        except PyLoxParseError as e:
            if self._debug:
                self._error(self._peek(), "Parse Error", str(e))
            self._has_error = True
            self._synchronize()
            return None

    def _class_declaration(self) -> Class:
        """
        Parse a class declaration.
        :return: The parsed data
        """
        name = self._consume(LiteralTokenType.IDENTIFIER, "Expected class name.")
        super_class = None
        if self._match(ComplexTokenType.LESS):
            self._consume(LiteralTokenType.IDENTIFIER, "Expected superclass name.")
            super_class = Variable(self._previous())
        self._consume(SimpleTokenType.LEFT_BRACE, "Expected '{' before class body.")
        methods: list[Function] = []
        while not self._check(SimpleTokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function_declaration("method"))
        self._consume(SimpleTokenType.RIGHT_BRACE, "Expected '}' after class body.")
        return Class(name, super_class, methods)

    def _function_declaration(self, kind: str) -> Function:
        """
        Parse a function declaration.
        :param kind: The kind of function
        :return: The parsed data
        """
        name = self._consume(LiteralTokenType.IDENTIFIER, f"Expected {kind} name.")
        self._consume(SimpleTokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters: list["Token"] = []
        if not self._check(SimpleTokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self._error(
                        self._peek(), "Parse Error", f"Cannot have more than 255 parameters in {kind} {name.lexeme}"
                    )
                parameters.append(self._consume(LiteralTokenType.IDENTIFIER, "Expected parameter name."))
                if not self._match(SimpleTokenType.COMMA):
                    break
        self._consume(SimpleTokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self._consume(SimpleTokenType.LEFT_BRACE, f"Expected '{' before {kind} body.")
        body = self._block()
        return Function(name, parameters, body)

    def _var_declaration(self) -> Var:
        """
        Parse a variable declaration.
        :return: The parsed data
        """
        name = self._consume(LiteralTokenType.IDENTIFIER, "Expected variable name.")
        initializer = None
        if self._match(ComplexTokenType.EQUAL):
            initializer = self._assignment()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)

    def _statement(self) -> Stmt:
        """
        Parse a statement.
        :return: The parsed data
        """
        if self._match(KeywordTokenType.FOR):
            return self._for_statement()
        elif self._match(KeywordTokenType.IF):
            return self._if_statement()
        elif self._match(KeywordTokenType.PRINT):
            return self._print_statement()
        elif self._match(KeywordTokenType.RETURN):
            return self._return_statement()
        elif self._match(KeywordTokenType.WHILE):
            return self._while_statement()
        elif self._match(KeywordTokenType.BREAK):
            return self._break_statement()
        elif self._match(KeywordTokenType.CONTINUE):
            return self._continue_statement()
        elif self._match(SimpleTokenType.LEFT_BRACE):
            return Block(self._block())
        return self._expression_statement()

    def _for_statement(self) -> Stmt:
        """
        Parse a for statement.
        :return: The parsed data
        """
        self._consume(SimpleTokenType.LEFT_PAREN, "Expected '(' after 'for'.")
        if self._match(SimpleTokenType.SEMICOLON):
            initializer = None
        elif self._match(KeywordTokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()
        condition = None
        if not self._check(SimpleTokenType.SEMICOLON):
            condition = self._assignment()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after loop condition.")
        increment = None
        if not self._check(SimpleTokenType.RIGHT_PAREN):
            increment = self._assignment()
        self._consume(SimpleTokenType.RIGHT_PAREN, "Expected ')' after for clauses.")
        body = self._statement()
        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def _if_statement(self) -> Stmt:
        """
        Parse an if statement.
        :return: The parsed data
        """
        self._consume(SimpleTokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self._assignment()
        self._consume(SimpleTokenType.RIGHT_PAREN, "Expected ')' after if condition.")
        then_branch = self._statement()
        else_branch = None
        if self._match(KeywordTokenType.ELSE):
            else_branch = self._statement()
        return If(condition, then_branch, else_branch)

    def _print_statement(self) -> Stmt:
        """
        Parse a print statement.
        :return: The parsed data
        """
        value = self._assignment()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def _return_statement(self) -> Stmt:
        """
        Parse a return statement.
        :return: The parsed data
        """
        keyword = self._previous()
        value = None
        if not self._check(SimpleTokenType.SEMICOLON):
            value = self._assignment()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after return value.")
        return Return(keyword, value)

    def _while_statement(self) -> Stmt:
        """
        Parse a while statement.
        :return: The parsed data
        """
        self._consume(SimpleTokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self._assignment()
        self._consume(SimpleTokenType.RIGHT_PAREN, "Expected ')' after condition.")
        body = self._statement()
        return While(condition, body)

    def _break_statement(self) -> Stmt:
        """
        Parse a break statement.
        :return: The parsed data
        """
        keyword = self._previous()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after 'break'.")
        return Break(keyword)

    def _continue_statement(self) -> Stmt:
        """
        Parse a continue statement.
        :return: The parsed data
        """
        keyword = self._previous()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after 'continue'.")
        return Continue(keyword)

    def _expression_statement(self) -> Stmt:
        """
        Parse an expression statement.
        :return: The parsed data
        """
        expr = self._assignment()
        self._consume(SimpleTokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)

    def _assignment(self) -> Expr:
        """
        Parse an assignment.
        :return: The parsed data
        """
        expr = self._or()
        if self._match(ComplexTokenType.EQUAL):
            value = self._assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            self._error(self._previous(), "Invalid assignment target.", "Cannot assign to this expression.")
        return expr

    def _or(self) -> Expr:
        """
        Parse an or expression.
        :return: The parsed data
        """
        expr = self._and()
        while self._match(KeywordTokenType.OR):
            operator, right = self._previous(), self._and()
            expr = Logical(expr, operator, right)
        return expr

    def _and(self) -> Expr:
        """
        Parse an and expression.
        :return: The parsed data
        """
        expr = self._equality()
        while self._match(KeywordTokenType.AND):
            operator, right = self._previous(), self._equality()
            expr = Logical(expr, operator, right)
        return expr

    def _equality(self) -> Expr:
        """
        Parse an equality expression.
        :return: The parsed data
        """
        expr = self._comparison()
        while self._match(ComplexTokenType.BANG_EQUAL, ComplexTokenType.EQUAL_EQUAL):
            operator, right = self._previous(), self._comparison()
            expr = Binary(expr, operator, right)
        return expr

    def _comparison(self) -> Expr:
        """
        Parse a comparison expression.
        :return: The parsed data
        """
        expr = self._term()
        while self._match(
            ComplexTokenType.GREATER, ComplexTokenType.GREATER_EQUAL, ComplexTokenType.LESS, ComplexTokenType.LESS_EQUAL
        ):
            operator, right = self._previous(), self._term()
            expr = Binary(expr, operator, right)
        return expr

    def _term(self) -> Expr:
        """
        Parse a term expression.
        :return: The parsed data
        """
        expr = self._factor()
        while self._match(SimpleTokenType.MINUS, SimpleTokenType.PLUS, ComplexTokenType.BACKSLASH):
            operator, right = self._previous(), self._factor()
            expr = Binary(expr, operator, right)
        return expr

    def _factor(self) -> Expr:
        """
        Parse a factor expression.
        :return: The parsed data
        """
        expr = self._unary()
        while self._match(SimpleTokenType.SLASH, SimpleTokenType.STAR, SimpleTokenType.MODULO, SimpleTokenType.CARAT):
            operator, right = self._previous(), self._unary()
            expr = Binary(expr, operator, right)
        return expr

    def _unary(self) -> Expr:
        """
        Parse a unary expression.
        :return: The parsed data
        """
        if self._match(SimpleTokenType.BANG, SimpleTokenType.MINUS):
            operator, right = self._previous(), self._unary()
            return Unary(operator, right)
        return self._call()

    def _call(self) -> Expr:
        """
        Parse a call expression.
        :return: The parsed data
        """
        expr = self._primary()
        assert isinstance(expr, Expr)
        while True:
            if self._match(SimpleTokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(SimpleTokenType.DOT):
                name = self._consume(LiteralTokenType.IDENTIFIER, "Expected property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        """
        Finish parsing a call expression.
        :param callee: The callee
        :return: The parsed data
        """
        arguments: list[Expr] = []
        if not self._check(SimpleTokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Cannot have more than 255 arguments.", "\n")
                arguments.append(self._assignment())
                if not self._match(SimpleTokenType.COMMA):
                    break
        paren = self._consume(SimpleTokenType.RIGHT_PAREN, "Expected ')' after arguments.")
        return Call(callee, paren, arguments)

    def _primary(self) -> Expr | None:
        """
        Parse a primary expression.
        :return: The parsed data
        """
        if self._match(KeywordTokenType.FALSE):
            return Literal(False)
        if self._match(KeywordTokenType.TRUE):
            return Literal(True)
        if self._match(KeywordTokenType.NIL):
            return Literal(None)
        if self._match(LiteralTokenType.NUMBER, LiteralTokenType.STRING):
            return Literal(self._previous().literal)
        if self._match(KeywordTokenType.SUPER):
            keyword = self._previous()
            self._consume(SimpleTokenType.DOT, "Expected '.' after 'super'.")
            method = self._consume(LiteralTokenType.IDENTIFIER, "Expected superclass method name.")
            return Super(keyword, method)
        if self._match(KeywordTokenType.THIS):
            return This(self._previous())
        if self._match(LiteralTokenType.IDENTIFIER):
            return Variable(self._previous())
        if self._match(SimpleTokenType.LEFT_PAREN):
            expr = self._assignment()
            self._consume(SimpleTokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
        self._error(self._peek(), f"Expected expression. Got '{self._peek().lexeme}'.", "Invalid expression.")
