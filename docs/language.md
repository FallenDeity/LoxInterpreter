# Language Design

> 📝 **Note**  
> Currently in early stage all language design decisions will follow the tutorial and examples from [here](https://www.craftinginterpreters.com/the-lox-language.html).

## First Look

```js
// This is a comment
print "Hello, World!";
```

Current `Lox` will follow syntax of C-like languages, but with some differences. It will have the following features:

- Dynamic typing
- Automatic memory management (garbage collection)

## Data Types

`Lox` will have the following data types:

- Booleans

    ```js
    true;
    false;
    ```

- Numbers

    ```js
    123;
    123.456;
    ```

- Strings

    ```js
    "Hello, World!";
    ""; // Empty string
    ```

- Nil

    ```js
    nil;
    ```

## Expressions

`Lox` will have the following expressions:

- Arithmetic

    ```js
    1 + 2;
    3 - 4;
    5 * 6;
    7 / 8;
    -9;  // prefix
    ```

- Comparison

    ```js
    1 > 2;
    3 < 4;
    5 >= 6;
    7 <= 8;
    123 == 456;
    123 != 456;
    ```  

- Logical

    ```js
    true and false;
    true or false;
    !true;
    ```

- Grouping

    ```js
    (1 + 2) * 3;
    ```

## Statements

A statement's job is to produce some effect. They are executed for their side effects such as output, input, or assignment and modification of variables.

## Variables

Variables are used to store values. They are created with the `var` keyword.

```js
var a = 1;
var b;  // Uninitialized variable defaults to `nil`
```

## Control Flow

`Lox` will have the following control flow statements:

- `if`

    ```js
    if (true) {
        print "true";
    } else {
        print "false";
    }
    ```

- `while`

    ```js
    while (true) {
        print "true";
    }
    ```

- `for`

    ```js
    for (var i = 0; i < 10; i = i + 1) {
        print i;
    }
    ```

## Functions

Functions are used to group statements together to perform some task. They are created with the `fun` keyword.

```js
fun add(a, b) {
    return a + b;
}


fun main() {
    print add(1, 2);  // returns `nil` since main() doesn't return anything
}
```

Functions are considered first-class citizens in `Lox`. This means that they can be passed around like any other value.

```js
fun add(a, b) {
    return a + b;
}

fun main() {
    var adder = add;
    print adder(1, 2);
}
```

```js
fun wrapper()
{
	fun inner()
	{
		print "Hello, World!";
	}
}
```

## Classes

There are two ways to approach objects in `OOP`:

- **Class-based**: Objects are instances of classes, and classes inherit from other classes.
- **Prototype-based**: Objects are instances of other objects, and objects inherit from other objects.

### Class-based

In class-based languages, classes are the blueprints for objects. They define what properties and methods an object will have. Objects are instances of classes.
Instances store state in fields, and behavior is defined by methods.

![Class-based](https://craftinginterpreters.com/image/the-lox-language/class-lookup.png)

### Prototype-based

In prototype-based languages, objects are the blueprints for objects. They define what properties and methods an object will have. Objects are instances of other objects.

![Prototype-based](https://craftinginterpreters.com/image/the-lox-language/prototype-lookup.png)

### `Lox` Approach

`Lox` will follow the class-based approach.

```js
class Person {
    init(name) {
        this.name = name;
    }

    greet() {
        print "Hello, my name is " + this.name + ".";
    }
}


var person = Person("John");
person.greet();
```

### Inheritance in `Lox`

```js
class Person {
    init(name) {
        this.name = name;
    }

    greet() {
        print "Hello, my name is " + this.name + ".";
    }
}


class Student < Person {
    init(name, id) {
        super.init(name);
        this.id = id;
    }

    greet() {
        super.greet();
        print "My student ID is " + this.id + ".";
    }
}
```

## Standard Library

For now standard libraries in `Lox` will be limited to the default `clock()` method. I will slowly add other methods to give it basic functionality.

### TODO

- [ ] Add `IO` methods
- [ ] Add `Math` methods
- [ ] Add `String` methods
- [ ] Add `Network` methods
- [ ] Add `File` methods

## `PyLox` our Interpreter

`PyLox` is a tree walk interpreter written in `Python`. It will be used as the default interpreter for `Lox`.

## References

- [Crafting Interpreters](https://www.craftinginterpreters.com/the-lox-language.html)

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
    <a class="btn-blue" href="./" style="float: left;">Previous: Home</a>
    <a class="btn-blue" href="./docs/scanner.html" style="float: right;">Next: Scanner</a>
</html>
