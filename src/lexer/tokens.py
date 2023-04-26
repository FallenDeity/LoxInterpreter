import dataclasses
import enum
import typing as t

if t.TYPE_CHECKING:
    from src.models import Cursor


__all__: tuple[str, ...] = (
    "TokenType",
    "Token",
    "SimpleTokenType",
    "ComplexTokenType",
    "LiteralTokenType",
    "KeywordTokenType",
    "EOFTokenType",
    "MiscTokenType",
)


class TokenType(enum.StrEnum):
    """Base class for token types."""

    @classmethod
    def as_dict(cls) -> dict[str, str]:
        """Return a dictionary of the enum values."""
        return {key: str(value) for key, value in cls.__members__.items()}


class SimpleTokenType(TokenType):
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"
    BANG = "!"


class ComplexTokenType(TokenType):
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="


class LiteralTokenType(TokenType):
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()


class KeywordTokenType(TokenType):
    AND = "and"
    CLASS = "class"
    ELSE = "else"
    FALSE = "false"
    FUN = "fun"
    FOR = "for"
    IF = "if"
    NIL = "nil"
    OR = "or"
    PRINT = "print"
    RETURN = "return"
    SUPER = "super"
    THIS = "this"
    TRUE = "true"
    VAR = "var"
    WHILE = "while"
    BREAK = "break"
    CONTINUE = "continue"


class EOFTokenType(TokenType):
    EOF = enum.auto()


class MiscTokenType(TokenType):
    WS = " "
    TAB = "\t"
    LF = "\r"


@dataclasses.dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: t.Optional[str]
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.token_type=}, {self.lexeme=}, {self.literal=}, {self.line=}, {self.column=})"

    @classmethod
    def from_raw(cls, token: TokenType, cursor: "Cursor", literal: t.Optional[str] = None) -> "Token":
        """Create a token from a raw character."""
        return cls(
            token_type=token,
            lexeme=cursor.source[cursor.start : cursor.current],
            literal=literal,
            line=cursor.line,
            column=cursor.column,
        )
