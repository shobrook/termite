# Standard library
import os
from typing import Union, Generator, Dict, List

# Third party
import litellm

# Set any necessary LiteLLM environment variables if not already handled by the user's environment
# For example, LiteLLM might use the same OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
# It's also good practice to set a specific log level for litellm if needed, e.g., litellm.set_verbose=True

#########
# HELPERS
#########

MAX_TOKENS = 8192 # This might be configurable per model in LiteLLM or might not be needed.

######
# MAIN
######

def call_llm(
    system: str, messages: List[Dict[str, str]], **kwargs
) -> Union[str, Generator[str, None, None]]:
    """
    Calls the appropriate LLM provider using LiteLLM.

    Args:
        system: The system prompt.
        messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}].
        **kwargs: Additional arguments for litellm.completion, such as:
            model (str): The model to use (e.g., "gpt-4o", "claude-3-opus-20240229").
                         LiteLLM will infer the provider from the model string.
            temperature (float): The temperature for generation.
            stream (bool): Whether to stream the response.
            max_tokens (int): Maximum tokens for the response.
            # Add other relevant LiteLLM parameters as needed.

    Returns:
        If stream is False, returns the LLM's response as a string.
        If stream is True, returns a generator that yields response chunks.
    """
    # Combine system message with user/assistant messages for LiteLLM
    all_messages = [{"role": "system", "content": system}] + messages

    # Prepare parameters for litellm.completion
    # Model should be passed in kwargs. If not, LiteLLM might have a default or raise an error.
    # It's good practice to ensure 'model' is present if your application relies on it.
    model = kwargs.get("model", os.getenv("LITELLM_MODEL")) # Or a default model if you prefer
    if not model:
        # Try to infer from common environment variables if no explicit model is set via kwargs or LITELLM_MODEL
        # This part tries to maintain some backward compatibility with the old provider selection logic,
        # but it's best if the user specifies the model directly for LiteLLM.
        if os.getenv("OPENAI_API_KEY"):
            model = "gpt-4o" # Default OpenAI model
        elif os.getenv("ANTHROPIC_API_KEY"):
            model = "claude-3-5-sonnet-20240620" # Default Anthropic model
        elif os.getenv("GEMINI_API_KEY"):
            model = "gemini/gemini-pro" # Default Gemini model
        elif os.getenv("OLLAMA_MODEL"):
            # For Ollama, LiteLLM expects the model to be prefixed with "ollama/"
            model = f"ollama/{os.getenv('OLLAMA_MODEL')}"
        else:
            # Fallback or raise error if no model can be determined
            # For now, let LiteLLM handle it or raise an error if model is None.
            # Consider raising a custom error if a model isn't found.
            pass


    litellm_params = {
        "model": model,
        "messages": all_messages,
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", MAX_TOKENS),
        "stream": kwargs.get("stream", False),
    }

    # Add any other kwargs that litellm.completion might accept
    # For example, custom API keys, base URLs, etc., if not set globally via environment variables.
    # LiteLLM generally prefers these to be set as environment variables.

    try:
        response = litellm.completion(**litellm_params)

        if not litellm_params["stream"]:
            # Accessing the message content from the non-streaming response
            # LiteLLM's non-streaming response object has a structure like:
            # Choice(finish_reason='stop', index=0, message=Message(content='Response text', role='assistant'))
            # Or for some models, it could be directly in response.choices[0].message.content
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            else:
                # Fallback or error handling if the expected structure isn't found
                # This can depend on the specific model/provider via LiteLLM
                # For debugging, one might log the full response object.
                # print(f"Unexpected response structure: {response}")
                return "" # Or raise an error
        else:
            # Handle streaming response
            # LiteLLM's streaming response yields ModelChunk objects
            # ModelChunk(id='...', choices=[StreamingChoice(delta=Delta(content='...', role='assistant'), finish_reason=None, index=0)], created=..., model='...', object='...', system_fingerprint='...')
            def stream_generator():
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            return stream_generator()

    except Exception as e:
        # Log the exception or handle it as per application requirements
        # print(f"LiteLLM API call failed: {e}")
        # It might be useful to re-raise the exception or return a specific error message.
        raise # Re-raise the exception for now
