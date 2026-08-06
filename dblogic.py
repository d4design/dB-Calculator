"""Core calculation logic for the decibel calculator.

Decibels are a logarithmic unit, so ordinary arithmetic doesn't apply
directly. Every value entered is treated as a dB level; before any
operation is performed it is converted to its linear power ratio,
the operation is carried out in linear space, and the result is
converted back to dB.

    linear = 10 ** (dB / 10)
    dB     = 10 * log10(linear)

For + and -, both operands are dB levels (e.g. combining or removing
a noise source), so both are converted to linear before the operation.

For x, / and %, the first operand is a dB level; the second operand is
treated as a plain multiplier/divisor/percentage applied to the linear
value (e.g. "10 identical sources" = level x 10), not itself a dB level.
"""

import math

OPS = ('+', '-', '×', '÷', '%')  # + - × ÷ %


class CalculatorError(Exception):
    pass


def db_to_linear(db):
    return 10 ** (db / 10)


def linear_to_db(linear):
    if linear <= 0:
        raise CalculatorError('Result undefined (non-positive energy)')
    return 10 * math.log10(linear)


def format_number(value):
    if abs(value) < 1e-9:
        value = 0.0
    text = f'{value:.1f}'
    if text == '-0.0':
        text = '0.0'
    return text


def apply_op(op, stored_db, operand2):
    """Apply op to stored_db (a dB level) and operand2, returning a dB result."""
    linear1 = db_to_linear(stored_db)
    if op == '+':
        result_linear = linear1 + db_to_linear(operand2)
    elif op == '-':
        result_linear = linear1 - db_to_linear(operand2)
    elif op == '×':
        result_linear = linear1 * operand2
    elif op == '÷':
        if operand2 == 0:
            raise CalculatorError('Cannot divide by zero')
        result_linear = linear1 / operand2
    elif op == '%':
        result_linear = linear1 * (operand2 / 100)
    else:
        raise CalculatorError(f'Unknown operator {op!r}')
    return linear_to_db(result_linear)


class DecibelCalculator:
    """State machine for a calculator-style UI, driven by button/key events."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.display = '0'
        self.expression = ''
        self.stored_db = None
        self.pending_op = None
        self.just_evaluated = False
        self.new_entry = True
        self.error = False

    def clear_entry(self):
        self.display = '0'
        self.new_entry = True
        self.error = False

    def input_digit(self, digit):
        if self.just_evaluated or self.error:
            self.reset()
        if self.new_entry:
            self.display = '0.' if digit == '.' else digit
            self.new_entry = False
        else:
            if digit == '.' and '.' in self.display:
                return
            if self.display == '0' and digit != '.':
                self.display = digit
            else:
                if len(self.display.replace('-', '').replace('.', '')) >= 15:
                    return
                self.display += digit

    def toggle_sign(self):
        if self.error:
            return
        if self.display.startswith('-'):
            self.display = self.display[1:]
        elif self.display != '0':
            self.display = '-' + self.display

    def backspace(self):
        if self.new_entry or self.error:
            return
        self.display = self.display[:-1]
        if self.display in ('', '-'):
            self.display = '0'
            self.new_entry = True

    def set_operator(self, op):
        if self.error:
            return
        if self.pending_op is not None and not self.new_entry:
            self.equals()
            if self.error:
                return
        self.stored_db = float(self.display)
        self.pending_op = op
        self.expression = f'{format_number(self.stored_db)} dB {op}'
        self.new_entry = True
        self.just_evaluated = False

    def equals(self):
        if self.pending_op is None or self.stored_db is None or self.error:
            return
        operand2 = float(self.display)
        op = self.pending_op
        try:
            result_db = apply_op(op, self.stored_db, operand2)
        except CalculatorError as exc:
            self.display = 'Error'
            self.expression = str(exc)
            self.pending_op = None
            self.stored_db = None
            self.just_evaluated = True
            self.new_entry = True
            self.error = True
            return
        self.expression = f'{format_number(self.stored_db)} dB {op} {format_number(operand2)} ='
        self.display = format_number(result_db)
        self.stored_db = result_db
        self.pending_op = None
        self.just_evaluated = True
        self.new_entry = True
