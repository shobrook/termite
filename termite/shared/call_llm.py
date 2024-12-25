# Standard library
import os
from typing import Union, Generator, Dict, List

# Third party
from ollama import chat
from openai import OpenAI
from anthropic import Anthropic


#########
# HELPERS
#########


MAX_TOKENS = 8192


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


def call_openai(
    system: str, messages: List[Dict[str, str]], **kwargs
) -> Union[str, Generator[str, None, None]]:
    openai = OpenAI()
    stream = False if "stream" not in kwargs else kwargs["stream"]
    response = openai.chat.completions.create(
        messages=[{"role": "system", "content": system}, *messages],
        model="gpt-4o" if "model" not in kwargs else kwargs["model"],
        temperature=0.7 if "temperature" not in kwargs else kwargs["temperature"],
        stream=stream,
        max_tokens=MAX_TOKENS,
    )

    if not stream:
        return response.choices[0].message.content

    response = (e.choices[0] for e in response)
    response = (e for e in response if e.finish_reason != "stop" and e.delta.content)
    response = (e.delta.content for e in response)

    return response


def call_anthropic(
    system: str, messages: List[Dict[str, str]], **kwargs
) -> Union[str, Generator[str, None, None]]:
    anthropic = Anthropic()
    stream = False if "stream" not in kwargs else kwargs["stream"]
    response = anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages,
        temperature=0.7 if "temperature" not in kwargs else kwargs["temperature"],
        stream=stream,
    )

    if not stream:
        return response.content[0].text

    response = (e for e in response if e.type == "content_block_delta")
    response = (e.delta.text for e in response)

    return response


def call_ollama(system: str, messages: List[Dict[str, str]]) -> str:
    response = chat(
        model=os.getenv("OLLAMA_MODEL", None),
        messages=[{"role": "system", "content": system}, *messages],
    )
    return response.message.content


######
# MAIN
######


def call_llm(
    system: str, messages: List[Dict[str, str]], **kwargs
) -> Union[str, Generator[str, None, None]]:
    provider = get_llm_provider()
    if provider == "openai":
        return call_openai(system, messages, **kwargs)
    elif provider == "anthropic":
        return call_anthropic(system, messages, **kwargs)
    elif provider == "ollama":
        return call_ollama(system, messages)
