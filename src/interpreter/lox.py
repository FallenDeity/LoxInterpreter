import pathlib

from src.exceptions import PyLoxException, PyLoxKeyboardInterrupt
from src.lexer import Lexer
from src.logger import Logger
from src.parser import Parser
from src.preprocessor import PreProcessor

from .interpreter import Interpreter
from .resolver import Resolver

__all__: tuple[str, ...] = ("PyLox",)


class PyLox:
    def __init__(self, source: str | pathlib.Path = "") -> None:
        self._file_path = pathlib.Path(source) if source else None
        self.logger = Logger(name="PyLox")
        self.interpreter = Interpreter(self, self.logger)
        self._source = self._read_file(self._file_path) if self._file_path else ""
        process = PreProcessor(self._source)
        self._source = process.source
        self.lexer = Lexer(self._source, self.logger)

    @staticmethod
    def _read_file(path: pathlib.Path) -> str:
        """Read the source file."""
        with open(path, "r") as file:
            return file.read()

    def run_prompt(self) -> None:
        while True:
            try:
                source = input(">>> ")
            except KeyboardInterrupt:
                self.logger.debug("Exiting PyLox...")
                raise PyLoxKeyboardInterrupt
            else:
                self.logger.info("Running PyLox...")
                self.lexer.source = f"{source}\n"
                try:
                    tokens = self.lexer.scan_tokens()
                    parser = Parser(tokens, self.logger, self._source)
                    statements = parser.parse()
                    if parser._has_error:
                        continue
                    resolver = Resolver(self.interpreter)
                    resolver._resolve(statements)
                    self.interpreter.interpret(statements)
                    self.logger.info("Finished running PyLox.")
                except PyLoxException:
                    continue

    def run(self) -> None:
        self.logger.info("Running PyLox...")
        tokens = self.lexer.scan_tokens()
        parser = Parser(tokens, self.logger, self._source)
        statements = parser.parse()
        if parser._has_error:
            return
        resolver = Resolver(self.interpreter)
        resolver._resolve(statements)
        self.interpreter.interpret(statements)
        self.logger.info("Finished running PyLox.")
