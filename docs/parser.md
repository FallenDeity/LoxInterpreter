# Parsing

## Introduction

In the previous step we have created a lexer that can tokenize our input. Now we need to parse the tokens and create an AST (Abstract Syntax Tree) from them. The AST is a tree representation of the source code.
An `AST` is a more richer and comprehensive representation of the source code than the tokens which allows us to evaluate the code and generate the output.
Regular/linear language formats like a stream of tokens cannot be used for complex expressions due to multiple variations of the same expression. Hence we need a more complex representation to handle arbitrary levels of nesting and precedence.

![AST](https://craftinginterpreters.com/image/representing-code/tree-evaluate.png)

## Grammar

The grammar of a language is a set of rules that define the syntax of the language.

Our language `Lox` will contain the following Grammar expressions:

- Literals (e.g. `123`, `"abc"`, `true`, `nil`)
- Unary expressions (e.g. `-123`, `!true`)
- Binary expressions (e.g. `1 + 2`, `3 * 4`, `true == false`)
- Grouping expressions (e.g. `(1 + 2) * 3`)
- Variable expressions (e.g. `a`, `b`)
- Assignment expressions (e.g. `a = 1`, `b = "abc"`)
- Logical expressions (e.g. `true and false`, `true or false`)
- Call expressions (e.g. `print("abc")`, `print(1 + 2)`)
- Get expressions (e.g. `a.b`, `a.b.c`)
- Set expressions (e.g. `a.b = "abc"`, `a.b.c = 1 + 2`)
- This expressions (e.g. `this`)
- Super expressions (e.g. `super.method()`)

> ℹ️  **Note**
> Definition of the data models can be found [here](https://github.com/FallenDeity/LoxInterpreter/blob/master/src/utils/expr.py)

Now that we know what expressions we need to support, we can define the grammar rules for them. The grammar rules are defined using a notation called `Backus-Naur Form` (BNF).
BNF is a notation for expressing context-free grammars. A context-free grammar is a set of recursive rules used to generate patterns of strings.

The following is the BNF notation for our language:

```bnf
program        → declaration* EOF ;

declaration    → classDecl
               | funDecl
               | varDecl
               | statement ;

classDecl      → "class" IDENTIFIER ( "<" IDENTIFIER )?  // Inheritance
                 "{" function* "}" ;

funDecl        → "fun" function ;

varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;

statement      → exprStmt
               | forStmt
               | ifStmt
               | printStmt
               | returnStmt
               | whileStmt
               | block
               | breakStmt
               | continueStmt ;  

exprStmt       → expression ";" ;
```

The `*` symbol means that the preceding element can be repeated zero or more times. The `|` symbol means that the preceding element is optional. The `?` symbol means that the preceding element can be repeated zero or one times.

## Parsing

Now that we have defined the grammar rules, we can start parsing the tokens. We will use a technique called `Recursive Descent Parsing` to parse the tokens. Recursive descent parsing is a top-down parsing technique that constructs the parse tree from the top and the input is read from left to right. The parser starts with the start symbol and recursively parses the input until it matches the start symbol.

Let's start by defining the `Parser` class:

```python
class Parser:
    def __init__(self, tokens: list["Token"], logger: "Logger", source: str, debug: bool = True) -> None:
        self._tokens = tokens
        self._current = 0
        self._logger = logger
        self._debug = debug
        self._source = source
        self._has_error = False

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
```

This is the base parser class that we will use to parse the tokens. The parser class contains the following methods to help us parse the tokens:

- `_previous()` - Get the previous token.
- `_peek()` - Get the current token.
- `_is_at_end()` - Check if the parser is at the end of the tokens.
- `_advance()` - Advance the parser.
- `_check()` - Check if the current token is of a certain type.
- `_match()` - Check if the current token is of any of the given types.

Now that we have defined the base parser class, we can start parsing the tokens.  

