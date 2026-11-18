import os
import runpy
import sys
from unittest import mock

import pytest

import main

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAIN_PATH = os.path.join(ROOT, "main.py")

CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "max_tokens": 500,
    "safety": True,
    "openai_api_key": "k",
}


# ---------- print_usage ----------

def test_print_usage_shows_header_and_options(monkeypatch, capsys):
    monkeypatch.setattr(main, "config", CONFIG, raising=False)
    main.print_usage()
    out = capsys.readouterr().out
    assert "chat-cli v0.1" in out
    assert "-a, --ask" in out


def test_print_usage_shows_config_values(monkeypatch, capsys):
    monkeypatch.setattr(main, "config", CONFIG, raising=False)
    main.print_usage()
    out = capsys.readouterr().out
    assert "* Model        : gpt-3.5-turbo" in out
    assert "* Temperature  : 0" in out
    assert "* Max. Tokens  : 500" in out
    assert "* Safety       : On" in out


def test_print_usage_safety_off(monkeypatch, capsys):
    monkeypatch.setattr(main, "config", {**CONFIG, "safety": False}, raising=False)
    main.print_usage()
    assert "* Safety       : Off" in capsys.readouterr().out


# ---------- read_config ----------

def test_read_config_loads_yaml_next_to_main():
    m = mock.mock_open(read_data="model: gpt-4\ntemperature: 0.5\n")
    with mock.patch("builtins.open", m):
        cfg = main.read_config()
    assert cfg == {"model": "gpt-4", "temperature": 0.5}
    assert m.call_args[0][0] == os.path.join(ROOT, "config.yaml")


def test_read_config_missing_file_raises():
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            main.read_config()


# ---------- __main__ entry point ----------

def _run_main(argv, env, user_input="Y", response="ls -la", mock_call_open_ai=True):
    """Execute main.py as a script with every side effect mocked out."""
    patches = {
        "set_api_key": mock.patch("app.utils.openai.set_api_key"),
        "call_open_ai": mock.patch("app.utils.openai.call_open_ai", return_value=response),
        "check_for_issue": mock.patch("app.utils.formatting.check_for_issue"),
        "check_for_markdown": mock.patch("app.utils.formatting.check_for_markdown"),
        "display": mock.patch("app.utils.formatting.display_response_command_and_prompt_user_input",
                              return_value=user_input),
        "evaluate_input": mock.patch("app.utils.formatting.evaluate_input"),
        "safe_load": mock.patch("yaml.safe_load", return_value=CONFIG),
        "open": mock.patch("builtins.open", mock.mock_open(read_data="")),
    }
    if not mock_call_open_ai:
        del patches["call_open_ai"]
    started = {name: p.start() for name, p in patches.items()}
    try:
        with mock.patch.object(sys, "argv", ["main.py"] + argv), \
             mock.patch.dict(os.environ, env, clear=True):
            runpy.run_path(MAIN_PATH, run_name="__main__")
    finally:
        for p in patches.values():
            p.stop()
    return started


BASH = {"SHELL": "/bin/bash"}


def test_main_without_args_prints_usage_and_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        _run_main([], BASH)
    assert exc.value.code == -1
    assert "Usage:" in capsys.readouterr().out


def test_main_joins_args_into_prompt():
    m = _run_main(["list", "all", "files"], BASH)
    m["call_open_ai"].assert_called_once_with("list all files", "/bin/bash", CONFIG)


def test_main_sets_api_key_from_config():
    m = _run_main(["date"], BASH)
    m["set_api_key"].assert_called_once_with(CONFIG)


def test_main_runs_full_pipeline():
    m = _run_main(["list", "files"], BASH, user_input="Y", response="ls")
    m["check_for_issue"].assert_called_once_with("ls")
    m["check_for_markdown"].assert_called_once_with("ls")
    m["display"].assert_called_once_with("ls", CONFIG, False)
    m["evaluate_input"].assert_called_once_with("Y", "ls", "/bin/bash", CONFIG, False)


@pytest.mark.parametrize("flag", ["-a", "--ask"])
def test_main_ask_flag(flag):
    m = _run_main([flag, "show", "time"], BASH)
    m["call_open_ai"].assert_called_once_with("show time", "/bin/bash", CONFIG)
    assert m["display"].call_args[0][2] is True
    assert m["evaluate_input"].call_args[0][4] is True


def test_main_defaults_to_powershell_without_shell_env():
    m = _run_main(["list", "files"], {})
    m["call_open_ai"].assert_called_once_with("list files", "powershell.exe", CONFIG)


# ---------- more edge cases ----------

def test_main_ask_flag_without_prompt_exits_before_api_call(capsys):
    # Real call_open_ai: it exits on the empty prompt; the conftest guard proves no API call is made.
    with pytest.raises(SystemExit) as exc:
        _run_main(["-a"], BASH, mock_call_open_ai=False)
    assert exc.value.code == -1
    assert "No user prompt specified." in capsys.readouterr().out


def test_main_flag_after_first_word_is_part_of_prompt():
    m = _run_main(["list", "-a", "files"], BASH)
    m["call_open_ai"].assert_called_once_with("list -a files", "/bin/bash", CONFIG)
    assert m["display"].call_args[0][2] is False


def test_read_config_empty_file_returns_none():
    with mock.patch("builtins.open", mock.mock_open(read_data="")):
        assert main.read_config() is None


def test_print_usage_without_safety_key_raises(monkeypatch):
    cfg = {k: v for k, v in CONFIG.items() if k != "safety"}
    monkeypatch.setattr(main, "config", cfg, raising=False)
    with pytest.raises(KeyError):
        main.print_usage()


@pytest.mark.xfail(strict=True, reason="Bug/TODO: --help is sent to OpenAI as a prompt instead of "
                                       "printing usage")
def test_main_help_flag_prints_usage_without_api_call():
    m = None
    with pytest.raises(SystemExit):
        m = _run_main(["--help"], BASH)
    assert m is None or not m["call_open_ai"].called


@pytest.mark.xfail(strict=True, reason="Bug: Ctrl+C at the confirmation prompt prints a traceback "
                                       "instead of exiting cleanly")
def test_main_ctrl_c_at_prompt_exits_cleanly():
    display = mock.patch("app.utils.formatting.display_response_command_and_prompt_user_input",
                         side_effect=KeyboardInterrupt)
    display.start()
    try:
        with pytest.raises(SystemExit):
            _run_main_no_display(["list", "files"], BASH)
    except KeyboardInterrupt:
        # Caught here so the interrupt fails this test instead of stopping the whole pytest run.
        pytest.fail("KeyboardInterrupt escaped as a traceback")
    finally:
        display.stop()


def _run_main_no_display(argv, env):
    """Like _run_main but leaves display_response_command_and_prompt_user_input to the caller."""
    patches = [
        mock.patch("app.utils.openai.set_api_key"),
        mock.patch("app.utils.openai.call_open_ai", return_value="ls"),
        mock.patch("app.utils.formatting.check_for_issue"),
        mock.patch("app.utils.formatting.check_for_markdown"),
        mock.patch("app.utils.formatting.evaluate_input"),
        mock.patch("yaml.safe_load", return_value=CONFIG),
        mock.patch("builtins.open", mock.mock_open(read_data="")),
    ]
    for p in patches:
        p.start()
    try:
        with mock.patch.object(sys, "argv", ["main.py"] + argv), \
             mock.patch.dict(os.environ, env, clear=True):
            runpy.run_path(MAIN_PATH, run_name="__main__")
    finally:
        for p in patches:
            p.stop()
