import dataclasses

__all__: tuple[str, ...] = ("Cursor",)


@dataclasses.dataclass
class Cursor:
    """
    A cursor for tracking the current position in the source code.
    """

    current: int = 0
    start: int = 0
    line: int = 1
    column: int = 1
    source: str = ""

    def advance(self) -> str:
        """
        Advance the cursor by one character.
        :return: The character at the current position.
        """
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]

    def bump_line(self) -> None:
        self.line += 1
        self.column = 1

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

    def peek(self, offset: int = 0) -> str:
        """
        Peek at the character at the current position.
        :param offset: The offset from the current position.
        :return: The character at the current position.
        """
        if self.current + offset >= len(self.source):
            return "\0"
        return self.source[self.current + offset]

    def error_highlight(self, message: str) -> str:
        """
        Highlight the error in the source code.
        :param message: The error message.
        :return: The error message with the source code.
        """
        error = f"Error on line {self.line} at column {self.column}:\n"
        c_line = self.source.splitlines()[self.line - 1]
        return f"{error}\n{c_line}\n{'~' * (self.column - 1)}^\n{message}"

    @property
    def at_end(self) -> bool:
        """
        Check if the cursor is at the end of the source code.
        :return: True if the cursor is at the end of the source code, False otherwise.
        """
        return self.current >= len(self.source)
