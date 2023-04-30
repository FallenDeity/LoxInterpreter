* [Resolver](#resolver)
  * [Semantic Analysis](#semantic-analysis)
  * [Resolver Class](#resolver-class)
    * [Blocks](#blocks)
    * [Functions](#functions)
    * [Classes](#classes)
  * [Running the Resolver](#running-the-resolver)

# Resolver

Previously we add environments or rather scoping for blocks and variables [here](environment.html) but our language `Lox` includes closures where we consider functions as first class citizens. This means that functions can be passed around as values and can be stored in variables. This also means that functions can be defined inside other functions and can access variables from the enclosing function. This is where we need to introduce the concept of `Resolver` which is responsible for resolving and binding variables.

Take the following example:

```javascript
fun makeCounter() {
  var i = 0;
  fun count() {
    i = i + 1;
    print i;
  }

  return count;
}

var counter = makeCounter();
counter(); // "1".
counter(); // "2".
```

In the above example, the function `makeCounter` returns another function `count` which is stored in the variable `counter`. When we call `counter` it prints `1` and `2` on the console. This is because the function `count` has access to the variable `i` which is defined in the enclosing function `makeCounter`. This is called a closure.

So if we try to run it currently, we will get an error saying that the variable `i` is not defined. This is because the variable `i` is not defined in the current scope. It is defined in the enclosing scope. So we need to resolve the variable `i` in the enclosing scope.

So in this case to solve this issue we need to capture the current active environment when the function is declared and store it in the function object. Then when the function is called we need to set the environment of the function to the captured environment. This way the function will have access to the variables in the enclosing scope.

![Closure](https://craftinginterpreters.com/image/functions/closure.png)

## Semantic Analysis

When we made our parser, we made sure the parser was able to tell which programs were `syntactically` valid and which were not. But we still need to check if the program is `semantically` valid. This means that the program is syntactically valid and also makes sense. For example, the following program is syntactically valid but semantically invalid.

```javascript
return 1;  // return is not inside a function.
```

So we need to make sure that the program is semantically valid. The `Resolver` is responsible for resolving and binding variables. It is also responsible for checking if the program is semantically valid. So we need to make sure that the `Resolver` is run before the interpreter.  

## Resolver Class

```python
class Resolver(StmtProtocol, VisitorProtocol):  # we since original book was in java, but python dosent support overloading, we need to use protocol in short it has no run time affect other than reminding us to implement the methods for each function defined in the protocol

    def __init__(self, interpreter: "Interpreter") -> None:
        self._interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function: FunctionType = FunctionType.NONE  # NONE, FUNCTION, INITIALIZER, METHOD
        self.current_class: ClassType = ClassType.NONE  # NONE, CLASS, SUBCLASS
        self.current_loop: LoopyType = LoopyType.NONE  # NONE, WHILE reason we dont have FOR is any for loop can be converted to while loop for just acts as syntactic sugar
```

Basic resolver class nothing much to explain here, we have a list of scopes, current function, current class and current loop. Lets us now define methods for the resolver class.

- BeginScope

```python
    def _begin_scope(self) -> None:
        self.scopes.append({})
```

This method is used to begin a new scope. We do this by appending a new dictionary to the list of scopes.

- EndScope

```python
    def _end_scope(self) -> None:
        self.scopes.pop()
```

This method is used to end the current scope. We do this by popping the last dictionary from the list of scopes.

- ResolveOne

```python
    def _resolve_one(self, expr: t.Union["Stmt", "Expr"]) -> None:
        expr.accept(self)  # this is the visitor pattern common to all Stmt and Expr classes
```

Remeber when we defined dataclasses for different statements and expressions, we made sure that they all had an accept method which accepted a visitor. This is the visitor pattern. We will use this pattern to traverse the AST and resolve variables.

For example, if we have the following code:

```python
class Stmt:
    def foo(self, visitor: "VisitorProtocol") -> None:
        pass


class RandomStmt(Stmt):
    def foo(self, visitor: "VisitorProtocol") -> None:
        visitor.visit_random_stmt(self)
```

So now when we call `foo` on `RandomStmt` it will call `visit_random_stmt` on the visitor. So we can define a visitor like this:

```python
class MyVisitor(VisitorProtocol):
    def visit_random_stmt(self, stmt: RandomStmt) -> None:
        print("RandomStmt")

    def visit(self, stmt: Stmt) -> None:
        stmt.accept(self)
```

- Resolve

```python
    def _resolve(self, statements: t.Sequence[t.Union["Stmt", "Expr"]]) -> None:
        try:
            for statement in statements:
                self._resolve_one(statement)
        except PyLoxResolutionError as e:
            self._interpreter._logger.error(e)
            raise e
```

This is the main method which is used to resolve variables. We pass in a list of statements which we recieve from the parser. We then iterate over each statement and call `_resolve_one` on it. If we encounter an error we log it and raise it.

- Declare

```python
    def _declare(self, name: Token) -> None:
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise PyLoxResolutionError(
                name, f"Variable with name {name.lexeme} already declared in this scope."
            )

        scope[name.lexeme] = False
```

Declaration adds a new variable to the current scope. We first check if there is a current scope. If there is no current scope we return. If there is a current scope we check if the variable is already declared in the current scope. If it is already declared we raise an error. If it is not declared we add it to the current scope.

- Define

```python
    def _define(self, name: Token) -> None:
        if not self.scopes:
            return

        self.scopes[-1][name.lexeme] = True
```

Definition marks a variable as defined. We first check if there is a current scope. If there is no current scope we return. If there is a current scope we mark the variable as defined.

- ResolveLocal

```python
    def _resolve_local(self, expr: "Expr", name: "Token") -> None:
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self._interpreter._resolve(expr, i)
                return
```

This method is used to resolve a variable in the current scope. We first iterate over the scopes in reverse order. We then check if the variable is declared in the current scope. If it is declared we resolve the variable.
The interpreter has a method called `_resolve` which is used to resolve a variable. We pass in the expression and the distance of the variable from the current scope. The distance is the number of scopes between the current scope and the scope in which the variable is declared.
We will see how this works later.  

Now that we have defined all the methods for the resolver class, let us define the methods for the visitor pattern. Since this more of an explanation report I won't define all the methods here. You can find the full code [here](https://github.com/FallenDeity/LoxInterpreter/blob/master/src/interpreter/resolver.py).

These are the following methods we will define:

- Blocks
- Functions
- Classes

### Blocks

Resolving blocks are an integral part of the resolver class since majority of the code is in blocks be it functions, loops or classes.

```python
    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()
```

We first begin a new scope. We then resolve all the statements in the block. We then end the scope. If you remember we defined a method called `_resolve` which takes in a list of statements and resolves them. We use that method here to resolve all the statements in the block.

### Functions

For resolving functions we will make a common method so we can reuse it for functions, lambdas and methods.

```python
    def _resolve_function(self, function: t.Union["Function", "Lambda"], type_: FunctionType) -> None:
        enclosing_function = self.current_function  # save the current function
        self.current_function = type_  # set the current function to the type of function we are resolving

        self._begin_scope()  # begin a new scope
        for param in function.params:  # declare and define all the parameters
            self._declare(param)  # declare the parameter
            self._define(param)  # define the parameter

        self._resolve(function.body)  # resolve the body of the function
        self._end_scope()  # end the scope

        self.current_function = enclosing_function  # restore the current function
```

We first save the current function. We then set the current function to the type of function we are resolving. We then begin a new scope. We then declare and define all the parameters. We then resolve the body of the function. We then end the scope. We then restore the current function.

```python
    def visit_function_stmt(self, stmt: Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)
```

We first declare and define the function. We then resolve the function.

```python
    def visit_lambda_expr(self, expr: Lambda) -> None:
        self._resolve_function(expr, FunctionType.LAMBDA)  # resolve the lambda
```

### Classes

```python
    def visit_class_stmt(self, stmt: "Class") -> t.Any:
        enclosing_class = self.current_class  # save the current class
        self.current_class = ClassType.CLASS  # set the current class to class
        self._declare(stmt.name)  # declare the class
        self._define(stmt.name)  # define the class
        if stmt.superclass is not None:  # check if the class inherits from another class
            self.current_class = ClassType.SUBCLASS  # set the current class to subclass
            if stmt.name.lexeme == stmt.superclass.name.lexeme:  # check if the class inherits from itself
                raise PyLoxResolutionError(
                    self._interpreter.error(stmt.superclass.name, "A class cannot inherit from itself.")
                )
            self._resolve_one(stmt.superclass)  # resolve the superclass
            self._begin_scope()  # begin a new scope
            self.scopes[-1]["super"] = True  # declare and define super
        self._begin_scope()  # begin a new scope
        self.scopes[-1]["this"] = True  # declare and define this equivalent to self in python
        for method in stmt.methods:  # resolve all the methods
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":  # check if the method is an initializer equivalent to __init__ in python
                declaration = FunctionType.INITIALIZER
            self._resolve_function(method, declaration)  # resolve the method
        self._end_scope()  # end the scope
        if stmt.superclass is not None:
            self._end_scope()  # end the scope
        self.current_class = enclosing_class
        return None
```

Resolving classes is a bit more tricky than functions because of the way inheritance works and operation of class instance `this` and `super`.
There a few edges cases which I'll show which will also explain why we track the current class, function and scope.

Say a user defines a class like this:

```js
class A {
    init() {
        return 10;  // this is not allowed since init must return the initialized class instance
    }
}
```

So for cases such as this we have to track and handle in this particular case the `init` method differently. We do this by checking if the method is an initializer and if it is we set the declaration to `FunctionType.INITIALIZER` and then resolve the method.

```python
    def visit_return_stmt(self, stmt: "Return") -> t.Any:
        if self.current_function == FunctionType.NONE:  # check if we are in a function
            raise PyLoxResolutionError(self._interpreter.error(stmt.keyword, "Cannot return from top-level code."))
        if stmt.value is not None:  # check if the return statement has a value
            if self.current_function == FunctionType.INITIALIZER:  # check if we are in an initializer
                raise PyLoxResolutionError(
                    self._interpreter.error(stmt.keyword, "Cannot return a value from an initializer.")
                )
            self._resolve_one(stmt.value)
        return None
```

This how `return` statements are handled and checks for weird edge cases and semantics.

With this we conclude the basic implementation of the resolver. Now it's time to run it and see if it works.

## Running the Resolver

```
class Foo {
    init () {
        return 1;  // expected error
    }
}

var foo = Foo();
```
```
  File "C:\Users\FallenDeity\PycharmProjects\Lox\src\interpreter\resolver.py", line 232, in visit_return_stmt
    raise PyLoxResolutionError(
src.exceptions.PyLoxResolutionError: EX_SOFTWARE: RuntimeError at line 3:15
        return 1;
~~~~~~~~~~~~~~~^
Cannot return a value from an initializer.
```

With that we have successfully implemented the resolver. Now we can move on to the final and most exciting phase of the interpreter, the interpreter itself.

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
    <a class="btn-blue" href="environment.html" style="float: left;">Previous: Environment</a>
    <a class="btn-blue" href="interpreter.html" style="float: right;">Next: Interpreter</a>
</html>
