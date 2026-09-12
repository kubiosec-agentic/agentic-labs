"""
Tests for lab073_MCP_Stateless - stateless MCP and the fastmcp 3->4 shift.

Smoke tests: file existence, syntax validation, structural checks (~seconds).
No API keys required; the lab's demonstrations (client_demo, sampling_probe)
do not call any hosted model.
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab073_MCP_Stateless"

SCRIPTS = [
    "stateless_server.py",
    "stateful_server.py",
    "client_demo.py",
    "sampling_probe.py",
]

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab073
class TestLab073Smoke:
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

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_script_valid_syntax(self, script):
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Requirements content checks ---

    def test_requirements_has_fastmcp(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "fastmcp" in content.lower()

    def test_requirements_targets_fastmcp_4(self):
        """This lab deliberately runs on the fastmcp 4.x generation."""
        content = (LAB_DIR / "requirements.txt").read_text()
        assert ">=4" in content, "requirements.txt should target fastmcp 4.x"

    def test_requirements_has_requests(self):
        """Needed because Exercise 1 reuses lab070's server_streamable.py."""
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "requests" in content.lower()

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB073" in content

    def test_readme_mentions_stateless(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "stateless" in content.lower()

    def test_readme_mentions_fastmcp(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "fastmcp" in content.lower() or "FastMCP" in content

    def test_readme_references_lab070(self):
        """The lab reuses lab070's servers to make its point."""
        content = (LAB_DIR / "README.md").read_text()
        assert "lab070" in content.lower()

    # --- No em-dashes (house style) ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "—" not in content, "README.md contains em-dashes"

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_no_emdashes_in_script(self, script):
        content = (LAB_DIR / script).read_text()
        assert "—" not in content, f"{script} contains em-dashes"
