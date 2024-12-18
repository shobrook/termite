# Standard library
import os
from typing import Dict, List

# Third party
from ollama import chat
from openai import OpenAI
from anthropic import Anthropic


#########
# HELPERS
#########


def get_llm_provider():
    if os.getenv("OPENAI_API_KEY", None):  # Default
        return "openai"

    if os.getenv("ANTHROPIC_API_KEY", None):
        return "anthropic"

    if os.getenv("OLLAMA_MODEL", None):
        return "ollama"

    raise ValueError(
        "No API key found for OpenAI or Anthropic. No Ollama model found either."
    )


def run_openai(system: str, messages: List[Dict[str, str]], **kwargs) -> str:
    openai = OpenAI()
    response = openai.chat.completions.create(
        messages=[{"role": "system", "content": system}, *messages],
        model="gpt-4o" if "model" not in kwargs else kwargs["model"],
        temperature=0.7 if "temperature" not in kwargs else kwargs["temperature"],
    )
    return response.choices[0].message.content


def run_anthropic(system: str, messages: List[Dict[str, str]], **kwargs) -> str:
    anthropic = Anthropic()
    response = anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        system=system,
        messages=messages,
        temperature=0.7 if "temperature" not in kwargs else kwargs["temperature"],
    )
    return response.content[0].text


def run_ollama(system: str, messages: List[Dict[str, str]]) -> str:
    response = chat(
        model=os.getenv("OLLAMA_MODEL", None),
        messages=[{"role": "system", "content": system}, *messages],
    )
    return response.message.content


######
# MAIN
######


def run_llm(system: str, messages: List[Dict[str, str]], **kwargs) -> str:
    provider = get_llm_provider()
    if provider == "openai":
        return run_openai(system, messages, **kwargs)
    elif provider == "anthropic":
        return run_anthropic(system, messages, **kwargs)
    elif provider == "ollama":
        return run_ollama(system, messages)
