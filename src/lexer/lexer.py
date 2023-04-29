import typing as t

from src.exceptions import PyLoxSyntaxError, PyLoxValueError
from src.utils.cursor import Cursor

from .tokens import (
    ComplexTokenType,
    EOFTokenType,
    KeywordTokenType,
    LiteralTokenType,
    MiscTokenType,
    SimpleTokenType,
    Token,
    TokenType,
)

if t.TYPE_CHECKING:
    from src.logger import Logger


__all__: tuple[str, ...] = ("Lexer",)


class Lexer:
    def __init__(self, source: str, logger: "Logger") -> None:
        self._source = source
        self._tokens: list[Token] = []
        self._cursor = Cursor(source=self._source)
        self._logger = logger

    def _add_token(self, token_type: TokenType, literal: t.Any = None) -> None:
        """Add a token to the list of tokens."""
        self._tokens.append(Token.from_raw(token_type, self._cursor, literal))

    def _read_string(self, terminator: str = '"') -> None:
        """Read a string."""
        while self._cursor.peek() != terminator and not self._cursor.at_end:
            if self._cursor.peek() == "\n":
                self._cursor.bump_line()
            self._cursor.advance()
        if self._cursor.at_end:
            self._logger.error(self._cursor.error_highlight("Unterminated string."))
            raise PyLoxValueError(self._cursor.error_highlight("Unterminated string."))
        self._cursor.advance()
        value = self._cursor.source[self._cursor.start + 1 : self._cursor.current - 1]
        self._add_token(LiteralTokenType.STRING, value)

    def _read_identifier(self) -> None:
        """Read an identifier."""
        while self._cursor.peek().isalnum() or self._cursor.peek() == "_":
            self._cursor.advance()
        value = self._cursor.source[self._cursor.start : self._cursor.current]
        _ids = [i.lexeme for i in self._tokens if i.token_type == LiteralTokenType.IDENTIFIER]
        if self._cursor.column - len(value) == 1 and value not in (
            *KeywordTokenType.as_dict().values(),
            *_ids,
        ):
            self._logger.error(self._cursor.error_highlight(f"Invalid identifier '{value}'."))
            raise PyLoxSyntaxError(self._cursor.error_highlight(f"Invalid identifier '{value}'."))
        elif value in KeywordTokenType.as_dict().values():
            self._add_token(KeywordTokenType(value))
        else:
            self._add_token(LiteralTokenType.IDENTIFIER, value)

    def _read_number(self) -> None:
        """Read a number."""
        while self._cursor.peek().isdigit():
            self._cursor.advance()
        is_float = False
        if self._cursor.peek() == "." and self._cursor.peek(offset=1).isdigit():
            is_float = True
            self._cursor.advance()
            while self._cursor.peek().isdigit():
                self._cursor.advance()
        value = self._cursor.source[self._cursor.start : self._cursor.current]
        if self._cursor.column - len(value) == 1 and self._cursor.peek().isalpha() or self._cursor.peek() == "_":
            self._logger.error(self._cursor.error_highlight(f"Invalid number '{value}'."))
            raise PyLoxSyntaxError(self._cursor.error_highlight(f"Invalid number '{value}'."))
        self._add_token(LiteralTokenType.NUMBER, float(value) if is_float else int(value))

    def _read_comment(self) -> None:
        """Read a comment."""
        if self._cursor.match(str(SimpleTokenType.SLASH)):
            while self._cursor.peek() != "\n" and not self._cursor.at_end:
                self._cursor.advance()
        elif self._cursor.match(str(SimpleTokenType.STAR)):
            while not self._cursor.at_end and not (
                self._cursor.match(str(SimpleTokenType.STAR)) and self._cursor.match(str(SimpleTokenType.SLASH))
            ):
                if self._cursor.peek() == "\n":
                    self._cursor.bump_line()
                self._cursor.advance()
            if self._cursor.at_end:
                self._logger.error(self._cursor.error_highlight("Unterminated comment."))
                raise PyLoxSyntaxError(self._cursor.error_highlight("Unterminated comment."))
        else:
            self._add_token(SimpleTokenType.SLASH)

    def _read_complex(self, char: str) -> None:
        if self._cursor.match(str(ComplexTokenType.EQUAL)):
            self._add_token(ComplexTokenType(f"{char}{str(ComplexTokenType.EQUAL)}"))
        elif self._cursor.match(str(ComplexTokenType.BACKSLASH)) and char == str(ComplexTokenType.BACKSLASH):
            self._add_token(ComplexTokenType(char))
        else:
            self._add_token(ComplexTokenType(char))

    def _scan_token(self) -> None:
        """Scan the source file for a token."""
        char = self._cursor.advance()
        if char in MiscTokenType.as_dict().values():
            return
        elif char == str(SimpleTokenType.SLASH):
            self._read_comment()
        elif char in ComplexTokenType.as_dict().values():
            self._read_complex(char)
        elif char in SimpleTokenType.as_dict().values():
            self._add_token(SimpleTokenType(char))
        elif char == "\n":
            self._cursor.bump_line()
        elif char in (str(LiteralTokenType.SINGLE_QUOTE), str(LiteralTokenType.DOUBLE_QUOTE)):
            self._read_string(LiteralTokenType(char))
        elif char.isalpha() or char == "_":
            self._read_identifier()
        elif char.isdigit():
            self._read_number()
        else:
            self._logger.error(self._cursor.error_highlight(f"Unexpected character '{char}'."))
            raise PyLoxSyntaxError(self._cursor.error_highlight(f"Unexpected character '{char}'."))

    def scan_tokens(self) -> list[Token]:
        """Scan the source file for tokens."""
        while not self._cursor.at_end:
            self._cursor.start = self._cursor.current
            self._scan_token()
        eof_ = Token.from_raw(EOFTokenType.EOF, self._cursor)
        self._tokens.append(eof_)
        return self._tokens

    @property
    def source(self) -> str:
        """Return the source file."""
        return self._source

    @source.setter
    def source(self, source: str) -> None:
        """Set the source file."""
        self._source = source
        self._cursor = Cursor(source=self._source)
