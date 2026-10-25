"""Validate client retry budgets without making network requests."""

import pytest
from unittest.mock import MagicMock

from fastdocparse.llm_client import LLMClient


def fake_client():
    client = object.__new__(LLMClient)
    client.model = "test-local"
    client.client = MagicMock()
    client.client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="{}"))
    ]
    return client


@pytest.mark.parametrize("tokens", [0, -1, True, 0.5, float("nan")])
def test_invalid_max_tokens_never_call_provider(tokens):
    client = fake_client()
    with pytest.raises(ValueError, match="max_tokens"):
        client._call([], 0, tokens)
    client.client.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("retries", [-1, True, 0.5, 6, float("nan")])
def test_invalid_retry_counts_never_call_provider(retries):
    client = fake_client()
    with pytest.raises(ValueError, match="retries"):
        client._call([], 0, 100, retries=retries)
    client.client.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("delay", [-1, True, float("nan"), float("inf"), 61])
def test_invalid_backoff_never_call_provider(delay):
    client = fake_client()
    with pytest.raises(ValueError, match="backoff"):
        client._call([], 0, 100, backoff=delay)
    client.client.chat.completions.create.assert_not_called()


def test_valid_zero_retries_uses_single_completion_call():
    client = fake_client()
    assert client._call([], 0, 100, retries=0, backoff=0) == "{}"
    client.client.chat.completions.create.assert_called_once()
