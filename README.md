# 🐛 Termite

Generate terminal UIs (TUIs) with simple text prompts.

![Demo](assets/demo.gif)

Termite lets you quickly prototype a terminal app to solve a problem. It works well for tasks like:

- "Show me which ports are active"
- "Make me a throughput monitor for my Redis queue"
- "Help me manage my Docker containers"
- "Diff these two SQL tables"

Under the hood, an LLM is generating and auto-executing a Python script that implements the UI. By default, UIs are built with the [urwid](https://urwid.org/) library, but you can also use [rich](https://rich.readthedocs.io/en/latest/), [curses](https://docs.python.org/3/library/curses.html), or [textual](https://textual.textualize.io/).

Please use with caution. Termite is still very experimental and it's obviously risky to run AI-generated code.

## Installation

```bash
> pipx install termite-ai
```

Once installed, Termite uses [LiteLLM](https://litellm.ai/) to connect to a wide range of LLM providers (100+). You need to set the appropriate environment variables for your chosen provider.

**Common Environment Variables:**

```bash
# For OpenAI Models (e.g., GPT-4o, GPT-3.5-turbo)
> export OPENAI_API_KEY="..."
# Optionally, for custom OpenAI-compatible endpoints:
> export OPENAI_BASE_URL="..." # Defaults to None

# For Anthropic Models (e.g., Claude 3.5 Sonnet, Claude 3 Opus)
> export ANTHROPIC_API_KEY="..."

# For Google Gemini Models (e.g., Gemini Pro)
> export GEMINI_API_KEY="..."

# For Ollama (Locally Hosted Models like Llama 3)
> export OLLAMA_MODEL="llama3" # Specify the Ollama model tag
# Ensure your Ollama server is running and accessible. LiteLLM will typically connect to http://localhost:11434.
# For custom Ollama API base, set: OLLAMA_API_BASE_URL="http://custom.host:port"

# For other providers (Azure, Bedrock, Cohere, etc.):
# Please refer to the LiteLLM documentation for the required environment variables.
# https://docs.litellm.ai/docs/providers
```

**Specifying a Model:**

Termite determines which LLM model to use based on the following, in order of priority:

1.  **`LITELLM_MODEL` Environment Variable (Recommended for clarity):**
    You can explicitly set the model string that LiteLLM should use. This is the most direct way to specify a model, especially for providers not covered by the common variables above.
    ```bash
    > export LITELLM_MODEL="azure/your-deployment-name" # Example for Azure
    > export LITELLM_MODEL="bedrock/anthropic.claude-3-sonnet-20240229-v1:0" # Example for Bedrock
    > export LITELLM_MODEL="groq/llama3-70b-8192" # Example for Groq
    ```

2.  **Inference from Common API Keys (if `LITELLM_MODEL` is not set):**
    *   If `OPENAI_API_KEY` is set: Defaults to `gpt-4o`.
    *   If `ANTHROPIC_API_KEY` is set (and OpenAI key is not): Defaults to `claude-3-5-sonnet-20240620`.
    *   If `GEMINI_API_KEY` is set (and OpenAI/Anthropic keys are not): Defaults to `gemini/gemini-pro`.

3.  **`OLLAMA_MODEL` Environment Variable (if `LITELLM_MODEL` and other API keys are not set):**
    *   If `OLLAMA_MODEL` is set (e.g., `export OLLAMA_MODEL="llama3"`): Termite will use `ollama/your_ollama_model_name` (e.g., `ollama/llama3`).

**Example:**
If you have `OPENAI_API_KEY` set but want to use a specific Cohere model, you should set:
```bash
> export COHERE_API_KEY="..."
> export LITELLM_MODEL="cohere/command-r-plus"
```
If `LITELLM_MODEL` was not set in the above example, Termite would default to using an OpenAI model because `OPENAI_API_KEY` is also present.

For detailed provider configurations and a full list of supported models, please consult the [LiteLLM documentation](https://docs.litellm.ai/docs/providers).

## Usage

To use, run the following:

```bash
> termite
```

You'll be asked to describe what you want to build. Do this, and then Termite will execute the following steps:

1. Generate a design document based on your prompt.
2. Implement the TUI in Python.
3. Iteratively fix runtime errors, if any exist.
4. (Optional) Iteratively refine the TUI based on self-reflections.

Once finished, your TUI will be saved to the `~/.termite` directory and automatically started up for you to use.

### Advanced Usage

You can configure the steps above with the following command-line arguments:

- `--library`: Specify the library Termite should use to build the TUI. Options are: urwid, rich, textual, and curses. Default is urwid.
- `--refine`: Setting this will improve the output by adding a self-reflection and refinement step to the process.
- `--refine-iters`: Controls the number of times the TUI should be refined, if `--refine` is enabled. Default is 1.
- `--fix-iters`: Controls the maximum number of attempts Termite should make at fixing a bug with the TUI. Default is 10.

## Examples

> Built something cool? [Submit a PR](https://github.com/shobrook/termite/pulls) to add your example here.

**"Make me a simple process monitor"**

![Process](./assets/process.png)

**"Help me manage my Git branches (view, create, switch, etc.)"**

![Git](./assets/git.png)

**"I need a quick way to test some RegEx patterns"**

![RegEx](./assets/regex.png)

## Roadmap

The bottleneck in most code generation pipelines is the verifier. That is, how can we verify that the generated code is what we want? Termite currently does the bare minimum for verification –– we execute the TUI in a pseudo-terminal to detect runtime exceptions. But a TUI can still look or behave improperly even if it runs without errors...

Some ideas:

1. Capture an image of what the TUI looks like and feed it to GPT-4o Vision for evaluation. This could help verify UI correctness.
2. Use an agent to simulate user actions in the TUI and record the results. This could help verify functionality correctness. But the problem here is some actions in a TUI can be destructive (e.g. killing a process in `htop`).
