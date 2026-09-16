"""A small, safe expression evaluator.

Python's eval() would be much shorter, but it would also happily run
any code that ends up in the display. This uses a tokeniser and the
shunting-yard algorithm instead, which is safer and nicer to explain.
"""

import math


class CalculatorError(Exception):
    pass


# symbol: (precedence, associativity)
OPERATORS = {
    "+": (1, "left"),
    "-": (1, "left"),
    "*": (2, "left"),
    "/": (2, "left"),
    "%": (2, "left"),
    "^": (3, "right"),
    "u": (4, "right"),  # unary minus
}


# Tokenising
def parse_number(text):
    try:
        return float(text)
    except ValueError:
        raise CalculatorError(f"'{text}' is not a number.")


def tokenise(expression):
    tokens = []
    number = ""

    for character in expression:

        if character.isdigit() or character == ".":
            number += character
            continue

        if number:
            tokens.append(parse_number(number))
            number = ""

        if character.isspace():
            continue

        if character in "()":
            tokens.append(character)

        elif character in OPERATORS:
            previous = tokens[-1] if tokens else None

            # A minus is unary at the start, or after another
            # operator or an opening bracket.
            follows_value = (
                previous is not None
                and (not isinstance(previous, str) or previous == ")")
            )

            if character == "-" and not follows_value:
                tokens.append("u")
            else:
                tokens.append(character)

        else:
            raise CalculatorError(f"'{character}' can't be used here.")

    if number:
        tokens.append(parse_number(number))

    return tokens


# Shunting-yard
def to_postfix(tokens):
    output = []
    stack = []

    for token in tokens:

        if not isinstance(token, str):
            output.append(token)

        elif token == "(":
            stack.append(token)

        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())

            if not stack:
                raise CalculatorError("Missing an opening bracket.")

            stack.pop()

        else:
            precedence, associativity = OPERATORS[token]

            while stack and stack[-1] != "(":
                top_precedence = OPERATORS[stack[-1]][0]

                if top_precedence > precedence or (
                    top_precedence == precedence
                    and associativity == "left"
                ):
                    output.append(stack.pop())
                else:
                    break

            stack.append(token)

    while stack:
        operator = stack.pop()

        if operator == "(":
            raise CalculatorError("Missing a closing bracket.")

        output.append(operator)

    return output


# Evaluating
def evaluate_postfix(tokens):
    stack = []

    for token in tokens:

        if not isinstance(token, str):
            stack.append(token)
            continue

        if token == "u":
            if not stack:
                raise CalculatorError("That expression isn't finished.")

            stack.append(-stack.pop())
            continue

        if len(stack) < 2:
            raise CalculatorError("That expression isn't finished.")

        right = stack.pop()
        left = stack.pop()

        if token == "+":
            stack.append(left + right)

        elif token == "-":
            stack.append(left - right)

        elif token == "*":
            stack.append(left * right)

        elif token == "/":
            if right == 0:
                raise CalculatorError("Can't divide by zero.")

            stack.append(left / right)

        elif token == "%":
            if right == 0:
                raise CalculatorError("Can't divide by zero.")

            stack.append(math.fmod(left, right))

        elif token == "^":
            try:
                stack.append(left ** right)
            except (OverflowError, ValueError):
                raise CalculatorError("That number is too big.")

    if len(stack) != 1:
        raise CalculatorError("That expression isn't finished.")

    return stack[0]


def evaluate(expression):
    # The buttons use nicer looking symbols than Python does.
    cleaned = (
        expression
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
    )

    if not cleaned.strip():
        raise CalculatorError("Nothing to work out.")

    result = evaluate_postfix(to_postfix(tokenise(cleaned)))

    if math.isinf(result) or math.isnan(result):
        raise CalculatorError("That result isn't a number.")

    return result


def format_result(value):
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))

    return f"{round(value, 10):g}"