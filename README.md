# Eeddword Password Generator

A desktop password generator built with Python and Tkinter. Generates cryptographically secure passwords and gives real-time feedback on strength and estimated crack time.

---

## Features

- **Cryptographically secure generation** via Python's `secrets` module
- **Configurable character sets** — uppercase, lowercase, digits, symbols, separators, and brackets (including Finnish characters Å, Ä, Ö)
- **Adjustable length** — slider from 4 to 72 characters
- **Entropy estimate** — displays bit strength with a rating (Weak → Excellent)
- **Crack time estimate** — powered by `zxcvbn`, showing estimates for both fast (specialized breach hardware) and slow (gaming PC) attack scenarios
- **One-click copy** to clipboard with confirmation feedback

---

## Requirements

- Python 3.10+
- [Pillow](https://pypi.org/project/Pillow/)
- [zxcvbn](https://pypi.org/project/zxcvbn/)

Install dependencies:

```bash
pip install pillow zxcvbn
```

---

## Usage

```bash
python eeddword.py
```

An optional `logo.png` in the same directory will be used as the window icon. If missing, the app still runs normally.

---

## Strength Rating

| Bits of entropy | Rating       |
|----------------|--------------|
| < 40           | Weak         |
| 40 – 71        | Fair         |
| 72 – 99        | Strong       |
| 100 – 127      | Very Strong  |
| 128+           | Excellent    |

Entropy is calculated from the character pool size implied by the password's contents, multiplied by password length: `log₂(pool_size) × length`.

---

## Notes

- Crack time estimates come from `zxcvbn` and reflect two threat models: offline fast hashing (10¹⁰ guesses/sec) and offline slow hashing (10⁴ guesses/sec).
- Passwords longer than 72 characters are reported as taking centuries to crack regardless of composition, as `zxcvbn` does not process beyond that length.
- The generated password is never stored or transmitted anywhere.

