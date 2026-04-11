"""
Tests for lab070_MCP - Model Context Protocol integration.

Smoke tests:  file existence, syntax validation, structural checks    (~seconds)
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab070_MCP"

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab070
class TestLab070Smoke:
    """Quick structural checks that run in seconds."""

    # --- File existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    @pytest.mark.parametrize("script", [
        "mcp_01_stdio.py",
        "mcp_01_stdio_interactive.py",
        "mcp_02_streamable.py",
        "mcp_03_streamable.py",
        "mcp_04_streamable.py",
        "mcp_05_youtube_transcribe.py",
        "mcp_06_streamable_mitm.py",
        "mcp_07_memory_graph.py",
        "server_streamable.py",
        "server_rogue_streamable.py",
    ])
    def test_script_exists(self, script):
        """Each MCP script file must exist."""
        assert (LAB_DIR / script).is_file(), f"Missing script: {script}"

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", [
        "mcp_01_stdio.py",
        "mcp_01_stdio_interactive.py",
        "mcp_02_streamable.py",
        "mcp_03_streamable.py",
        "mcp_04_streamable.py",
        "mcp_05_youtube_transcribe.py",
        "mcp_06_streamable_mitm.py",
        "mcp_07_memory_graph.py",
        "server_streamable.py",
        "server_rogue_streamable.py",
    ])
    def test_script_valid_syntax(self, script):
        """Every Python script must parse without syntax errors."""
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Requirements content checks ---

    def test_requirements_has_fastmcp(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "fastmcp" in content.lower()

    def test_requirements_has_openai_agents(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai-agents" in content.lower() or "openai_agents" in content.lower()

    def test_requirements_has_openai(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in content.lower()

    def test_requirements_has_requests(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "requests" in content.lower()

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB070" in content

    def test_readme_mentions_mcp(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "MCP" in content or "Model Context Protocol" in content

    def test_readme_mentions_fastmcp(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "fastmcp" in content.lower() or "FastMCP" in content

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    @pytest.mark.parametrize("script", [
        "mcp_01_stdio.py",
        "mcp_01_stdio_interactive.py",
        "mcp_02_streamable.py",
        "mcp_03_streamable.py",
        "mcp_04_streamable.py",
        "mcp_05_youtube_transcribe.py",
        "mcp_06_streamable_mitm.py",
        "mcp_07_memory_graph.py",
        "server_streamable.py",
        "server_rogue_streamable.py",
    ])
    def test_no_emdashes_in_script(self, script):
        """Check for em-dashes in script files."""
        content = (LAB_DIR / script).read_text()
        assert "\u2014" not in content, f"{script} contains em-dashes"
