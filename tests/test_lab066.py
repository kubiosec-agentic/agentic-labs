"""
Tests for lab066_DeepAgents - the Deep Agents harness lab.

Smoke tests: file existence, syntax validation, structural checks (~seconds).
The slow test runs Exercise 1 against OpenAI and needs OPENAI_API_KEY.
"""

import ast
import pathlib
import subprocess
import sys

import pytest

from tests.conftest import require_env

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab066_DeepAgents"

SCRIPTS = [
    "common.py",
    "docker_sandbox.py",
    "da_01_harness.py",
    "da_02_filesystem.py",
    "da_03_skills.py",
    "da_04_subagents.py",
    "da_05_sandbox.py",
    "da_06_memory.py",
    "da_07_context.py",
    "da_08_injection.py",
]

FIXTURES = [
    "reset_workspace.sh",
    "skills/port-triage/SKILL.md",
    "memory/AGENTS.md",
    "memory/AGENTS.md.orig",
    "workspace/notes.md",
    "workspace/app.py",
    "workspace/scan.txt",
    "workspace/vendor/README.md",
    "workspace/.aws/credentials",
    "workspace/.claude/settings.json",
]

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab066
class TestLab066Smoke:
    """Quick structural checks that run in seconds."""

    # --- File existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_script_exists(self, script):
        assert (LAB_DIR / script).is_file(), f"Missing script: {script}"

    @pytest.mark.parametrize("fixture", FIXTURES)
    def test_fixture_exists(self, fixture):
        assert (LAB_DIR / fixture).is_file(), f"Missing fixture: {fixture}"

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_script_valid_syntax(self, script):
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Requirements content checks ---

    def test_requirements_has_deepagents(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "deepagents" in content.lower()

    def test_requirements_has_langchain_openai(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain-openai" in content.lower()

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB066" in content

    def test_readme_mentions_every_script(self):
        content = (LAB_DIR / "README.md").read_text()
        for script in SCRIPTS:
            if script.startswith("da_"):
                assert script in content, f"README does not mention {script}"

    def test_readme_covers_harness_capabilities(self):
        content = (LAB_DIR / "README.md").read_text().lower()
        for word in ["skill", "sub-agent", "sandbox", "memory", "summaris", "offload"]:
            assert word in content, f"README should cover '{word}'"

    def test_no_em_dashes(self):
        for path in [LAB_DIR / "README.md", *(LAB_DIR / s for s in SCRIPTS)]:
            assert "—" not in path.read_text(), f"em-dash found in {path.name}"

    # --- Structural checks ---

    def test_skill_has_front_matter(self):
        content = (LAB_DIR / "skills/port-triage/SKILL.md").read_text()
        assert content.startswith("---\nname: port-triage\n")
        assert "description:" in content.splitlines()[2]

    def test_workspace_env_is_recreated_by_reset(self):
        """workspace/.env is gitignored on purpose; reset_workspace.sh must recreate it."""
        content = (LAB_DIR / "reset_workspace.sh").read_text()
        assert "workspace/.env" in content

    def test_injection_payload_present(self):
        content = (LAB_DIR / "workspace/vendor/README.md").read_text()
        assert "/.env" in content and "/memory/AGENTS.md" in content

    def test_docker_sandbox_is_hardened(self):
        content = (LAB_DIR / "docker_sandbox.py").read_text()
        for flag in ["--network", "--cap-drop", "--pids-limit", "--read-only", "no-new-privileges"]:
            assert flag in content, f"docker_sandbox.py should pass {flag}"

    def test_hardened_injection_uses_interrupt_on_memory(self):
        content = (LAB_DIR / "da_08_injection.py").read_text()
        assert 'mode="interrupt"' in content and "/memory/**" in content

    def test_everything_covers_dotfiles(self):
        """The dotfile-trap fix must include the dot-matching globs."""
        content = (LAB_DIR / "common.py").read_text()
        assert 'EVERYTHING = ["/**", "/**/.*", "/**/.*/**"]' in content

    def test_da02_has_weak_deny_toggle(self):
        content = (LAB_DIR / "da_02_filesystem.py").read_text()
        assert "DA_WEAK_DENY" in content and "deny_all" in content

    def test_dotfile_secrets_are_fake(self):
        """Fixture credentials must be obviously fake."""
        for f in ["workspace/.aws/credentials", "workspace/.claude/settings.json"]:
            assert "FAKE" in (LAB_DIR / f).read_text().upper()


# ============================================================================
# SLOW TESTS (real model calls)
# ============================================================================


@pytest.mark.slow
@pytest.mark.lab066
class TestLab066Live:
    @require_env("OPENAI_API_KEY")
    def test_da_01_runs(self):
        """Exercise 1 end to end: needs deepagents installed in the test env."""
        pytest.importorskip("deepagents")
        proc = subprocess.run(
            [sys.executable, "da_01_harness.py"],
            cwd=LAB_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert proc.returncode == 0, proc.stderr[-2000:]
        assert "write_file" in proc.stdout
