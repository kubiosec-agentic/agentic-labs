"""
Tests for lab087_Mem0.
Smoke tests validate structure, syntax, and content without API calls.
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab087_Mem0"

SCRIPTS = ["mem_01.py", "mem_02.py", "mem_03.py", "mem_04.py", "mem_05.py"]


@pytest.mark.smoke
@pytest.mark.lab087
class TestLab087Smoke:
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

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_script_exists(self, script):
        assert (LAB_DIR / script).is_file()

    # -- syntax checks ------------------------------------------------------

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_script_syntax(self, script):
        src = (LAB_DIR / script).read_text()
        ast.parse(src)

    # -- requirements -------------------------------------------------------

    def test_requirements_has_mem0(self):
        reqs = (LAB_DIR / "requirements.txt").read_text().lower()
        assert "mem0" in reqs

    # -- README content -----------------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB087" in readme

    def test_readme_mentions_mem0(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "Mem0" in readme or "mem0" in readme

    def test_readme_mentions_qdrant(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "qdrant" in readme

    def test_readme_documents_all_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        for script in SCRIPTS:
            assert script in readme, f"{script} not mentioned in README"

    # -- no em-dashes -------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_no_emdashes_in_scripts(self, script):
        src = (LAB_DIR / script).read_text()
        assert "\u2014" not in src, f"{script} contains em-dashes"
