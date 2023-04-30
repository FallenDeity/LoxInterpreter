* [Interpreter](#interpreter)
  * [The Interpreter](#the-interpreter)
    * [Local Variables](#local-variables)
  * [Evaluating Expressions](#evaluating-expressions)
    * [Grouping](#grouping)
    * [Unary](#unary)
    * [Binary](#binary)
  * [Evaluating statements](#evaluating-statements)
    * [Expression statement](#expression-statement)
    * [Blocks](#blocks)
    * [Variable declaration](#variable-declaration)
    * [If statement](#if-statement)
    * [While statement](#while-statement)
    * [Functions and Classes](#functions-and-classes)
    * [Calls](#calls)
    * [Get and Set](#get-and-set)
  * [Conclusion](#conclusion)

# Interpreter

This brings us to the end of this fascinating journey of building our own language and interpreter from scratch. In this final chapter, we will put together all the pieces we have built so far and create a fully functional interpreter for our language.  
The interpreter code structure is similar to the `resolver` code structure. We will have a `accept` method for each node type. The `accept` method will be responsible for evaluating the node and returning the result. Just instead of resolving scope, we will be evaluating the node.

Since we are building a tree-walk interpreter, we will start from the root node and recursively evaluate each node. A node will be evaluated by calling its `accept` method. The `accept` method will call the `accept` method of its children and so on. The `accept` method of a node will return the result of the node evaluation. The result of the node evaluation will be used by the parent node to evaluate itself. This process will continue until we reach the root node. The result of the root node evaluation will be the result of the program.

So let's get started.

## The Interpreter

```python
class Interpreter(VisitorProtocol, StmtProtocol):
    _environment: Environment
    builtins: pathlib.Path = pathlib.Path("src/builtins")

    def __init__(self, lox: "PyLox", logger: "Logger") -> None:
        self._lox = lox
        self._logger = logger
        self._environment = Environment()
        self._locals: t.Dict["Expr", int] = {}

    def interpret(self, statements: list["Stmt"]) -> None:
        """Interpret a list of statements."""
        try:
            for statement in statements:
                self._evaluate(statement)
        except PyLoxRuntimeError as error:
            self._logger.error(str(error))
```

The `Interpreter` class implements the `VisitorProtocol` and `StmtProtocol` protocols. The `VisitorProtocol` protocol is used to implement the visitor pattern for the expression nodes. The `StmtProtocol` protocol is used to implement the visitor pattern for the statement nodes. The `Interpreter` class also has an `_environment` attribute which is an instance of the `Environment` class. The `Environment` class is used to store the variables and their values. The `Interpreter` class also has a `_locals` attribute which is a dictionary that maps an expression node to its depth in the scope. The `_locals` dictionary is used to store the local variables and their values.

The `interpret` method is the entry point of the interpreter. It takes a list of statements as an argument. The `interpret` method iterates over the list of statements and calls the `_evaluate` method of the `Interpreter` class with each statement as an argument. The `_evaluate` method is responsible for evaluating the statement.

```python
    def _evaluate(self, stmt: Stmt) -> None:
        stmt.accept(self)  # accept is the visitor pattern method
```

### Local Variables

When we were talking about the `Resolver` class, we discussed about a `_resolve_local` method. This method called onto the `_resolve` method of the `Interpreter` class. The `_resolve` method of the `Interpreter` class is responsible for resolving the local variables. The `_resolve` method takes two arguments, the `expr` and the `depth`. The `expr` argument is the expression node whose value is to be resolved. The `depth` argument is the depth of the scope in which the expression node is present. The `_resolve` method returns the value of the expression node.

```python
    def _resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth
```

Storing the depth of the scope in which the expression node is present is useful when we are resolving the local variables. It allows us to know how many scopes we need to go up to resolve the local variable.

Take this program for example:

```js
fun foo(n) {
    var multiplier = 2;
    return multiplier * n;
}

print foo(5);
```

In this case there are two local variables, `n` and `multiplier`. At one level of nesting compared to global environment. So when the `Resolver` class resolves the local variables, it will call the `_resolve` method of the `Interpreter` class with the `depth` argument as `0` zero since we calculated depth using for loops which starts from zero by default. The `_resolve` method will store the `depth` argument in the `_locals` dictionary. So the `_locals` dictionary will look like this:

```python
{
    Variable(name=Token(self.token_type=<LiteralTokenType.IDENTIFIER: 'identifier'>,
                        self.lexeme='multiplier',
                        self.literal='multiplier',
                        self.line=3,
                        self.column=22)): 0,
    Variable(name=Token(self.token_type=<LiteralTokenType.IDENTIFIER: 'identifier'>,
                        self.lexeme='n',
                        self.literal='n',
                        self.line=3,
                        self.column=26)): 0
}
```

Now that we have the information we need for variable declaration, assignment stored away, let's move onto a few methods to access them when needed.

```python
    def _lookup_variable(self, name: "Token", expr: "Expr") -> t.Any:
        """Lookup a variable."""
        distance = self._locals.get(expr)
        if distance is not None:
            return self._environment.get_at(distance, name)
        return self._environment.get(name)
```

The `_lookup_variable` method first checks if the variable exists in the `_local` dictionary. If it does, it calls onto the methods of the `Environment` class to fetch it which we discussed some time back [here](environment.html). If the variable is not present in the `_local` dictionary, which indicates that the variable is a global variable, it calls onto the `get` method of the `Environment` class to fetch it.

## Evaluating Expressions

Lets start of with some basic expressions and operations to show how the interpreter works because at the core of any language is a bunch of expressions and then these expressions are used and conditions or tasks such as loops to evaluate a few more expressions.

### Grouping

```python
    def visit_grouping_expr(self, expr: Grouping) -> t.Any:
        """Evaluate a grouping expression."""
        return self._evaluate(expr.expression)
```

The `visit_grouping_expr` method is responsible for evaluating a grouping expression. The `visit_grouping_expr` method takes a `Grouping` instance as an argument. The `Grouping` instance has an `expression` attribute which is an expression node. The `visit_grouping_expr` method calls onto the `_evaluate` method of the `Interpreter` class with the `expression` attribute of the `Grouping` instance as an argument. The `_evaluate` method is responsible for evaluating the expression node.

### Unary

```python
    def visit_unary_expr(self, expr: "Unary") -> t.Any:
        """Visit a unary expression."""
        right: t.Any = self._evaluate(expr.right)
        match expr.operator.token_type:
            case SimpleTokenType.MINUS:
                self._numeric_validation(expr.operator, right)
                return -right
            case SimpleTokenType.BANG:
                return not self.is_truthy(right)
            case _:
                raise PyLoxRuntimeError(self.error(expr.operator, f"Unknown unary operator {expr.operator.lexeme}."))
```

The `visit_unary_method` is similar in operation in case of unary operations the `right` side is the expression or a value to which the unary operator is applied. In `Lox` language we have two unary operators, `!` and `-`. The `!` operator is used to negate the truthiness of the expression or value. The `-` operator is used to negate the expression or value.  
To apply these operators we need to first validate the expression or value. The `_numeric_validation` method is used to validate the expression or value.

- Numeric validation

```python
    def _numeric_validation(self, operator: "Token", *operands: t.Any) -> None:
        """Validate numeric operands."""
        for operand in operands:
            if not isinstance(operand, (int, float)):
                raise PyLoxTypeError(
                    self.error(operator, f"Operand must be a number for operator '{operator.lexeme}'.")
                )
        return None
```

Pretty straight forward, we check if the operand is an instance of `int` or `float` and if it is not we raise a `PyLoxTypeError` exception.

- Truthiness

```python
    @staticmethod
    def is_truthy(obj: t.Any) -> bool:
        """Check if an object is truthy."""
        return bool(obj)
```

Again nothing much for us to do here, we just call the `bool` function on the object and return the result. Cases like this show advantages of a high level languages like `Python`, `Java` etc.

### Binary

```python
    def visit_binary_expr(self, expr: "Binary") -> t.Any:
        """Visit a binary expression."""
        left, right = self._evaluate(expr.left), self._evaluate(expr.right)
        match expr.operator.token_type:
            case SimpleTokenType.MINUS:  # Subtraction
                self._numeric_validation(expr.operator, left, right)  # Validate numeric operands
                return left - right  # Perform subtraction
            case SimpleTokenType.PLUS:  # Addition
                if isinstance(left, str) and isinstance(right, str):  # Check if both operands are strings
                    return left + right  # Concatenate strings
                self._numeric_validation(expr.operator, left, right)  # Validate numeric operands
                raise PyLoxRuntimeError(self.error(expr.operator, "Operands must be two numbers or two strings."))
            case SimpleTokenType.SLASH:  # Division
                self._numeric_validation(expr.operator, left, right)  # Validate numeric operands
                try:
                    return left / right  # Perform division
                except ZeroDivisionError:
                    raise PyLoxRuntimeError(self.error(expr.operator, "Division by zero."))
            case ComplexTokenType.BACKSLASH:  # Integer division
                self._numeric_validation(expr.operator, left, right)
                try:
                    return left // right  # Perform integer division
                except ZeroDivisionError:
                    raise PyLoxRuntimeError(self.error(expr.operator, "Division by zero."))
            case SimpleTokenType.STAR:  # Multiplication
                self._numeric_validation(expr.operator, left, right)
                return left * right  # Perform multiplication
            case SimpleTokenType.MODULO:  # Modulo
                self._numeric_validation(expr.operator, left, right)
                return left % right  # Perform modulo
            case SimpleTokenType.CARAT:  # Exponentiation
                self._numeric_validation(expr.operator, left, right)
                return left**right  # Perform exponentiation
            case ComplexTokenType.GREATER:  # Greater than
                self._numeric_validation(expr.operator, left, right)
                return left > right  # Perform greater than
            case ComplexTokenType.GREATER_EQUAL:  # Greater than or equal to
                self._numeric_validation(expr.operator, left, right)
                return left >= right  # Perform greater than or equal to
            case ComplexTokenType.LESS:  # Less than
                self._numeric_validation(expr.operator, left, right)
                return left < right  # Perform less than
            case ComplexTokenType.LESS_EQUAL:  # Less than or equal to
                self._numeric_validation(expr.operator, left, right)
                return left <= right  # Perform less than or equal to
            case ComplexTokenType.BANG_EQUAL:  # Not equal to
                return not self.is_equal(left, right)  # Perform not equal to
            case ComplexTokenType.EQUAL_EQUAL:  # Equal to
                return self.is_equal(left, right)  # Perform equal to
            case _:
                raise PyLoxRuntimeError(
                    self.error(expr.operator, f"Unexpected binary operator {expr.operator.lexeme}.")
                )
```

I think you can figure out what’s going on here. The main difference from the unary negation operator is that we have two operands to evaluate. Nothing much to explain here.

```python
    @staticmethod
    def is_equal(left: t.Any, right: t.Any) -> bool:
        """Check if two objects are equal."""
        return left == right
```

We are just using the `==` operator to check if the two objects are equal.

So far we have seen how basic expressions are evaluated. Now let's use these bottom level expressions to see how statements are evaluated.

## Evaluating statements


### Expression statement

```python
    def visit_expression_stmt(self, stmt: "Expression") -> None:
        """Visit an expression statement."""
        self._evaluate(stmt.expression)
```

The `visit_expression_stmt` method is used to evaluate an expression statement. An expression statement is a statement that contains an expression. For example, `print "Hello World!"` is an expression statement. The `print` keyword is an expression and the string `"Hello World!"` is the expression.
In this case we just evaluate the expression and return the result.

```python
    def visit_print_stmt(self, stmt: "Print") -> None:
        """Visit a print statement."""
        value: t.Any = self._evaluate(stmt.expression)
        print(self._stringify(value))  # just calls str() on the value and handles special cases for nil and bool
```

Now that we have seen a basic statement evaluation, let's see how we can evaluate a block of statements.

### Blocks

```python
    def visit_block_stmt(self, stmt: "Block") -> None:
        """Visit a block statement."""
        self._execute_block(stmt.statements, Environment(enclosing=self.environment))
```

As the name of the method suggests it evaluates a block of statements. A block of statements is a group of statements enclosed in curly braces `{}`. For example, the body of a function is a block of statements. In this case we create a new environment enclosing the current environment and execute the block of statements in the new environment this ensures that the variables declared in the block are not accessible outside the block.

```python
    def _execute_block(self, statements: list["Stmt"], environment: Environment) -> None:
        """Execute a block of statements."""
        previous: Environment = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self._evaluate(statement)
        finally:
            self._environment = previous
```

Pretty standard what you expected it to do right? We just iterate over the statements and evaluate them.

### Variable declaration

```python
    def visit_var_stmt(self, stmt: "Var") -> None:
        """Visit a variable declaration statement."""
        value: t.Any = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)
        self._environment.define(stmt.name.lexeme, value)
```

This method is used to evaluate a variable declaration statement. A variable declaration statement is a statement that declares a variable. For example, `var a = 10` is a variable declaration statement. In this case we evaluate the initializer expression and store the result in the variable. If the initializer is not present we just store `None` in the variable in which case it defaults to `nil`.

### If statement

```python
    def visit_if_stmt(self, stmt: "If") -> None:
        """Visit an if statement."""
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._evaluate(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._evaluate(stmt.else_branch)
```

From this point onwards we will move onto features higher up in the hierarchy. The `visit_if_stmt` method is used to evaluate an if statement. An if statement is a statement that contains a condition and a then branch and an optional else branch.

Lets take a look at the `if` statement in Lox.

```js
var a = 2;
if (a > 2) {
    print "a is greater than 2";
}
else if (2 == a) {
    print "a is equal to 2";  // This is printed
}
else {
    print "a is less than 2";
}
```

The syntax of the `if` statement is pretty standard in this case we evaluate the `if` condition and if it is true we evaluate the then branch otherwise we evaluate the else branch in the case displayed above the else branch contains another `if` statement.

### While statement

```python
    def visit_while_stmt(self, stmt: "While") -> None:
        """Visit a while statement."""
        try:
            while self.is_truthy(self._evaluate(stmt.condition)):
                try:
                    self._evaluate(stmt.body)
                except PyLoxContinueError:
                    if stmt.for_transformed and isinstance(stmt.body, Block):
                        self._execute_block([stmt.body.statements[-1]], Environment(self._environment))
                        continue
                    continue
        except PyLoxRuntimeError:
            return
```

The implementation of `while` loop differs from the original Lox implementations due to addition of keywords like `continue` and `break`. Both these keywords raise respective error which is flagged by the interpreter and handled accordingly.

The little challenge here was handling the loop evaluation correctly when a `continue` statement is encountered. The `continue` statement is handled by the `PyLoxContinueError` exception. When the exception is raised we check if the loop is a `for` loop and if it is we execute the increment expression and continue the loop. If it is not a `for` loop we just continue the loop.

### Functions and Classes

```python
    def visit_function_stmt(self, stmt: "Function") -> None:
        """Visit a function declaration statement."""
        function: LoxFunction = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)
```

And yeah thats it! Surprised? Well, a function or class in general just a declaration. It is not evaluated until it is called. So we just create a new `LoxFunction` object and store it in the environment.

```python
    def visit_class_stmt(self, stmt: "Class") -> None:
        super_class = None  # super class flag
        if stmt.superclass is not None:  # if a super class is present
            super_class = self._evaluate(stmt.superclass)  # The super class is evaluated
            if not isinstance(super_class, LoxClass):  # If the super class is not a LoxClass
                raise PyLoxRuntimeError(
                    self.error(stmt.name, f"{stmt.superclass.name} must be an instance of LoxClass.")
                )
        self._environment.define(stmt.name, None)  # The class is defined in the environment
        if stmt.superclass is not None:  # If a super class is present
            self._environment = Environment(self._environment)  # A new environment is created
            self._environment.define(Token(KeywordTokenType.SUPER, "super", None, 0, 0), super_class)  # The super class is defined in the environment
        methods: t.Dict[str, LoxFunction] = {}
        for method in stmt.methods:  # all the methods are evaluated
            function_: LoxFunction = LoxFunction(method, self._environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function_
        new_class: LoxClass = LoxClass(stmt.name.lexeme, super_class, methods)  # A new LoxClass object is created
        if super_class is not None:
            assert isinstance(self._environment.enclosing, Environment)
            self._environment = self._environment.enclosing  # The environment is restored
        self._environment.assign(stmt.name, new_class)  # The class is assigned to the variable
```

Similarly, a class is also just a declaration. The class is not evaluated until it is used. So we just create a new `LoxClass` object and store it in the environment.
It gets slightly more complicated when a super class is present. In that case we create a new environment and store the super class in the environment. Then we evaluate all the methods in the new environment. After that we create a new `LoxClass` object and store it in the environment. Finally, we restore the environment and assign the `LoxClass` object to the variable.

### Calls

Now we get onto the real action. The `visit_call_expr` method is triggered whenver any function or class or a callable object in general is called. Lets take a look at the implementation.

```python
    def visit_call_expr(self, expr: "Call") -> t.Any:
        """Visit a call expression."""
        callee: t.Any = self._evaluate(expr.callee)
        arguments: t.List[t.Any] = [self._evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise PyLoxRuntimeError(self.error(expr.paren, "Can only call functions and classes."))
        if len(arguments) != callee.arity:
            raise PyLoxRuntimeError(self.error(expr.paren, f"Expected {callee.arity} arguments but got {len(arguments)}"))
        try:
            return callee(self, arguments)
        except Exception as e:
            self._logger.error(f"Error calling function {expr.paren.line}:{expr.paren.column}:\n{e}")
            raise PyLoxRuntimeError(self.error(expr.paren, f"Error calling function {expr.paren.line}:{expr.paren.column}:\n{e}"))
```

You might remember from the [parser](parser.html) stage that a `Call` object consists of the callee ie `foo(1, 2, 3)` in this case `foo` is the callee and the arguments ie `1, 2, 3` in this case. The callee is evaluated and the arguments are evaluated and stored in a list. Then we check if the callee is a callable object. If it is not we raise an error. If it is a callable object we check if the number of arguments passed is equal to the arity of the callee. If it is not we raise an error. If it is we call the callee with the arguments and return the result.

### Get and Set

```python
    def visit_get_expr(self, expr: "Get") -> t.Any:
        """Visit a get expression."""
        obj: t.Any = self._evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise PyLoxRuntimeError(self.error(expr.name, "Only instances have properties."))
```

```python
    def visit_set_expr(self, expr: "Set") -> t.Any:
        """Visit a set expression."""
        obj = self._evaluate(expr.object)
        if not isinstance(obj, LoxInstance):
            raise PyLoxRuntimeError(self.error(expr.name, "Only instances have fields."))
        value: t.Any = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value
```

The `visit_get_expr` method is triggered whenver a property of an instance is accessed. The `visit_set_expr` method is triggered whenver a property of an instance is set. In both cases we evaluate the object and check if it is an instance. If it is not we raise an error. If it is we get or set the property of the instance.

With this we have completed most of the general functionality of the interpreter. Now for the moment of truth. Lets run the interpreter and see if it works.

```python
# This is just a quick script to run the interpreter
from src import PyLox

if __name__ == "__main__":
    PyLox("test.lox").run()
```

Pylox is the interface class which allows us to interact with the interpreter. The `run` method runs the interpreter. Lets run the interpreter on the following code.

```js
class Node {
    init (value) {
        this.value = value;
        this.next = nil;
    }
}


class List {
    init() {
        this.head = nil;
        this.tail = nil;
    }

    add(value) {
        var node = Node(value);
        if (!this.head) {
            this.head = node;
            this.tail = node;
        } else {
            this.tail.next = node;
            this.tail = node;
        }
    }

    remove(value) {
        var node = this.head;
        var prev = nil;
        while (node) {
            if (node.value == value) {
                if (!prev) {
                    this.head = node.next;
                } else {
                    prev.next = node.next;
                }
                return;
            }
            prev = node;
            node = node.next;
        }
    }

    write() {
        var node = this.head;
        while (node) {
            print node.value;
            node = node.next;
        }
    }
}


var list = List();
for (var i = 0; i < 10; i = i + 1) {
    list.add(i);
}
for (var i = 0; i < 10; i = i + 1) {
    if (i % 2 == 0) {
        list.remove(i);
    }
}
list.write();
```

This code creates a linked list and removes all the even numbers from it. Lets run the interpreter.

```bash
[2023-05-01 03:08:04,953] | ~\src\interpreter\lox.py:58 | INFO | Running PyLox...
1
3
5
7
9
[2023-05-01 03:08:04,963] | ~\src\interpreter\lox.py:67 | INFO | Finished running PyLox.
```

It works! We have successfully implemented a working interpreter for the Lox language.

## Conclusion

Hey thats pretty cool! You have made it to the end of the series.
I learnt a lot while writing this interpreter. I hope you learnt something too. If you have any questions or suggestions feel free to contact me. I would love to hear from you. You can find the source code for this project [here](https://github.com/FallenDeity/LoxInterpreter).  

Going further I have added a bunch of additional features to the exisiting `Lox` implementation which can be found [here](tasks.html)

With that I bid you adieu. Until next time.

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
    <a class="btn-blue" href="../index.html" style="float: left;">Previous: Home</a>
    <a class="btn-blue" href="tasks.html" style="float: right;">Next: Tasks</a>
</html>
