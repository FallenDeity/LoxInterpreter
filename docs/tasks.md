# Progress

Note that this is a list of features that I want to implement, and not necessarily the order in which I will implement them.

What has already been implemented:

- [x] Entire lexer implementation
- [x] Expression parsing
- [x] Syntax Errors
- [x] Expression execution
- [x] Print statements
- [x] Variable declaration, and global scope
- [x] Interactive REPL
- [x] Variable assignment
- [x] Proper runtime errors
- [x] Synchronization and reporting multiple parse errors
- [x] Local scope, enclosing scope, blocks and nesting
- [x] `if`-`else` statements
- [x] `while` loops
- [x] `for` loops
- [x] Logical `and` and `or` operators
- [x] Function declarations, calls, first class functions and callbacks
- [x] Return values
- [x] Closures
- [x] Compile time variable resolution and binding
- [x] Class declarations, objects, and properties
- [x] Class properties
- [x] Methods
- [x] `this` attribute
- [x] Constructors
- [x] Inheritance

## Extra features

Here's the full set of extra features, and their progress:

- [x] _Much_ better error messages
- [x] Namespace concept for inbuilt libraries
- [x] Allowing single quotes for strings
- [x] String escapes: `\n`, `\t`, `\'`, `\"`, `\\` and `\↵`
- [x] New operators:
  - [x] Modulo `%`
  - [x] Integer division `\`
  - [x] Power `^`
- [x] Lambda expressions
- [x] New data types:
  - [x] string: `"Hello, world!"`
  - [x] int: `42`
  - [x] list: `[42, 56]`
  - [x] dictionary: `{42: "Forty two"}`
- [x] Indexing support: for lists, dictionaries and strings
- [x] Comparison operators work on strings
- [x] `break` and `continue` semantics in loops
- [x] Exceptions, `try` / `except` blocks and `raise` statements
- [ ] Default values for function parameters
- [ ] `*args`
- [x] Added builtin functions:
  - [x] `input`
  - [x] `read` and `write` for files
  - [x] `min`, `max` and `abs`
  - [x] `map`, `filter` and `reduce` that take lists and return new lists
- [x] An `import` system
- [x] Builtin Callable types
- [x] A standard library
  - [x] `random` module
  - [x] `io` module string and binary reads/writes to files
  - [x] `http` library to make a web server and client
  - [x] `math` module
