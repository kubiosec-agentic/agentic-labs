"""
Tests for lab080_MAS - Multi-Agent Systems.
Smoke tests validate structure and content without API calls.
"""

import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab080_MAS"

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.lab080
class TestLab080Smoke:
    """Structure and content checks (no network needed)."""

    # -- file existence -----------------------------------------------------

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir()

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    # -- subdirectories exist -----------------------------------------------

    def test_crewai_directory_exists(self):
        assert (LAB_DIR / "crewai").is_dir()

    def test_agno_directory_exists(self):
        assert (LAB_DIR / "agno").is_dir()

    def test_fastagent_directory_exists(self):
        assert (LAB_DIR / "fastagent").is_dir()

    def test_pydanticai_directory_exists(self):
        assert (LAB_DIR / "pydanticai").is_dir()

    # -- requirements checks ------------------------------------------------

    def test_requirements_has_crewai(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "crewai" in req

    def test_requirements_has_agno(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "agno" in req

    def test_requirements_has_pydantic_ai(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "pydantic-ai" in req

    # -- README content checks ----------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB080" in readme

    def test_readme_mentions_multi_agent(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "agent" in readme

    def test_readme_mentions_frameworks(self):
        readme = (LAB_DIR / "README.md").read_text()
        # Should mention at least some of the frameworks
        frameworks = ["CrewAI", "Agno", "FastAgent", "Pydantic"]
        mentioned = sum(1 for fw in frameworks if fw in readme or fw.lower() in readme.lower())
        assert mentioned >= 2, "README should mention multiple agent frameworks"

    # -- em-dash check ------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"
