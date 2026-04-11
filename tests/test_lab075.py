"""
Tests for lab075_MS_Agent_Framework.
Smoke tests validate structure, syntax, and content without API calls.
"""

import ast
import os
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab075_MS_Agent_Framework"

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.lab075
class TestLab075Smoke:
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

    @pytest.mark.parametrize("script", [
        "MAF_01_openai_agent.py",
        "MAF_02_azure_agent.py",
        "MAF_03_middleware.py",
        "MAF_04_workflow.py",
        "MAF_05_mcp_agent.py",
        "MAF_06_code_interpreter.py",
    ])
    def test_script_exists(self, script):
        assert (LAB_DIR / script).is_file()

    # -- syntax validation --------------------------------------------------

    @pytest.mark.parametrize("script", [
        "MAF_01_openai_agent.py",
        "MAF_02_azure_agent.py",
        "MAF_03_middleware.py",
        "MAF_04_workflow.py",
        "MAF_05_mcp_agent.py",
        "MAF_06_code_interpreter.py",
    ])
    def test_script_valid_syntax(self, script):
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # -- setup scripts are executable ---------------------------------------

    def test_lab_setup_is_executable(self):
        assert os.access(LAB_DIR / "lab_setup.sh", os.X_OK)

    def test_lab_cleanup_is_executable(self):
        assert os.access(LAB_DIR / "lab_cleanup.sh", os.X_OK)

    # -- requirements checks ------------------------------------------------

    def test_requirements_has_agent_framework(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "agent-framework" in req

    def test_requirements_has_pydantic(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "pydantic" in req

    # -- README content checks ----------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB075" in readme

    def test_readme_documents_all_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        for script in ["MAF_01_openai_agent.py", "MAF_02_azure_agent.py",
                       "MAF_03_middleware.py", "MAF_04_workflow.py",
                       "MAF_05_mcp_agent.py", "MAF_06_code_interpreter.py"]:
            assert script in readme, f"{script} not mentioned in README"

    def test_readme_has_setup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "set up" in readme or "setup" in readme

    def test_readme_has_cleanup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "cleanup" in readme

    # -- em-dash check ------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    def test_no_emdashes_in_scripts(self):
        for py in LAB_DIR.glob("MAF_*.py"):
            src = py.read_text()
            assert "\u2014" not in src, f"{py.name} contains em-dashes"
