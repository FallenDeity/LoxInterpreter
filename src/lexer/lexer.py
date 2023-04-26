import pathlib
import typing as t

from src.exceptions import PyLoxSyntaxError, PyLoxValueError
from src.models import Cursor

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
    _file_path: pathlib.Path | str

    def __init__(self, source: str | pathlib.Path, logger: "Logger") -> None:
        self._file_path = pathlib.Path(source) if source else ""
        self._source = self._read_file(self._file_path) if self._file_path else ""
        self._tokens: list[Token] = []
        self._curser = Cursor(source=self._source)
        self._logger = logger

    @staticmethod
    def _read_file(path: pathlib.Path) -> str:
        """Read the source file."""
        with open(path, "r") as file:
            return file.read()

    def _add_token(self, token_type: TokenType, literal: str | None = None) -> None:
        """Add a token to the list of tokens."""
        self._tokens.append(Token.from_raw(token_type, self._curser, literal))

    def _read_string(self) -> None:
        """Read a string."""
        while self._curser.peek() != '"' and not self._curser.at_end:
            if self._curser.peek() == "\n":
                self._curser.line += 1
                self._curser.column = 1
            self._curser.advance()
        if self._curser.at_end:
            self._logger.error(self._curser.error_highlight("Unterminated string."))
            raise PyLoxValueError(self._curser.error_highlight("Unterminated string."))
        self._curser.advance()
        value = self._curser.source[self._curser.start + 1 : self._curser.current - 1]
        self._add_token(LiteralTokenType.STRING, value)

    def _read_identifier(self) -> None:
        """Read an identifier."""
        while self._curser.peek().isalnum() or self._curser.peek() == "_":
            self._curser.advance()
        value = self._curser.source[self._curser.start : self._curser.current]
        _ids = [i.lexeme for i in self._tokens if i.token_type == LiteralTokenType.IDENTIFIER]
        if self._curser.column - len(value) == 1 and value not in (
            *KeywordTokenType.as_dict().values(),
            *_ids,
        ):
            self._logger.error(self._curser.error_highlight(f"Invalid identifier '{value}'."))
            raise PyLoxSyntaxError(self._curser.error_highlight(f"Invalid identifier '{value}'."))
        elif value in KeywordTokenType.as_dict().values():
            self._add_token(KeywordTokenType(value))
        else:
            self._add_token(LiteralTokenType.IDENTIFIER, value)

    def _read_number(self) -> None:
        """Read a number."""
        while self._curser.peek().isdigit():
            self._curser.advance()
        if self._curser.peek() == "." and self._curser.peek(offset=1).isdigit():
            self._curser.advance()
            while self._curser.peek().isdigit():
                self._curser.advance()
        value = self._curser.source[self._curser.start : self._curser.current]
        if self._curser.column - len(value) == 1 and self._curser.peek().isalpha() or self._curser.peek() == "_":
            self._logger.error(self._curser.error_highlight(f"Invalid number '{value}'."))
            raise PyLoxSyntaxError(self._curser.error_highlight(f"Invalid number '{value}'."))
        self._add_token(LiteralTokenType.NUMBER, value)

    def _scan_token(self) -> None:
        """Scan the source file for a token."""
        char = self._curser.advance()
        if char in MiscTokenType.as_dict().values():
            return
        elif char == str(SimpleTokenType.SLASH):
            if self._curser.match(str(SimpleTokenType.SLASH)):
                while self._curser.peek() != "\n" and not self._curser.at_end:
                    self._curser.advance()
            else:
                self._add_token(SimpleTokenType.SLASH)
        elif char in SimpleTokenType.as_dict().values():
            self._add_token(SimpleTokenType(char))
        elif char in ComplexTokenType.as_dict().values():
            if self._curser.match("="):
                self._add_token(ComplexTokenType(f"{char}="))
            else:
                self._add_token(ComplexTokenType(char))
        elif char == "\n":
            self._curser.line += 1
            self._curser.column = 1
        elif char == '"':
            self._read_string()
        elif char.isalpha() or char == "_":
            self._read_identifier()
        elif char.isdigit():
            self._read_number()
        else:
            self._logger.error(self._curser.error_highlight(f"Unexpected character '{char}'."))
            raise PyLoxSyntaxError(self._curser.error_highlight(f"Unexpected character '{char}'."))

    def scan_tokens(self) -> list[Token]:
        """Scan the source file for tokens."""
        while not self._curser.at_end:
            self._curser.start = self._curser.current
            self._scan_token()
        eof_ = Token.from_raw(EOFTokenType.EOF, self._curser)
        eof_.lexeme = ""
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
        self._curser = Cursor(source=self._source)
        self._file_path = ""
