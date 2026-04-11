"""
Tests for lab064_Langgraph - Langgraph workflow integration.

Smoke tests:  file existence, syntax validation, structural checks    (~seconds)
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab064_Langgraph"

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab064
class TestLab064Smoke:
    """Quick structural checks that run in seconds."""

    # --- File existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    @pytest.mark.parametrize("script", [
        "LG_01.py", "LG_02.py", "LG_03.py",
    ])
    def test_script_exists(self, script):
        """Each Langgraph script file must exist."""
        assert (LAB_DIR / script).is_file(), f"Missing script: {script}"

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", [
        "LG_01.py", "LG_02.py", "LG_03.py",
    ])
    def test_script_valid_syntax(self, script):
        """Every Python script must parse without syntax errors."""
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Requirements content checks ---

    def test_requirements_has_langgraph(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "langgraph" in content.lower()

    def test_requirements_has_langchain_core(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain" in content.lower()

    def test_requirements_has_langchain_openai(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain" in content.lower() or "openai" in content.lower()

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB064" in content

    def test_readme_mentions_langgraph(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "Langgraph" in content or "langgraph" in content or "graph" in content.lower()

    def test_readme_mentions_workflow(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "workflow" in content.lower() or "graph" in content.lower() or "state" in content.lower()

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    @pytest.mark.parametrize("script", [
        "LG_01.py", "LG_02.py", "LG_03.py",
    ])
    def test_no_emdashes_in_script(self, script):
        """Check for em-dashes in script files."""
        content = (LAB_DIR / script).read_text()
        assert "\u2014" not in content, f"{script} contains em-dashes"
