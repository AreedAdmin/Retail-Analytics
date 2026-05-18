# AI-assisted: reviewed by [name]
"""Tests for ai/providers/echo_provider.py."""
import pytest

from ai.providers.echo_provider import EchoProvider
from ai.providers.base import LlmResponse


def test_echo_generate_returns_llm_response():
    p = EchoProvider()
    resp = p.generate("You are a retail analytics assistant.", "What is the lift?")
    assert isinstance(resp, LlmResponse)


def test_echo_provider_name():
    p = EchoProvider()
    assert p.name == "echo"


def test_echo_response_has_label():
    p = EchoProvider()
    resp = p.generate("system prompt text", "user question")
    assert "[General inference]" in resp.text


def test_echo_response_echoes_system_excerpt():
    p = EchoProvider()
    resp = p.generate("retail analytics context here", "any question")
    assert "retail analytics context here"[:30] in resp.text or \
           "Based on the provided context" in resp.text


def test_echo_provider_field():
    p = EchoProvider()
    resp = p.generate("sys", "usr")
    assert resp.provider == "echo"


def test_echo_health_check():
    p = EchoProvider()
    assert p.health_check() is True
