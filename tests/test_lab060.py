"""
Tests for lab060_OpenAI_Agents - OpenAI agents integration.

Smoke tests:  file existence, syntax validation, structural checks    (~seconds)
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab060_OpenAI_Agents"

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab060
class TestLab060Smoke:
    """Quick structural checks that run in seconds."""

    # --- File existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    def test_lab_setup_sh_exists(self):
        assert (LAB_DIR / "lab_setup.sh").is_file()

    def test_lab_cleanup_sh_exists(self):
        assert (LAB_DIR / "lab_cleanup.sh").is_file()

    @pytest.mark.parametrize("script", [
        "agent_01.py", "agent_02.py", "agent_03.py", "agent_04.py",
        "agent_05.py", "agent_06.py", "agent_07.py", "agent_08.py",
    ])
    def test_script_exists(self, script):
        """Each agent script file must exist."""
        assert (LAB_DIR / script).is_file(), f"Missing script: {script}"

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", [
        "agent_01.py", "agent_02.py", "agent_03.py", "agent_04.py",
        "agent_05.py", "agent_06.py", "agent_07.py", "agent_08.py",
    ])
    def test_script_valid_syntax(self, script):
        """Every Python script must parse without syntax errors."""
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Requirements content checks ---

    def test_requirements_has_openai_agents(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai-agents" in content.lower() or "openai_agents" in content.lower()

    def test_requirements_has_openai(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in content.lower()

    def test_requirements_has_pydantic(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "pydantic" in content.lower()

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB060" in content

    def test_readme_mentions_agents(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "Agent" in content or "agent" in content

    def test_readme_mentions_openai(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "OpenAI" in content or "openai" in content

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    @pytest.mark.parametrize("script", [
        "agent_01.py", "agent_02.py", "agent_03.py", "agent_04.py",
        "agent_05.py", "agent_06.py", "agent_07.py", "agent_08.py",
    ])
    def test_no_emdashes_in_script(self, script):
        """Check for em-dashes in script files."""
        content = (LAB_DIR / script).read_text()
        assert "\u2014" not in content, f"{script} contains em-dashes"
