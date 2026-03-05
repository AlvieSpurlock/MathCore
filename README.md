# PyCalc

PyCalc is a lightweight arithmetic utility designed to make basic math operations simple, readable, and easy to use in Python scripts. It provides a small collection of multi‑argument math functions — addition, subtraction, multiplication, division, modulo, even‑checking, and random integer generation — all wrapped in a clean, predictable API.

## Overview

PyCalc focuses on clarity and convenience. Instead of writing repetitive loops or manual arithmetic logic, PyCalc gives you a set of functions that accept a starting value and any number of additional values.

This makes PyCalc ideal for:

- Quick scripts

- Teaching environments

- Debugging utilities

- CLI tools

- Text‑based engines

- Any project that needs simple, readable math helpers

Its design is intentionally minimal — no classes, no dependencies, no overhead — just clean arithmetic functions.

## Why PyCalc?

Python already has arithmetic operators, but PyCalc solves a different problem: readability and convenience.

PyCalc provides:

- Multi‑argument operations (add(10, 2, 3, 4))

- Consistent function names

- A predictable interface

- A tiny footprint

- A built‑in debug UI for interactive testing

Instead of writing loops or chaining operators, PyCalc centralizes common math operations into a single, reusable module.

## Core Features

### Multi‑Argument Addition

```python
def add(start, *args):
    ...
```

Adds all values to the starting number.

### Multi‑Argument Subtraction

```python
def sub(start, *args):
    ...
```

### Multi‑Argument Multiplication

```python
def multi(start, *args):
    ...
```

### Multi‑Argument Division

```python
def div(start, *args):
    ...
```

### Even Number Check

```python
def IsEven(var):
    return var % 2 == 0
```

### Modulo Operation
```python
def mod(base, var):
    return base % var
```

### Random Integer Generator
```python
def rand(mi, ma):
    return randint(mi, ma)
```

## Debug UI

PyCalc includes a simple interactive testing interface:

```python
def debug():
    results = [0, 1, 2, 3, 4, 5, 6]
    results[0] = add(int(input("Give Number To Add:")), int(input("Add By:")))
    results[1] = sub(int(input("Give Number To Subtract:")), int(input("Subtract By:")))
    results[2] = multi(int(input("Give Number To Multiply:")), int(input("Multiply By:")))
    results[3] = div(int(input("Give Number To Divide:")), int(input("Divide By:")))
    results[4] = IsEven(int(input("Give Number To Check If Even:")))
    results[5] = mod(int(input("Give Number To Modulo:")), int(input("Modulo By:")))
    results[6] = rand(int(input("Give Min Range For Random Int:")), int(input("Give Max Range For Random Int:")))

    for num, result in enumerate(results):
        print(num + 1, ":", result)
```

This allows you to test every function interactively from the console.

## Example Usage

```python
from PyCalc import add, sub, multi, div, IsEven, mod, rand

print(add(10, 5, 2))       # 17
print(sub(20, 3, 2))       # 15
print(multi(2, 3, 4))      # 24
print(div(100, 2, 5))      # 10
print(IsEven(42))          # True
print(mod(17, 5))          # 2
print(rand(1, 10))         # Random int between 1 and 10
```

## Class Structure

```python
def add(start, *args): ...
def sub(start, *args): ...
def multi(start, *args): ...
def div(start, *args): ...
def IsEven(var): ...
def mod(base, var): ...
def rand(mi, ma): ...
def debug(): ...
```

(Full implementation included in repository.)

## Summary

PyCalc is a tiny, dependency‑free arithmetic helper library built for readability and convenience. With multi‑argument operations, a consistent API, and an optional debug UI, it’s a simple but effective tool for scripts, teaching, and CLI utilities.

Requires: Python 3.x
