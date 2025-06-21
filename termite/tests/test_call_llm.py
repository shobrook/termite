import unittest
from unittest.mock import patch, MagicMock, call
import os
from typing import Generator

# Assuming the tests will be run from the root of the project
# If not, sys.path adjustments might be needed here or in the test runner
from termite.shared.call_llm import call_llm # Only import call_llm

# Mock LiteLLM's completion response structure for non-streaming
class MockLiteLLMResponse:
    def __init__(self, content):
        self.choices = [MagicMock(message=MagicMock(content=content))]

# Mock LiteLLM's streaming chunk structure
class MockLiteLLMStreamChunk:
    def __init__(self, content):
        self.choices = [MagicMock(delta=MagicMock(content=content))]

class TestCallLLM(unittest.TestCase):
    def setUp(self):
        """Clear relevant environment variables before each test."""
        self.original_environ = os.environ.copy()
        vars_to_clear = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OLLAMA_MODEL", "LITELLM_MODEL"]
        for var in vars_to_clear:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Restore environment variables after each test."""
        os.environ.clear()
        os.environ.update(self.original_environ)

    @patch('termite.shared.call_llm.litellm.completion')
    def test_call_llm_non_streaming_with_openai_model(self, mock_litellm_completion):
        # Configure mock
        mock_litellm_completion.return_value = MockLiteLLMResponse("openai_test_response")

        # Set environment variable for API key (LiteLLM might pick this up)
        os.environ["OPENAI_API_KEY"] = "test_openai_key"

        # Call the function
        system_prompt = "System prompt"
        messages = [{"role": "user", "content": "Hello"}]
        # Explicitly pass model to use OpenAI via LiteLLM
        response = call_llm(system_prompt, messages, model="gpt-4o", temperature=0.5, stream=False)

        # Assertions
        self.assertEqual(response, "openai_test_response")
        expected_messages = [{"role": "system", "content": system_prompt}] + messages
        mock_litellm_completion.assert_called_once_with(
            model="gpt-4o",
            messages=expected_messages,
            temperature=0.5,
            max_tokens=8192, # Assuming default MAX_TOKENS from call_llm
            stream=False
        )

    @patch('termite.shared.call_llm.litellm.completion')
    def test_call_llm_streaming_with_anthropic_model(self, mock_litellm_completion):
        # Configure mock for streaming
        stream_chunks_content = ["claude_chunk1", " claude_chunk2", "claude_chunk3"]
        mock_litellm_completion.return_value = iter(
            [MockLiteLLMStreamChunk(content) for content in stream_chunks_content]
        )

        os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"

        system_prompt = "System stream prompt"
        messages = [{"role": "user", "content": "Stream hello"}]
        response_generator = call_llm(system_prompt, messages, model="claude-3-opus-20240229", stream=True)

        self.assertIsInstance(response_generator, Generator)
        responses = list(response_generator)
        self.assertEqual(responses, stream_chunks_content)

        expected_messages = [{"role": "system", "content": system_prompt}] + messages
        mock_litellm_completion.assert_called_once_with(
            model="claude-3-opus-20240229",
            messages=expected_messages,
            temperature=0.7, # Default temperature
            max_tokens=8192, # Default MAX_TOKENS
            stream=True
        )

    @patch('termite.shared.call_llm.litellm.completion')
    def test_call_llm_with_ollama_model_from_env(self, mock_litellm_completion):
        mock_litellm_completion.return_value = MockLiteLLMResponse("ollama_env_response")
        os.environ["OLLAMA_MODEL"] = "llama3" # User sets this for Ollama

        system_prompt = "Ollama system"
        messages = [{"role": "user", "content": "Hi Ollama"}]
        # No model passed in kwargs, call_llm should infer "ollama/llama3"
        response = call_llm(system_prompt, messages, stream=False)

        self.assertEqual(response, "ollama_env_response")
        expected_messages = [{"role": "system", "content": system_prompt}] + messages
        mock_litellm_completion.assert_called_once_with(
            model="ollama/llama3", # LiteLLM format for Ollama
            messages=expected_messages,
            temperature=0.7,
            max_tokens=8192,
            stream=False
        )

    @patch('termite.shared.call_llm.litellm.completion')
    def test_call_llm_with_gemini_model_and_explicit_model_kwarg(self, mock_litellm_completion):
        mock_litellm_completion.return_value = MockLiteLLMResponse("gemini_kwarg_response")
        os.environ["GEMINI_API_KEY"] = "test_gemini_key" # LiteLLM uses this

        system_prompt = "Gemini system"
        messages = [{"role": "user", "content": "Hi Gemini"}]
        # Model explicitly passed
        response = call_llm(system_prompt, messages, model="gemini/gemini-pro", stream=False)

        self.assertEqual(response, "gemini_kwarg_response")
        expected_messages = [{"role": "system", "content": system_prompt}] + messages
        mock_litellm_completion.assert_called_once_with(
            model="gemini/gemini-pro",
            messages=expected_messages,
            temperature=0.7,
            max_tokens=8192,
            stream=False
        )

    @patch('termite.shared.call_llm.litellm.completion')
    def test_call_llm_model_inference_priority(self, mock_litellm_completion):
        # Test that LITELLM_MODEL > OPENAI > ANTHROPIC > GEMINI > OLLAMA for default model inference
        mock_litellm_completion.return_value = MockLiteLLMResponse("response")

        system_prompt = "System"
        messages = [{"role": "user", "content": "Hello"}]

        # 1. LITELLM_MODEL
        os.environ["LITELLM_MODEL"] = "custom_litellm_model"
        os.environ["OPENAI_API_KEY"] = "fake_key" # Others present
        os.environ["ANTHROPIC_API_KEY"] = "fake_key"
        os.environ["GEMINI_API_KEY"] = "fake_key"
        os.environ["OLLAMA_MODEL"] = "fake_ollama"
        call_llm(system_prompt, messages)
        mock_litellm_completion.assert_called_with(model="custom_litellm_model", messages=unittest.mock.ANY, temperature=unittest.mock.ANY, max_tokens=unittest.mock.ANY, stream=False)
        del os.environ["LITELLM_MODEL"]
        mock_litellm_completion.reset_mock()

        # 2. OPENAI
        call_llm(system_prompt, messages)
        mock_litellm_completion.assert_called_with(model="gpt-4o", messages=unittest.mock.ANY, temperature=unittest.mock.ANY, max_tokens=unittest.mock.ANY, stream=False)
        del os.environ["OPENAI_API_KEY"]
        mock_litellm_completion.reset_mock()

        # 3. ANTHROPIC
        call_llm(system_prompt, messages)
        mock_litellm_completion.assert_called_with(model="claude-3-5-sonnet-20240620", messages=unittest.mock.ANY, temperature=unittest.mock.ANY, max_tokens=unittest.mock.ANY, stream=False)
        del os.environ["ANTHROPIC_API_KEY"]
        mock_litellm_completion.reset_mock()

        # 4. GEMINI
        call_llm(system_prompt, messages)
        mock_litellm_completion.assert_called_with(model="gemini/gemini-pro", messages=unittest.mock.ANY, temperature=unittest.mock.ANY, max_tokens=unittest.mock.ANY, stream=False)
        del os.environ["GEMINI_API_KEY"]
        mock_litellm_completion.reset_mock()

        # 5. OLLAMA
        call_llm(system_prompt, messages)
        mock_litellm_completion.assert_called_with(model="ollama/fake_ollama", messages=unittest.mock.ANY, temperature=unittest.mock.ANY, max_tokens=unittest.mock.ANY, stream=False)
        del os.environ["OLLAMA_MODEL"]
        mock_litellm_completion.reset_mock()

        # 6. No model, no keys (should let litellm handle or pass None, depending on call_llm implementation)
        # Current call_llm passes None if no model is found, litellm would error.
        # This test just checks that it's called with model=None if nothing is found.
        call_llm(system_prompt, messages)
        mock_litellm_completion.assert_called_with(model=None, messages=unittest.mock.ANY, temperature=unittest.mock.ANY, max_tokens=unittest.mock.ANY, stream=False)


    @patch('termite.shared.call_llm.litellm.completion')
    def test_call_llm_handles_litellm_exception(self, mock_litellm_completion):
        mock_litellm_completion.side_effect = Exception("LiteLLM API Error")

        system_prompt = "System"
        messages = [{"role": "user", "content": "Hello"}]
        with self.assertRaisesRegex(Exception, "LiteLLM API Error"):
            call_llm(system_prompt, messages, model="gpt-3.5-turbo")

if __name__ == '__main__':
    unittest.main()
