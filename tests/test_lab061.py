"""
Tests for lab061_Google_Agents.
Smoke tests validate structure, syntax, and content without API calls.
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab061_Google_Agents"


@pytest.mark.smoke
@pytest.mark.lab061
class TestLab061Smoke:
    """Structure, syntax, and content checks (no network needed)."""

    # -- file existence -----------------------------------------------------

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir()

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    def test_lab_setup_exists(self):
        assert (LAB_DIR / "lab_setup.sh").is_file()

    def test_lab_cleanup_exists(self):
        assert (LAB_DIR / "lab_cleanup.sh").is_file()

    def test_adk_directory_exists(self):
        assert (LAB_DIR / "adk").is_dir()

    def test_cyber_guardian_agent_exists(self):
        assert (LAB_DIR / "adk" / "cyber_guardian" / "agent.py").is_file()

    def test_red_team_agent_exists(self):
        assert (LAB_DIR / "adk" / "llm_red_team_agent" / "agent.py").is_file()

    # -- syntax checks ------------------------------------------------------

    @pytest.mark.parametrize("script", [
        "adk/cyber_guardian/agent.py",
        "adk/cyber_guardian/tools.py",
        "adk/llm_red_team_agent/agent.py",
        "adk/llm_red_team_agent/config.py",
        "adk/llm_red_team_agent/tools.py",
        "adk/llm_red_team_agent/safety_rules.py",
        "adk/llm_red_team_agent/sub_agents/evaluator.py",
        "adk/llm_red_team_agent/sub_agents/red_team.py",
        "adk/llm_red_team_agent/sub_agents/target.py",
    ])
    def test_script_syntax(self, script):
        src = (LAB_DIR / script).read_text()
        ast.parse(src)

    # -- requirements -------------------------------------------------------

    def test_requirements_has_google_adk(self):
        reqs = (LAB_DIR / "requirements.txt").read_text().lower()
        assert "google-adk" in reqs

    # -- README content -----------------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB061" in readme

    def test_readme_mentions_adk(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "ADK" in readme or "adk" in readme

    def test_readme_mentions_gemini(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "gemini" in readme

    # -- no em-dashes -------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    @pytest.mark.parametrize("script", [
        "adk/cyber_guardian/agent.py",
        "adk/cyber_guardian/tools.py",
        "adk/llm_red_team_agent/agent.py",
        "adk/llm_red_team_agent/tools.py",
    ])
    def test_no_emdashes_in_scripts(self, script):
        src = (LAB_DIR / script).read_text()
        assert "\u2014" not in src, f"{script} contains em-dashes"
