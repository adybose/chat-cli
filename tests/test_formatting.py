from unittest import mock

import pytest

from app.utils import formatting as fmt


CONFIG_SAFE = {"safety": True, "model": "m", "temperature": 0, "max_tokens": 10}
CONFIG_UNSAFE = {"safety": False, "model": "m", "temperature": 0, "max_tokens": 10}


# ---------- check_for_issue ----------

@pytest.mark.parametrize("response", ["ls -la", "echo Sorry", "date"])
def test_check_for_issue_passes_valid_commands(response):
    assert fmt.check_for_issue(response) is None


@pytest.mark.xfail(strict=True, reason="Bug: response is lowercased but compared to capitalized "
                                       "prefixes, so refusals are never caught")
@pytest.mark.parametrize("response", [
    "Sorry, I can't do that",
    "I'm sorry, that is not possible",
    "I am unable to help",
    "sorry, no",
])
def test_check_for_issue_exits_on_refusal(response):
    with pytest.raises(SystemExit):
        fmt.check_for_issue(response)


@pytest.mark.xfail(strict=True, reason="Bug: an empty model reply is shown and offered for execution")
def test_check_for_issue_exits_on_empty_response():
    with pytest.raises(SystemExit):
        fmt.check_for_issue("")


# ---------- check_for_markdown ----------

def test_check_for_markdown_exits_on_code_fence(capsys):
    response = "```bash\nls -la\n```"
    with pytest.raises(SystemExit) as exc:
        fmt.check_for_markdown(response)
    assert exc.value.code == -1
    out = capsys.readouterr().out
    assert "contains markdown" in out and response in out


def test_check_for_markdown_passes_plain_command():
    assert fmt.check_for_markdown("ls -la") is None


@pytest.mark.xfail(strict=True, reason="Bug: response.count('```', 2) starts searching at index 2, "
                                       "so a lone fence at the very start is missed")
def test_check_for_markdown_detects_single_leading_fence():
    with pytest.raises(SystemExit):
        fmt.check_for_markdown("```bash ls -la")


# ---------- missing_posix_display ----------

def test_missing_posix_display_true_when_empty():
    with mock.patch.object(fmt.subprocess, "check_output", return_value=b"\n") as co:
        assert fmt.missing_posix_display() is True
    co.assert_called_once_with("echo $DISPLAY", shell=True)


def test_missing_posix_display_false_when_set():
    with mock.patch.object(fmt.subprocess, "check_output", return_value=b":0\n"):
        assert fmt.missing_posix_display() is False


# ---------- evaluate_input ----------

@pytest.mark.parametrize("user_input", ["Y", "y", ""])
def test_evaluate_input_runs_command_on_unix(user_input):
    with mock.patch.object(fmt.subprocess, "run") as run:
        fmt.evaluate_input(user_input, "ls", "/bin/bash", CONFIG_SAFE)
    run.assert_called_once_with(["/bin/bash", "-c", "ls"], shell=False)


def test_evaluate_input_runs_command_on_powershell():
    with mock.patch.object(fmt.subprocess, "run") as run:
        fmt.evaluate_input("Y", "dir", "powershell.exe", CONFIG_SAFE)
    run.assert_called_once_with(["powershell.exe", "/c", "dir"], shell=False)


@pytest.mark.parametrize("user_input", ["n", "N", "x"])
def test_evaluate_input_does_nothing_otherwise(user_input):
    with mock.patch.object(fmt.subprocess, "run") as run, \
         mock.patch.object(fmt.pyperclip, "copy") as copy, \
         mock.patch.object(fmt, "call_open_ai") as ai:
        fmt.evaluate_input(user_input, "ls", "/bin/bash", CONFIG_SAFE)
    run.assert_not_called()
    copy.assert_not_called()
    ai.assert_not_called()


@pytest.mark.parametrize("user_input", ["c", "C"])
def test_evaluate_input_copies_to_clipboard(user_input, capsys):
    with mock.patch.object(fmt, "missing_posix_display", return_value=False), \
         mock.patch.object(fmt.pyperclip, "copy") as copy:
        fmt.evaluate_input(user_input, "ls -la", "/bin/bash", CONFIG_SAFE)
    copy.assert_called_once_with("ls -la")
    assert "Copied Command ls -la to clipboard" in capsys.readouterr().out


def test_evaluate_input_copy_skipped_without_display():
    with mock.patch.object(fmt.os, "name", "posix"), \
         mock.patch.object(fmt, "missing_posix_display", return_value=True), \
         mock.patch.object(fmt.pyperclip, "copy") as copy:
        assert fmt.evaluate_input("c", "ls", "/bin/bash", CONFIG_SAFE) is None
    copy.assert_not_called()


@pytest.mark.parametrize("user_input", ["m", "M"])
def test_evaluate_input_modify_reprompts_and_recurses(user_input):
    with mock.patch("builtins.input", return_value="list hidden files"), \
         mock.patch.object(fmt, "call_open_ai", return_value="ls -a") as ai, \
         mock.patch.object(fmt, "check_for_issue") as issue, \
         mock.patch.object(fmt, "check_for_markdown") as md, \
         mock.patch.object(fmt, "display_response_command_and_prompt_user_input", return_value="Y") as disp, \
         mock.patch.object(fmt.subprocess, "run") as run:
        fmt.evaluate_input(user_input, "ls", "/bin/bash", CONFIG_SAFE, ask_flag=True)
    ai.assert_called_once_with("list hidden files", "/bin/bash", CONFIG_SAFE)
    issue.assert_called_once_with("ls -a")
    md.assert_called_once_with("ls -a")
    disp.assert_called_once_with("ls -a", CONFIG_SAFE, True)
    run.assert_called_once_with(["/bin/bash", "-c", "ls -a"], shell=False)


