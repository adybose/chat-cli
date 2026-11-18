import os
import sys

import pytest

# Make the repo root importable so `import main` and `import app...` work.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import dotenv  # noqa: E402
import openai  # noqa: E402


def _no_network(*args, **kwargs):
    raise AssertionError("Tests must not call the OpenAI API; mock openai.ChatCompletion.create")


@pytest.fixture(autouse=True)
def no_openai_key_or_network(monkeypatch):
    """Guarantee no test needs (or uses) a real OpenAI key or the network.

    - OPENAI_API_KEY is removed from the environment.
    - dotenv.load_dotenv is a no-op, so the repo's real .env is never read.
    - openai.api_key starts unset.
    - Any un-mocked ChatCompletion.create call fails the test immediately.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: False)
    monkeypatch.setattr(openai, "api_key", None)
    monkeypatch.setattr(openai.ChatCompletion, "create", _no_network)
