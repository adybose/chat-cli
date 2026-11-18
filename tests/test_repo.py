"""Consistency checks on the repo's own files (no code is executed against OpenAI)."""
import os
import re

import pytest
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return f.read()


def _requirement_names():
    names = []
    for line in _read("requirements.txt").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(re.split(r"[<>=!~\[ ]", line, 1)[0].lower())
    return names


def test_config_example_is_valid_yaml_with_all_keys_the_code_reads():
    cfg = yaml.safe_load(_read("config.yaml.example"))
    for key in ("model", "temperature", "max_tokens", "safety", "openai_api_key"):
        assert key in cfg, key


def test_config_example_defaults_to_gpt_35():
    cfg = yaml.safe_load(_read("config.yaml.example"))
    assert cfg["model"] == "gpt-3.5-turbo"
    assert cfg["temperature"] == 0
    assert cfg["max_tokens"] == 500
    assert cfg["safety"] is True


def test_clio_prompt_has_shell_and_os_placeholders():
    text = _read("app", "utils", "clio_prompt.txt")
    assert "{shell}" in text and "{os}" in text


def test_root_prompt_txt_matches_clio_prompt():
    assert _read("prompt.txt") == _read("app", "utils", "clio_prompt.txt")


def test_main_py_has_shebang_and_is_executable():
    assert _read("main.py").startswith("#!/usr/bin/env python3")
    assert os.access(os.path.join(ROOT, "main.py"), os.X_OK)


@pytest.mark.parametrize("module, requirement", [
    ("yaml", "pyyaml"),
    ("colorama", "colorama"),
    ("termcolor", "termcolor"),
    ("pyperclip", "pyperclip"),
    ("dotenv", "python-dotenv"),
    ("distro", "distro"),
    ("openai", "openai"),
])
def test_every_third_party_import_is_in_requirements(module, requirement):
    sources = _read("main.py") + _read("app", "utils", "openai.py") + _read("app", "utils", "formatting.py")
    assert re.search(rf"^\s*(import|from) {module}\b", sources, re.M), f"{module} is not imported"
    assert requirement in _requirement_names()


def test_psutil_is_listed_but_unused():
    """Documents a stale dependency: psutil is in requirements.txt but nothing imports it."""
    sources = _read("main.py") + _read("app", "utils", "openai.py") + _read("app", "utils", "formatting.py")
    assert "psutil" in _requirement_names()
    assert "psutil" not in sources


@pytest.mark.xfail(strict=True, reason="Bug: requirements.txt doesn't pin openai<1, but the code uses "
                                       "openai.ChatCompletion, which openai>=1.0 removed")
def test_requirements_pin_openai_below_1():
    line = next(l for l in _read("requirements.txt").splitlines() if l.lower().startswith("openai"))
    assert "<1" in line.replace(" ", "")
