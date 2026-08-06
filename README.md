# dB Calculator

A Windows desktop calculator that performs arithmetic on decibel (dB) values correctly — by converting to linear power ratios before combining values, then converting back to dB — instead of naively adding/subtracting the dB numbers themselves.

![Python](https://img.shields.io/badge/python-3.x-blue) ![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## Why

Decibels are a logarithmic unit, so ordinary arithmetic doesn't apply directly. For example, combining two 60 dB noise sources doesn't give 120 dB — it gives 63 dB. This tool handles that conversion automatically so you can work with dB values the way they actually behave physically.

## How it works

Every value entered is treated as a dB level. Before an operation is performed it's converted to its linear power ratio, the operation is carried out in linear space, and the result is converted back to dB:

```
linear = 10 ^ (dB / 10)
dB     = 10 * log10(linear)
```

- **`+` and `-`** — both operands are dB levels (e.g. combining or removing a noise source). Both are converted to linear before the operation.
- **`×`, `÷` and `%`** — the first operand is a dB level; the second operand is a plain multiplier/divisor/percentage applied to the linear value (e.g. "10 identical sources" = level × 10), not itself a dB level.

## Requirements

- Windows
- Python 3 with `tkinter` (included in the standard CPython installer for Windows)

No third-party dependencies.

## Running it

Double-click [DecibelCalculator.pyw](DecibelCalculator.pyw), or run it from a terminal:

```bash
pythonw DecibelCalculator.pyw
```

A shortcut ([dB Calculator.lnk](dB%20Calculator.lnk)) and icon ([db_calculator.ico](db_calculator.ico)) are included for pinning to the Start Menu or taskbar.

## Usage

Standard calculator layout and keyboard support:

| Keys | Action |
|---|---|
| `0-9`, `.` | Enter digits |
| `+` `-` `*` `/` `%` | Operators |
| `Enter` / `=` | Evaluate |
| `Backspace` | Delete last digit |
| `Esc` | Clear (C) |
| `Delete` | Clear entry (CE) |

The `±` button toggles the sign of the current entry. The window is resizable; fonts scale with window size.

## Project structure

| File | Purpose |
|---|---|
| [dblogic.py](dblogic.py) | Core calculation logic and calculator state machine (UI-independent) |
| [DecibelCalculator.pyw](DecibelCalculator.pyw) | Tkinter UI |