# ---------- display_response_command_and_prompt_user_input ----------

def test_display_prints_command(capsys):
    fmt.display_response_command_and_prompt_user_input("ls -la", CONFIG_UNSAFE)
    out = capsys.readouterr().out
    assert "Command: " in out and "ls -la" in out


def test_display_safety_off_returns_y_without_prompt():
    with mock.patch("builtins.input") as inp:
        assert fmt.display_response_command_and_prompt_user_input("ls", CONFIG_UNSAFE) == "Y"
    inp.assert_not_called()


def test_display_safety_on_prompts_user(capsys):
    with mock.patch.object(fmt, "missing_posix_display", return_value=False), \
         mock.patch("builtins.input", return_value="n"):
        assert fmt.display_response_command_and_prompt_user_input("ls", CONFIG_SAFE) == "n"
    assert "[c]opy to clipboard" in capsys.readouterr().out


def test_display_ask_flag_overrides_safety_off():
    with mock.patch.object(fmt, "missing_posix_display", return_value=False), \
         mock.patch("builtins.input", return_value="m"):
        assert fmt.display_response_command_and_prompt_user_input("ls", CONFIG_UNSAFE, ask_flag=True) == "m"


def test_display_hides_copy_option_without_display(capsys):
    with mock.patch.object(fmt.os, "name", "posix"), \
         mock.patch.object(fmt, "missing_posix_display", return_value=True), \
         mock.patch("builtins.input", return_value="y"):
        fmt.display_response_command_and_prompt_user_input("ls", CONFIG_SAFE)
    out = capsys.readouterr().out
    assert "[c]opy" not in out
    assert "Execute command? [Y]es [n]o [m]odify ==> " in out


def test_display_default_config_raises_keyerror():
    with pytest.raises(KeyError):
        fmt.display_response_command_and_prompt_user_input("ls")


# ---------- more edge cases ----------

def test_check_for_markdown_ignores_inline_backticks():
    assert fmt.check_for_markdown("echo `date`") is None


@pytest.mark.parametrize("user_input", ["yes", " y", "Yes"])
def test_evaluate_input_only_exact_y_runs(user_input):
    with mock.patch.object(fmt.subprocess, "run") as run:
        fmt.evaluate_input(user_input, "ls", "/bin/bash", CONFIG_SAFE)
    run.assert_not_called()


def test_evaluate_input_copy_on_windows_skips_display_check():
    with mock.patch.object(fmt.os, "name", "nt"), \
         mock.patch.object(fmt, "missing_posix_display", side_effect=AssertionError("not on Windows")), \
         mock.patch.object(fmt.pyperclip, "copy") as copy:
        fmt.evaluate_input("c", "dir", "powershell.exe", CONFIG_SAFE)
    copy.assert_called_once_with("dir")


def test_evaluate_input_ignores_command_exit_code():
    failed = fmt.subprocess.CompletedProcess(args=[], returncode=1)
    with mock.patch.object(fmt.subprocess, "run", return_value=failed):
        assert fmt.evaluate_input("Y", "false", "/bin/bash", CONFIG_SAFE) is None


def test_evaluate_input_modify_with_empty_prompt_exits(capsys):
    # Uses the real call_open_ai, which exits before any API call on an empty prompt.
    with mock.patch("builtins.input", return_value=""):
        with pytest.raises(SystemExit) as exc:
            fmt.evaluate_input("m", "ls", "/bin/bash", CONFIG_SAFE)
    assert exc.value.code == -1
    assert "No user prompt specified." in capsys.readouterr().out


def test_display_safety_zero_behaves_like_false():
    with mock.patch("builtins.input") as inp:
        assert fmt.display_response_command_and_prompt_user_input("ls", {**CONFIG_SAFE, "safety": 0}) == "Y"
    inp.assert_not_called()


def test_display_ctrl_d_at_prompt_raises_eoferror():
    with mock.patch.object(fmt, "missing_posix_display", return_value=False), \
         mock.patch("builtins.input", side_effect=EOFError):
        with pytest.raises(EOFError):
            fmt.display_response_command_and_prompt_user_input("ls", CONFIG_SAFE)


@pytest.mark.xfail(strict=True, reason="Bug: an empty 'safety:' in config.yaml (None) makes the function "
                                       "return None, and evaluate_input then crashes on None.upper()")
def test_display_safety_none_returns_an_answer():
    with mock.patch.object(fmt, "missing_posix_display", return_value=False), \
         mock.patch("builtins.input", return_value="n"):
        result = fmt.display_response_command_and_prompt_user_input("ls", {**CONFIG_SAFE, "safety": None})
    assert isinstance(result, str)


@pytest.mark.xfail(strict=True, reason="Bug: on macOS $DISPLAY is unset, so the clipboard option is "
                                       "hidden even though pyperclip works there")
def test_display_offers_copy_on_macos(capsys):
    with mock.patch.object(fmt.os, "name", "posix"), \
         mock.patch.object(fmt.sys, "platform", "darwin"), \
         mock.patch.object(fmt.subprocess, "check_output", return_value=b"\n"), \
         mock.patch("builtins.input", return_value="n"):
        fmt.display_response_command_and_prompt_user_input("ls", CONFIG_SAFE)
    assert "[c]opy" in capsys.readouterr().out
