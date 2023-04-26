* [Scanning](#scanning)
  * [Base Interpreter Framework](#base-interpreter-framework)
    * [Running a file](#running-a-file)
    * [Running in REPL mode](#running-in-repl-mode)
  * [Tokens](#tokens)
    * [Simple Tokens](#simple-tokens)
    * [Complex Tokens](#complex-tokens)
    * [Literals](#literals)
    * [Keywords](#keywords)
    * [Miscellaneous Tokens](#miscellaneous-tokens)
  * [Lexer](#lexer)
    * [Cursor](#cursor)
  * [Scan Tokens](#scan-tokens)
  * [Identify Tokens](#identify-tokens)

# Scanning

*Lexical Analysis* is the first phase in any compiler or an interpreter. It is also known as *scanning*. It converts the sequence of characters into sequence of tokens. A *token* is a sequence of characters that can be treated as a unit in the grammar of the programming languages.  

This part of the article will be explaining my take on the lexer for `Lox` language using python.

## Base Interpreter Framework

Currently there are going to be two modes for running lox scripts

- Directly from a file where interpreter recieves the file path as an argument
- Directly from the command line where interpreter runs in a REPL mode

> 📝 **Note**  
> REPL stands for Read-Eval-Print-Loop. It is a simple interactive computer programming environment that takes single user inputs, executes them, and returns the result to the user; a program written in a REPL environment is executed piecewise.

> ⚠️ **Warning**  
> For exiting the code or quitting on errors such as `SyntaxError` or `ValueError` we will take advantage of python's exception mechanism by raising custom exceptions.

```python
class PyLox:
    def __init__(self, source: str | pathlib.Path = "") -> None:
        self.logger = Logger(name="PyLox")
        self.lexer = Lexer(source, self.logger)
```

The `PyLox` class is the base class for the interpreter. It takes the path of the file as an argument and creates a `Lexer` object. The `Lexer` object is responsible for scanning the source code and generating tokens.
The `Logger` class is a simple wrapper around the `logging` module. It is used for logging the errors and warnings. In our case it is completely optional and replaceable with the `print` function.

### Running a file

```python
    def run(self) -> None:
        self.logger.info("Running PyLox...")
        tokens = self.lexer.scan_tokens()
        for token in tokens:
            self.logger.flair(f"{token}")
        self.logger.info("Finished running PyLox.")
```

The `run` method is responsible for running the interpreter in the file mode. It calls the `scan_tokens` method of the `Lexer` class which returns a list of tokens. The `run` method then iterates over the list of tokens and prints them to the console.

### Running in REPL mode

```python
    def run_prompt(self) -> None:
        while True:
            try:
                source = input("> ")
            except KeyboardInterrupt:
                self.logger.debug("Exiting PyLox...")
                raise PyLoxKeyboardInterrupt
            else:
                self.logger.info("Running PyLox...")
                self.lexer.source = f"{source}\n"
                tokens = self.lexer.scan_tokens()
                for token in tokens:
                    self.logger.flair(f"{token}")
                self.logger.info("Finished running PyLox.")
```

The `run_prompt` method is responsible for running the interpreter in the REPL mode. It takes the input from the user and passes it to the `Lexer` class. The `Lexer` class then scans the input and returns a list of tokens. The `run_prompt` method then iterates over the list of tokens and prints them to the console.
The `run_prompt` method is wrapped in a `while` loop which keeps the interpreter running until the user presses `Ctrl+C` to exit the interpreter.

## Tokens

Now before moving on to the `Lexer` class lets take a look at what all tokens or keywords we are going to support in our language.

```python
class TokenType(enum.StrEnum):
    """Base class for token types."""

    @classmethod
    def as_dict(cls) -> dict[str, str]:
        """Return a dictionary of the enum values."""
        return {key: str(value) for key, value in cls.__members__.items()}
```

All tokens with be stored in `Enums` for better readability and maintainability. The `TokenType` class is a base class for all the token types. It also provides a class method `as_dict` which returns a dictionary of all the token types.

```python
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
```

The `Token` class is a simple dataclass which stores the token type, lexeme, literal, line number and column number of the token. The `from_raw` class method is used to create a token from a raw character.

- `token_type` is the type of the token
- `lexeme` is the actual string of characters that make up the token
- `literal` is the value of the token (like in case of `var a = 10` the literal value of `a` is `10`)
- `line` is the line number of the token
- `column` is the column number of the token

### Simple Tokens

Simple tokens consist of single characters like `(`, `)`, `{`, `}`, etc. These tokens are represented by the `SimpleTokenType` class.

```python
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
```

These tokens are easiest to implement as they are just a single character except for `\` character which we will see soon why.

### Complex Tokens

Complex tokens consist of multiple characters like `==`, `!=`, `<=`, `>=`, etc. These tokens are represented by the `ComplexTokenType` class.

```python
class ComplexTokenType(TokenType):
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
```

These tokens are a bit tricky to implement as they consist of multiple characters and can be used in combination with other tokens. For example `=` can be used as an assignment operator or as a part of `==` token. To handle this we will be using a `\` character to escape the `=` character. So if the `\` character is present before the `=` character then we will treat it as a part of the `==` token otherwise we will treat it as an assignment operator.

### Literals

Literals are tokens consisting of a sequence of characters. These tokens are represented by the `LiteralTokenType` class.

```python
class LiteralTokenType(TokenType):
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
```

The `IDENTIFIER` token is used to represent variable names. The `STRING` token is used to represent string literals. The `NUMBER` token is used to represent number literals.

### Keywords

Keywords are tokens which have a special meaning in the language. These tokens are represented by the `KeywordTokenType` class.

```python
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
```

### Miscellaneous Tokens

Finally we arrive at miscellaneous tokens. These tokens are represented by the `MiscTokenType` class.

```python
class EOFTokenType(TokenType):
    EOF = enum.auto()


class MiscTokenType(TokenType):
    WS = " "
    TAB = "\t"
    LF = "\r"
```

These tokens are used to represent the end of file and white spaces and other arbitrary characters.

## Lexer

Now lets move on to the main attraction of this article, the `Lexer` class. The `Lexer` class is responsible for scanning the source code and generating tokens.  

```python
class Lexer:
    _file_path: pathlib.Path | str

    def __init__(self, source: str | pathlib.Path, logger: "Logger") -> None:
        self._file_path = pathlib.Path(source) if source else ""
        self._source = self._read_file(self._file_path) if self._file_path else ""
        self._tokens: list[Token] = []
        self._curser = Cursor(source=self._source)
        self._logger = logger
```

The `Lexer` class takes the source code and a `Logger` object as arguments. It then creates a `Cursor` object which is responsible for keeping track of the current position in the source code. The `Lexer` class also creates an empty list of tokens which will be populated by the `scan_tokens` method.
The cursor is a simple dataclass which keeps track of the current position in the source code. It helps in keeping the code organized and readable.


### Cursor

```python
@dataclasses.dataclass
class Cursor:
    current: int = 0
    start: int = 0
    line: int = 1
    column: int = 1
    source: str = ""
```

- current: The current position in the source code.
- start: The start position of the current token.
- line: The current line number.
- column: The current column number.
- source: The source code.

The cursor also provides a few handy methods which we will be using to tokenize the raw source code.

```python
    def advance(self) -> str:
        """
        Advance the cursor by one character.
        :return: The character at the current position.
        """
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]
```

The `advance` method is used to advance the cursor by one character.

```python
    def peek(self, offset: int = 0) -> str:
        """
        Peek at the character at the current position.
        :param offset: The offset from the current position.
        :return: The character at the current position.
        """
        if self.current + offset >= len(self.source):
            return "\0"
        return self.source[self.current + offset]
```

The `peek` method is used to peek at the character at the current position. It also takes an optional `offset` argument which can be used to peek at the character at a position relative to the current position.

```python
    def match(self, expected: str) -> bool:
        """
        Match the current character with the expected character.
        :param expected: The expected character.
        :return: True if the current character matches the expected character, False otherwise.
        """
        if self.at_end:
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True
```

The `match` method is used to match the current character with the expected character. It returns `True` if the current character matches the expected character, `False` otherwise.

```python
    @property
    def at_end(self) -> bool:
        """
        Check if the cursor is at the end of the source code.
        :return: True if the cursor is at the end of the source code, False otherwise.
        """
        return self.current >= len(self.source)
```

The `at_end` property is used to check if the cursor is at the end of the source code.

```python
    def error_highlight(self, message: str) -> str:
        """
        Highlight the error in the source code.
        :param message: The error message.
        :return: The error message with the source code.
        """
        error = f"Error on line {self.line} at column {self.column}:\n"
        c_line = self.source.splitlines()[self.line - 1]
        return f"{error}\n{c_line}\n{'~' * (self.column - 1)}^\n{message}"
```

The `error_highlight` method is used to highlight the error in the source code. It takes an error message as an argument and returns the error message with the source code.
The main reason why I included another column attribute was for more detailed error messages.

You wouldn't want an error like this would you? `:p`

```
Error: Unexpected "," somewhere in your code. Good luck finding it!
```

## Scan Tokens

```python
    def scan_tokens(self) -> list[Token]:
        """Scan the source file for tokens."""
        while not self._curser.at_end:
            self._curser.start = self._curser.current
            self._scan_token()
        eof_ = Token.from_raw(EOFTokenType.EOF, self._curser)
        eof_.lexeme = ""
        self._tokens.append(eof_)
        return self._tokens
```

The `scan_tokens` method is used to scan the source code for tokens. It does this by calling the `_scan_token` method until the cursor reaches the end of the source code. It then appends an `EOF` token to the list of tokens and returns the list of tokens.

## Identify Tokens

```python
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
```

Now lets break this down to smaller parts to make it easier to understand.

```python
        if char in MiscTokenType.as_dict().values():
            return
```

This part detects for characters which dont affect our final code such as `\t` or `\r` and white spaces.

```python
        elif char == str(SimpleTokenType.SLASH):
            if self._curser.match(str(SimpleTokenType.SLASH)):
                while self._curser.peek() != "\n" and not self._curser.at_end:
                    self._curser.advance()
            else:
                self._add_token(SimpleTokenType.SLASH)
```

Now this contains an interesting part as our language defines `//` as a comment. So we have to detect for that and ignore everything until we reach a new line character and segregate this operation from the division operation.

```python
        elif char in SimpleTokenType.as_dict().values():
            self._add_token(SimpleTokenType(char))
```

This part is as simple as it gets. It just adds a token for simple tokens like `(`, `)`, `{`, `}`, etc.

```python
        elif char in ComplexTokenType.as_dict().values():
            if self._curser.match("="):
                self._add_token(ComplexTokenType(f"{char}="))
            else:
                self._add_token(ComplexTokenType(char))
```

The above snippet handles cases for complex operators with one to two characters in variations like `==`, `!=`, `<=`, `>=`, etc.
`match` method attempts to match with the next character and if it matches, it adds a token for the complex operator with two characters. If it doesn't match, it adds a token for the complex operator with one character.

```python
        elif char == "\n":
            if self._curser.peek(offset=-2) != str(SimpleTokenType.SEMICOLON):
                self._logger.error(self._curser.error_highlight("Missing ';' at end of line."))
                raise PyLoxSyntaxError(self._curser.error_highlight("Missing ';' at end of line."))
            self._curser.line += 1
            self._curser.column = 1
```

This part is used to handle new line characters. It increments the line number and resets the column number to 1.
Also checks if the previous character is a semicolon or not. If it isn't, it raises an error.

```python
        elif char == '"':
            self._read_string()
```

```python
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
```

This part is used to handle strings. It reads the string until it reaches a `"` character and adds a token for the string.
If it reaches the end of the source code, it raises an error.

```python
        elif char.isalpha() or char == "_":
            self._read_identifier()
```

If a character is alphabetic or includes / starts with a `_` it matches it with an identifier / keyword depending on the case.

```python
    def _read_identifier(self) -> None:
        """Read an identifier."""
        while self._curser.peek().isalnum() or self._curser.peek() == "_":
            self._curser.advance()
        value = self._curser.source[self._curser.start : self._curser.current]
        _ids = [i.lexeme for i in self._tokens if i.token_type == LiteralTokenType.IDENTIFIER]  # list of existing identifiers for cases such as `var x = 7;` followed by `x = 8;` to check declaration
        if self._curser.column - len(value) == 1 and value not in (
            *KeywordTokenType.as_dict().values(),
            *_ids,
        ):  # if the identifier is not a keyword or already declared it raises an error
            self._logger.error(self._curser.error_highlight(f"Invalid identifier '{value}'."))
            raise PyLoxSyntaxError(self._curser.error_highlight(f"Invalid identifier '{value}'."))
        elif value in KeywordTokenType.as_dict().values():  # if the identifier is a keyword it adds a token for the keyword
            self._add_token(KeywordTokenType(value))
        else:  # else it adds a token for the identifier
            self._add_token(LiteralTokenType.IDENTIFIER, value)
```

This part is used to handle identifiers. It reads the identifier until it reaches a non-alphanumeric character and adds a token for the identifier.

```python
        elif char.isdigit():
            self._read_number()
```

If a character is a digit, it matches it with a number. By default all numbers in `Lox` are double precision floating point numbers.

```python
       def _read_number(self) -> None:
        """Read a number."""
        while self._curser.peek().isdigit():
            self._curser.advance()
        if self._curser.peek() == "." and self._curser.peek(offset=1).isdigit():  # if the number is followed by a `.` and a digit it reads the number as a double
            self._curser.advance()
            while self._curser.peek().isdigit():
                self._curser.advance()
        value = self._curser.source[self._curser.start : self._curser.current]
        if self._curser.column - len(value) == 1 and self._curser.peek().isalpha() or self._curser.peek() == "_":  # if the number is followed by an alphabetic character or a `_` it raises an error we dont want cases like 1var or any identifier starting with a number
            self._logger.error(self._curser.error_highlight(f"Invalid number '{value}'."))
            raise PyLoxSyntaxError(self._curser.error_highlight(f"Invalid number '{value}'."))
        self._add_token(LiteralTokenType.NUMBER, value)
```

This part is used to handle numbers. It reads the number until it reaches a non-digit character and adds a token for the number.

```python
        else:
            self._logger.error(self._curser.error_highlight(f"Unexpected character '{char}'."))
            raise PyLoxSyntaxError(self._curser.error_highlight(f"Unexpected character '{char}'."))
```

Finally if the character is not present in our pre-defined set of characters it raises an error.

```python
    def _add_token(self, token_type: TokenType, literal: str | None = None) -> None:
        """Add a token to the list of tokens."""
        self._tokens.append(Token.from_raw(token_type, self._curser, literal))
```

This concludes our `Lexer` class now we can fire up our `REPL` and test it out.

```
> var x = "123.9";
[2023-04-27 04:05:52,063] | ~\src\interpreter\lox.py:23 | INFO | Running PyLox...
[2023-04-27 04:05:52,063] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<KeywordTokenType.VAR: 'var'>, self.lexeme='var', self.literal=None, self.line=1, self.column=4)
[2023-04-27 04:05:52,064] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<LiteralTokenType.IDENTIFIER: 'identifier'>, self.lexeme='x', self.literal='x', self.line=1, self.column=6)
[2023-04-27 04:05:52,064] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<ComplexTokenType.EQUAL: '='>, self.lexeme='=', self.literal=None, self.line=1, self.column=8)
[2023-04-27 04:05:52,064] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<LiteralTokenType.STRING: 'string'>, self.lexeme='"123.9"', self.literal='123.9', self.line=1, self.column=16)
[2023-04-27 04:05:52,064] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<SimpleTokenType.SEMICOLON: ';'>, self.lexeme=';', self.literal=None, self.line=1, self.column=17)
[2023-04-27 04:05:52,064] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<EOFTokenType.EOF: 'eof'>, self.lexeme='', self.literal=None, self.line=1, self.column=17)
[2023-04-27 04:05:52,064] | ~\src\interpreter\lox.py:28 | INFO | Finished running PyLox.
> var y = 123.9;
[2023-04-27 04:06:28,694] | ~\src\interpreter\lox.py:23 | INFO | Running PyLox...
[2023-04-27 04:06:28,694] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<KeywordTokenType.VAR: 'var'>, self.lexeme='var', self.literal=None, self.line=1, self.column=4)
[2023-04-27 04:06:28,694] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<LiteralTokenType.IDENTIFIER: 'identifier'>, self.lexeme='y', self.literal='y', self.line=1, self.column=6)
[2023-04-27 04:06:28,694] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<ComplexTokenType.EQUAL: '='>, self.lexeme='=', self.literal=None, self.line=1, self.column=8)
[2023-04-27 04:06:28,694] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<LiteralTokenType.NUMBER: 'number'>, self.lexeme='123.9', self.literal='123.9', self.line=1, self.column=14)
[2023-04-27 04:06:28,694] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<SimpleTokenType.SEMICOLON: ';'>, self.lexeme=';', self.literal=None, self.line=1, self.column=15)
[2023-04-27 04:06:28,694] | ~\src\logger.py:98 | FLAIR | Token(self.token_type=<EOFTokenType.EOF: 'eof'>, self.lexeme='', self.literal=None, self.line=1, self.column=15)
[2023-04-27 04:06:28,694] | ~\src\interpreter\lox.py:28 | INFO | Finished running PyLox.
```

As you can see we have successfully implemented the `Lexer` class and it is working as expected.

<html lang="en">
    <style>
        .btn-blue {
            background-color: #3498db;
            border-color: #3498db;
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
        }
        .btn-blue:hover {
            background-color: #2980b9;
            border-color: #2980b9;
            color: #fff;
        }
    </style>
    <a class="btn-blue" href="language.html" style="float: left;">Previous: Language</a>
    <a class="btn-blue" href="parser.html" style="float: right;">Next: Parser</a>
</html>
