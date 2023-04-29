import dataclasses
import pathlib
import re

IMPORT_PATTERN = re.compile(r"import\s+(?P<module><\w+>|\"\w+.lox\")")
HEADERS = pathlib.Path("src/headers")


__all__: tuple[str, ...] = (
    "PreProcessor",
    "Import",
)


@dataclasses.dataclass
class Import:
    path: pathlib.Path
    line: int
    start: int
    end: int
    module: str


class PreProcessor:
    def __init__(self, source: str) -> None:
        self._includes: dict[str, Import] = {}
        self._source = source
        self._resolve_imports()

    def _resolve_imports(self) -> None:
        paths: set[pathlib.Path] = set()
        lines = self._source.splitlines(keepends=True)
        for n, line in enumerate(lines):
            if line.strip() and (match := IMPORT_PATTERN.match(line.strip())):
                module = match.group("module")
                if module.startswith("<"):
                    path = HEADERS / f"{module[1:-1]}.lox"
                elif module.startswith('"'):
                    path = pathlib.Path(module[1:-1])
                else:
                    raise ValueError(f"Invalid module {module!r}.")
                if path in paths or not path.exists():
                    continue
                paths.add(path)
                self._includes[path.as_posix()] = Import(path, n, match.start(), match.end(), module)
        for module in self._includes.values():
            text = module.path.read_text()
            if module.module.startswith("<") and "init" not in text and f"class {module.module[1:-1]}" in text:
                text += f"\nvar {module.module[1:-1]} = {module.module[1:-1]}();"
            self._source = self._source.replace(f"import {module.module}", text)

    @property
    def includes(self) -> dict[str, Import]:
        return self._includes

    @property
    def source(self) -> str:
        return self._source
