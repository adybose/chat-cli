from unittest import mock

import pytest

from app.utils import openai as oa


CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "max_tokens": 500,
    "safety": True,
    "openai_api_key": "config-key",
}

TEMPLATE = "You run {shell} on {os}. Question: "


def _patch_template(template=TEMPLATE):
    return mock.patch("builtins.open", mock.mock_open(read_data=template))


def _fake_response(content):
    resp = mock.MagicMock()
    resp.choices[0].message.content = content
    return resp


# ---------- safety net ----------

def test_unmocked_api_call_is_blocked():
    with _patch_template(), mock.patch.object(oa, "get_os_friendly_name", return_value="X"):
        with pytest.raises(AssertionError, match="must not call the OpenAI API"):
            oa.call_open_ai("list files", "/bin/bash", CONFIG)


# ---------- set_api_key ----------

def test_set_api_key_uses_env_var(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    oa.set_api_key(CONFIG)
    assert oa.openai.api_key == "env-key"


def test_set_api_key_falls_back_to_config():
    oa.set_api_key(CONFIG)
    assert oa.openai.api_key == "config-key"


def test_set_api_key_calls_load_dotenv(monkeypatch):
    with mock.patch.object(oa.dotenv, "load_dotenv") as load:
        oa.set_api_key(CONFIG)
    load.assert_called_once()


def test_set_api_key_missing_everywhere_raises():
    with pytest.raises(KeyError):
        oa.set_api_key({})


# ---------- get_os_friendly_name ----------

def test_os_name_linux():
    with mock.patch.object(oa.platform, "system", return_value="Linux"), \
         mock.patch.object(oa.distro, "name", return_value="Ubuntu 22.04 LTS") as name:
        assert oa.get_os_friendly_name() == "Linux/Ubuntu 22.04 LTS"
    name.assert_called_once_with(pretty=True)


@pytest.mark.parametrize("system, expected", [
    ("Windows", "Windows"),
    ("Darwin", "Darwin/macOS"),
    ("FreeBSD", "FreeBSD"),
])
def test_os_name_other_systems(system, expected):
    with mock.patch.object(oa.platform, "system", return_value=system):
        assert oa.get_os_friendly_name() == expected


# ---------- get_full_prompt ----------

def test_full_prompt_substitutes_shell_and_os():
    with _patch_template(), mock.patch.object(oa, "get_os_friendly_name", return_value="Darwin/macOS"):
        prompt = oa.get_full_prompt("list files", "/bin/zsh")
    assert prompt == "You run /bin/zsh on Darwin/macOS. Question: list files?"


@pytest.mark.parametrize("question", ["what time is it?", "show disk usage."])
def test_full_prompt_keeps_existing_punctuation(question):
    with _patch_template(), mock.patch.object(oa, "get_os_friendly_name", return_value="X"):
        prompt = oa.get_full_prompt(question, "/bin/bash")
    assert prompt.endswith(question)


def test_full_prompt_reads_clio_prompt_next_to_module():
    m = mock.mock_open(read_data=TEMPLATE)
    with mock.patch("builtins.open", m), mock.patch.object(oa, "get_os_friendly_name", return_value="X"):
        oa.get_full_prompt("hi", "/bin/bash")
    assert m.call_args[0][0].endswith("clio_prompt.txt")


def test_full_prompt_with_real_template_file():
    with mock.patch.object(oa, "get_os_friendly_name", return_value="Linux/Test"):
        prompt = oa.get_full_prompt("list files", "/bin/bash")
    assert "{shell}" not in prompt and "{os}" not in prompt
    assert "/bin/bash command translation engine on Linux/Test" in prompt
    assert prompt.endswith("list files?")


# ---------- call_open_ai ----------

def test_call_open_ai_empty_query_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        oa.call_open_ai("", "/bin/bash", CONFIG)
    assert exc.value.code == -1
    assert "No user prompt specified." in capsys.readouterr().out


def test_call_open_ai_returns_stripped_content():
    with mock.patch.object(oa, "get_full_prompt", return_value="full prompt?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", return_value=_fake_response("  ls -la \n")):
        assert oa.call_open_ai("list files", "/bin/bash", CONFIG) == "ls -la"


def test_call_open_ai_passes_config_to_api():
    with mock.patch.object(oa, "get_full_prompt", return_value="full prompt?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", return_value=_fake_response("ls")) as create:
        oa.call_open_ai("list files", "/bin/bash", CONFIG)
    kwargs = create.call_args.kwargs
    assert kwargs["model"] == CONFIG["model"]
    assert kwargs["temperature"] == CONFIG["temperature"]
    assert kwargs["max_tokens"] == CONFIG["max_tokens"]
    assert [m["role"] for m in kwargs["messages"]] == ["system", "user"]
    assert kwargs["messages"][1]["content"] == "full prompt?"


def test_call_open_ai_builds_prompt_from_query_and_shell():
    with mock.patch.object(oa, "get_full_prompt", return_value="p?") as gfp, \
         mock.patch.object(oa.openai.ChatCompletion, "create", return_value=_fake_response("ls")):
        oa.call_open_ai("list files", "/bin/zsh", CONFIG)
    gfp.assert_called_once_with("list files", "/bin/zsh")


@pytest.mark.xfail(strict=True, reason="Bug: system prompt is prompt[1], a single character, "
                                       "instead of the clio_prompt.txt rules")
def test_call_open_ai_system_prompt_is_the_rules_not_one_character():
    with mock.patch.object(oa, "get_full_prompt", return_value="Rules line\nQuestion: list files?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", return_value=_fake_response("ls")) as create:
        oa.call_open_ai("list files", "/bin/bash", CONFIG)
    system = create.call_args.kwargs["messages"][0]["content"]
    assert len(system) > 1


# ---------- more edge cases ----------

def test_set_api_key_empty_env_var_falls_back_to_config(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    oa.set_api_key(CONFIG)
    assert oa.openai.api_key == "config-key"


def test_os_name_linux_with_empty_distro_name():
    with mock.patch.object(oa.platform, "system", return_value="Linux"), \
         mock.patch.object(oa.distro, "name", return_value=""):
        assert oa.get_os_friendly_name() == "Linux/"


def test_full_prompt_replaces_every_placeholder():
    template = "{shell} and {shell} on {os} and {os}: "
    with _patch_template(template), mock.patch.object(oa, "get_os_friendly_name", return_value="OS"):
        prompt = oa.get_full_prompt("go", "/bin/sh")
    assert prompt == "/bin/sh and /bin/sh on OS and OS: go?"


def test_full_prompt_appends_question_mark_after_exclamation():
    with _patch_template(), mock.patch.object(oa, "get_os_friendly_name", return_value="X"):
        assert oa.get_full_prompt("hi!", "/bin/bash").endswith("hi!?")


def test_call_open_ai_propagates_openai_errors():
    err = oa.openai.error.AuthenticationError("Incorrect API key provided")
    with mock.patch.object(oa, "get_full_prompt", return_value="p?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", side_effect=err):
        with pytest.raises(oa.openai.error.AuthenticationError):
            oa.call_open_ai("list files", "/bin/bash", CONFIG)


@pytest.mark.xfail(strict=True, reason="Bug: OpenAI errors (bad key, rate limit) surface as a raw "
                                       "traceback instead of a short error and exit")
def test_call_open_ai_reports_openai_errors_cleanly():
    err = oa.openai.error.AuthenticationError("Incorrect API key provided")
    with mock.patch.object(oa, "get_full_prompt", return_value="p?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", side_effect=err):
        with pytest.raises(SystemExit):
            oa.call_open_ai("list files", "/bin/bash", CONFIG)


@pytest.mark.xfail(strict=True, reason="Bug: a whitespace-only prompt is not treated as empty "
                                       "and is sent to OpenAI")
def test_call_open_ai_rejects_whitespace_only_query():
    with mock.patch.object(oa, "get_full_prompt", return_value="p?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", return_value=_fake_response("ls")):
        with pytest.raises(SystemExit):
            oa.call_open_ai("   ", "/bin/bash", CONFIG)


@pytest.mark.xfail(strict=True, reason="Bug: a reply with content=None crashes on .strip()")
def test_call_open_ai_handles_reply_without_content():
    with mock.patch.object(oa, "get_full_prompt", return_value="p?"), \
         mock.patch.object(oa.openai.ChatCompletion, "create", return_value=_fake_response(None)):
        assert oa.call_open_ai("list files", "/bin/bash", CONFIG) == ""
