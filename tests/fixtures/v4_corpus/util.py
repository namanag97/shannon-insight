"""Utilities with a bimodal implementation profile."""


def real_work(n):
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
    return total


def todo_a():
    pass


def todo_b():
    """Docstring only."""


def todo_c():
    raise NotImplementedError
