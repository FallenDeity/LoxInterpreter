import dataclasses

__all__: tuple[str, ...] = ("Cursor",)


@dataclasses.dataclass
class Cursor:
    current: int = 0
    start: int = 0
    line: int = 1
    column: int = 1
    source: str = ""

    def advance(self) -> str:
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]

    def match(self, expected: str) -> bool:
        if self.at_end:
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def peek(self, offset: int = 0) -> str:
        if self.current + offset >= len(self.source):
            return "\0"
        return self.source[self.current + offset]

    def error_highlight(self, message: str) -> str:
        error = f"Error on line {self.line} at column {self.column}:\n"
        c_line = self.source.splitlines()[self.line - 1]
        return f"{error}\n{c_line}\n{'~' * (self.column - 1)}^\n{message}"

    @property
    def at_end(self) -> bool:
        return self.current >= len(self.source)
