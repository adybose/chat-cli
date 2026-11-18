import os
import shutil
import subprocess

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SETUP = os.path.join(ROOT, "setup.sh")

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")


@pytest.fixture
def sandbox(tmp_path):
    """A copy of the repo (with a dummy config.yaml) plus a fake HOME."""
    src = tmp_path / "src"
    home = tmp_path / "home"
    home.mkdir()
    shutil.copytree(ROOT, src, ignore=shutil.ignore_patterns(
        ".git", "chatclienv", ".env", "config.yaml", "tests", "__pycache__", ".pytest_cache"))
    (src / "config.yaml").write_text("model: test\n")
    return src, home


def _run(src, home, shell):
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "SHELL": shell}
    return subprocess.run(["bash", SETUP], cwd=src, env=env, capture_output=True, text=True)


def test_setup_copies_files_and_makes_main_executable(sandbox):
    src, home = sandbox
    result = _run(src, home, "/bin/sh")
    assert result.returncode == 0
    target = home / "chat-cli"
    for name in ("main.py", "prompt.txt", "config.yaml"):
        assert (target / name).exists(), name
    assert os.access(target / "main.py", os.X_OK)
    assert "Setup Complete!" in result.stdout


@pytest.mark.xfail(strict=True, reason="Bug: setup.sh does not copy the app/ package, so the "
                                       "installed main.py fails with No module named 'app'")
def test_setup_installs_app_package(sandbox):
    src, home = sandbox
    _run(src, home, "/bin/sh")
    assert (home / "chat-cli" / "app" / "utils" / "openai.py").exists()


def test_setup_adds_aliases_for_zsh(sandbox):
    src, home = sandbox
    (home / ".zshrc").write_text("")
    _run(src, home, "/bin/zsh")
    rc = (home / ".zshrc").read_text()
    assert f"alias chat={home}/chat-cli/main.py" in rc
    assert f"alias clio={home}/chat-cli/main.py" in rc


def test_setup_adds_aliases_for_bash(sandbox):
    src, home = sandbox
    (home / ".bash_aliases").write_text("")
    _run(src, home, "/bin/bash")
    rc = (home / ".bash_aliases").read_text()
    assert "alias chat=" in rc and "alias clio=" in rc


def test_setup_is_idempotent_for_aliases(sandbox):
    src, home = sandbox
    (home / ".zshrc").write_text("")
    _run(src, home, "/bin/zsh")
    result = _run(src, home, "/bin/zsh")
    rc = (home / ".zshrc").read_text()
    assert rc.count("alias chat=") == 1 and rc.count("alias clio=") == 1
    assert "alias chat already created" in result.stdout


def test_setup_other_shell_prints_manual_instructions(sandbox):
    src, home = sandbox
    result = _run(src, home, "/usr/bin/fish")
    assert "Shell was not bash or zsh" in result.stdout
    assert not (home / ".zshrc").exists()
    assert not (home / ".bash_aliases").exists()


# ---------- more edge cases ----------

def test_setup_script_has_valid_bash_syntax():
    result = subprocess.run(["bash", "-n", SETUP], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_setup_from_outside_repo_installs_nothing(sandbox, tmp_path):
    _, home = sandbox
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    _run(elsewhere, home, "/bin/sh")
    assert not (home / "chat-cli" / "main.py").exists()


def test_setup_bash_creates_missing_bash_aliases_file(sandbox):
    src, home = sandbox
    assert not (home / ".bash_aliases").exists()
    _run(src, home, "/bin/bash")
    rc = (home / ".bash_aliases").read_text()
    assert "alias chat=" in rc and "alias clio=" in rc


@pytest.mark.xfail(strict=True, reason="Bug: setup.sh has no error handling, so a failed copy "
                                       "(missing config.yaml) still reports success")
def test_setup_fails_when_config_yaml_missing(sandbox):
    src, home = sandbox
    (src / "config.yaml").unlink()
    result = _run(src, home, "/bin/sh")
    assert result.returncode != 0 or "Setup Complete!" not in result.stdout


@pytest.mark.xfail(strict=True, reason="Bug: setup.sh doesn't copy .env, so the installed copy "
                                       "can't find the API key")
def test_setup_copies_env_file(sandbox):
    src, home = sandbox
    (src / ".env").write_text("OPENAI_API_KEY=test\n")
    _run(src, home, "/bin/sh")
    assert (home / "chat-cli" / ".env").exists()
