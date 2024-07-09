# Termite

A CLI assistant that responds by generating a UI in your terminal.

*Demo video goes here*

Termite is useful for getting stuff done in your terminal. Things that would normally require multiple bash commands get abstracted away into TUIs.

- "Help me diff these two SQLite tables"
- "Show me which ports are currently active"
- "Make a real-time feed of the messages in my Redis queue"

You can also use it to help bootstrap your own terminal applications. Kinda like [v0.dev](https://v0.dev/) for TUIs.

## Installation

```bash
$ pip install termite-ai
```

## How it works

Termite (**Term**inal **I**nterfaces for **T**ext **E**xpressions) is a code generation agent. It uses tools to create the TUI from a component library, adds logic to the TUI by writing code, and validates the output using a combination of GPT-4V and automated testing.
