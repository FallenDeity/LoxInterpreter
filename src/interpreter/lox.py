import pathlib

from src.exceptions import PyLoxKeyboardInterrupt, PyLoxEception
from src.lexer import Lexer
from src.logger import Logger

__all__: tuple[str, ...] = ("PyLox",)


class PyLox:
    def __init__(self, source: str | pathlib.Path = "") -> None:
        self.logger = Logger(name="PyLox")
        self.lexer = Lexer(source, self.logger)

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
                    for token in tokens:
                        self.logger.flair(f"{token}")
                    self.logger.info("Finished running PyLox.")
                except PyLoxEception:
                    continue

    def run(self) -> None:
        self.logger.info("Running PyLox...")
        tokens = self.lexer.scan_tokens()
        for token in tokens:
            self.logger.flair(f"{token}")
        self.logger.info("Finished running PyLox.")
