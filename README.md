# Termite

A CLI assistant that responds by generating a user interface in your terminal.

*Demo video goes here*

Termite is a new user experience for your terminal. It will generate a custom interface to help satisfy any request:

- "Show me which ports are currently active"
- "Diff these two SQLite tables"
- "Make a real-time feed of the messages in my Redis queue"

Normally you'd have to write a script or install another CLI tool for tasks like these. But with Termite, the right interface will be assembled on the spot for you in just a few seconds. You'll be surprised at how powerful your terminal becomes.

<!--Termite can also handle requests that don't need a custom interface. For example, ... .-->

Termite is also useful if you're building your own terminal applications. You can use it to bootstrap, kind of like [v0.dev](https://v0.dev/) but for TUIs.

## Quickstart

```bash
$ pip install termite-ai
```

## Examples

## How it works

Termite (**Term**inal **I**nterfaces for **T**ext **E**xpressions) is a code generation agent. It uses tools to create the TUI from a component library, adds logic to the TUI by writing code, and validates the output using a combination of GPT-4V and automated testing.

Adaptive computing in your terminal.
