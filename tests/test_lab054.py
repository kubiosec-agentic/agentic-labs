"""
Tests for lab054_LangChain_Tools - LangChain tool integration.

Smoke tests:  file existence, syntax validation, structural checks    (~seconds)
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab054_LangChain_Tools"

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab054
class TestLab054Smoke:
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
        "LC_01.py", "LC_02.py", "LC_03.py",
        "LC_04.py", "LC_05.py", "LC_06.py",
    ])
    def test_script_exists(self, script):
        """Each LangChain script file must exist."""
        assert (LAB_DIR / script).is_file(), f"Missing script: {script}"

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", [
        "LC_01.py", "LC_02.py", "LC_03.py",
        "LC_04.py", "LC_05.py", "LC_06.py",
    ])
    def test_script_valid_syntax(self, script):
        """Every Python script must parse without syntax errors."""
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Requirements content checks ---

    def test_requirements_has_langchain(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain" in content.lower()

    def test_requirements_has_openai(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in content.lower()

    def test_requirements_has_pydantic(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "pydantic" in content.lower()

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB054" in content

    def test_readme_mentions_langchain(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "LangChain" in content or "langchain" in content

    def test_readme_mentions_tools(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "Tool" in content or "tool" in content or "integration" in content.lower()

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    @pytest.mark.parametrize("script", [
        "LC_01.py", "LC_02.py", "LC_03.py",
        "LC_04.py", "LC_05.py", "LC_06.py",
    ])
    def test_no_emdashes_in_script(self, script):
        """Check for em-dashes in script files."""
        content = (LAB_DIR / script).read_text()
        assert "\u2014" not in content, f"{script} contains em-dashes"
