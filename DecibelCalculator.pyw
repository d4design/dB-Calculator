"""Decibel Calculator - a standard-looking calculator that does its
arithmetic logarithmically, as decibel levels should be combined.

Run by double-clicking this file (requires pythonw / a Python install
with tkinter, which ships with standard CPython on Windows).
"""

import tkinter as tk
from tkinter import font as tkfont

from dblogic import DecibelCalculator, OPS

BG = '#1e1e1e'
DISPLAY_BG = '#1e1e1e'
EXPR_FG = '#9a9a9a'
DISPLAY_FG = '#ffffff'
BTN_NUM_BG = '#333333'
BTN_NUM_FG = '#ffffff'
BTN_NUM_ACTIVE = '#454545'
BTN_FUNC_BG = '#2a2a2a'
BTN_FUNC_FG = '#ffffff'
BTN_FUNC_ACTIVE = '#3d3d3d'
BTN_OP_BG = '#3a3a3a'
BTN_OP_FG = '#ff9f43'
BTN_OP_ACTIVE = '#4d4d4d'
BTN_OP_SELECTED_BG = '#ff9f43'
BTN_OP_SELECTED_FG = '#1e1e1e'
BTN_EQ_BG = '#ff9f43'
BTN_EQ_FG = '#1e1e1e'
BTN_EQ_ACTIVE = '#ffb35c'


class DecibelCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.calc = DecibelCalculator()
        self.op_buttons = {}

        # Reference size at which fonts are their defined (100%) size.
        self.font_base_w, self.font_base_h = 320, 480
        # Actual default window size (150% of the font reference size).
        self.default_w, self.default_h = 480, 720

        root.title('Decibel Calculator')
        root.configure(bg=BG)
        root.resizable(True, True)
        root.minsize(240, 360)
        root.geometry(f'{self.default_w}x{self.default_h}')

        self._build_fonts()
        self._build_display()
        self._build_keypad()
        self._bind_keys()
        self._refresh()

        root.bind('<Configure>', self._on_resize)

    def _build_fonts(self):
        self.expr_font = tkfont.Font(family='Segoe UI', size=11)
        self.display_font = tkfont.Font(family='Segoe UI', size=36, weight='bold')
        self.unit_font = tkfont.Font(family='Segoe UI', size=12)
        self.btn_font = tkfont.Font(family='Segoe UI', size=16)
        self.eq_font = tkfont.Font(family='Segoe UI', size=18, weight='bold')

    def _on_resize(self, event):
        if event.widget is not self.root:
            return
        scale = min(event.width / self.font_base_w, event.height / self.font_base_h)
        scale = max(0.6, min(scale, 4.0))
        self.expr_font.configure(size=max(8, round(11 * scale)))
        self.display_font.configure(size=max(16, round(36 * scale)))
        self.unit_font.configure(size=max(8, round(12 * scale)))
        self.btn_font.configure(size=max(9, round(16 * scale)))
        self.eq_font.configure(size=max(10, round(18 * scale)))

    def _build_display(self):
        frame = tk.Frame(self.root, bg=DISPLAY_BG)
        frame.pack(fill='both', expand=False, padx=0, pady=(20, 10))

        self.expr_label = tk.Label(
            frame, text='', anchor='e', bg=DISPLAY_BG, fg=EXPR_FG,
            font=self.expr_font,
        )
        self.expr_label.pack(fill='x', padx=16)

        self.display_label = tk.Label(
            frame, text='0', anchor='e', bg=DISPLAY_BG, fg=DISPLAY_FG,
            font=self.display_font,
        )
        self.display_label.pack(fill='x', padx=16, pady=(4, 0))

        self.unit_label = tk.Label(
            frame, text='dB', anchor='e', bg=DISPLAY_BG, fg=EXPR_FG,
            font=self.unit_font,
        )
        self.unit_label.pack(fill='x', padx=16)

    def _build_keypad(self):
        grid = tk.Frame(self.root, bg=BG)
        grid.pack(fill='both', expand=True, padx=10, pady=10)

        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform='col')
        for row in range(6):
            grid.grid_rowconfigure(row, weight=1, uniform='row')

        rows = [
            [('%', 'op'), ('CE', 'func'), ('C', 'func'), ('⌫', 'func')],
            [('7', 'num'), ('8', 'num'), ('9', 'num'), ('÷', 'op')],
            [('4', 'num'), ('5', 'num'), ('6', 'num'), ('×', 'op')],
            [('1', 'num'), ('2', 'num'), ('3', 'num'), ('−', 'op')],
            [('±', 'func'), ('0', 'num'), ('.', 'num'), ('+', 'op')],
        ]

        for r, row in enumerate(rows):
            for c, (label, kind) in enumerate(row):
                btn = self._make_button(grid, label, kind, self.btn_font)
                btn.grid(row=r, column=c, sticky='nsew', padx=4, pady=4)

        eq_btn = tk.Button(
            grid, text='=', font=self.eq_font, bg=BTN_EQ_BG, fg=BTN_EQ_FG,
            activebackground=BTN_EQ_ACTIVE, activeforeground=BTN_EQ_FG,
            bd=0, relief='flat', command=self.on_equals,
        )
        eq_btn.grid(row=5, column=0, columnspan=4, sticky='nsew', padx=4, pady=4)

    def _make_button(self, parent, label, kind, font):
        if kind == 'num':
            bg, fg, active = BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_ACTIVE
        elif kind == 'func':
            bg, fg, active = BTN_FUNC_BG, BTN_FUNC_FG, BTN_FUNC_ACTIVE
        else:
            bg, fg, active = BTN_OP_BG, BTN_OP_FG, BTN_OP_ACTIVE

        btn = tk.Button(
            parent, text=label, font=font, bg=bg, fg=fg,
            activebackground=active, activeforeground=fg,
            bd=0, relief='flat', highlightthickness=0,
        )

        if kind == 'num':
            btn.configure(command=lambda d=label: self.on_digit(d))
        elif label == 'C':
            btn.configure(command=self.on_clear)
        elif label == 'CE':
            btn.configure(command=self.on_clear_entry)
        elif label == '⌫':
            btn.configure(command=self.on_backspace)
        elif label == '±':
            btn.configure(command=self.on_toggle_sign)
        elif kind == 'op':
            op_symbol = {'÷': '÷', '×': '×', '−': '-', '+': '+', '%': '%'}[label]
            btn.configure(command=lambda o=op_symbol: self.on_operator(o))
            self.op_buttons[op_symbol] = btn

        return btn

    def _bind_keys(self):
        root = self.root
        for digit in '0123456789':
            root.bind(digit, lambda e, d=digit: self.on_digit(d))
        root.bind('.', lambda e: self.on_digit('.'))
        root.bind('<KP_Decimal>', lambda e: self.on_digit('.'))
        root.bind('+', lambda e: self.on_operator('+'))
        root.bind('-', lambda e: self.on_operator('-'))
        root.bind('*', lambda e: self.on_operator('×'))
        root.bind('/', lambda e: self.on_operator('÷'))
        root.bind('%', lambda e: self.on_operator('%'))
        root.bind('<Return>', lambda e: self.on_equals())
        root.bind('<KP_Enter>', lambda e: self.on_equals())
        root.bind('=', lambda e: self.on_equals())
        root.bind('<BackSpace>', lambda e: self.on_backspace())
        root.bind('<Escape>', lambda e: self.on_clear())
        root.bind('<Delete>', lambda e: self.on_clear_entry())

    # --- event handlers -------------------------------------------------

    def on_digit(self, digit):
        self.calc.input_digit(digit)
        self._refresh()

    def on_operator(self, op):
        self.calc.set_operator(op)
        self._refresh()

    def on_equals(self):
        self.calc.equals()
        self._refresh()

    def on_clear(self):
        self.calc.reset()
        self._refresh()

    def on_clear_entry(self):
        self.calc.clear_entry()
        self._refresh()

    def on_backspace(self):
        self.calc.backspace()
        self._refresh()

    def on_toggle_sign(self):
        self.calc.toggle_sign()
        self._refresh()

    # --- rendering --------------------------------------------------------

    def _refresh(self):
        self.display_label.config(text=self.calc.display)
        self.expr_label.config(text=self.calc.expression)
        self.unit_label.config(text='' if self.calc.error else 'dB')

        for op, btn in self.op_buttons.items():
            if op == self.calc.pending_op and self.calc.new_entry:
                btn.configure(bg=BTN_OP_SELECTED_BG, fg=BTN_OP_SELECTED_FG)
            else:
                btn.configure(bg=BTN_OP_BG, fg=BTN_OP_FG)


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default='')
    except Exception:
        pass
    DecibelCalculatorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
