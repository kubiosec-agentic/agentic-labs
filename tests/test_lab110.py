"""
Tests for lab110_A2A - Agent-to-Agent Communication.

Smoke tests: file existence, directory structure, script syntax, documentation checks (~seconds)
Slow tests: live A2A agent interactions (require running agents)
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab110_A2A"

# ============================================================================
# SMOKE TESTS - fast, no API calls, no agent interactions
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab110
class TestLab110Smoke:
    """Quick structural checks that run in seconds."""

    # --- Directory and file existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_test_agent_cards_sh_exists(self):
        assert (LAB_DIR / "test_agent_cards.sh").is_file()

    def test_adk_server_directory_exists(self):
        assert (LAB_DIR / "adk_server").is_dir()

    def test_microsoft_agent_framework_directory_exists(self):
        assert (LAB_DIR / "MicrosoftAgentFramework").is_dir()

    # --- Nested Python scripts: syntax check ---

    @pytest.mark.parametrize("script_path", [
        "MicrosoftAgentFramework/ms_client/demo.py",
        "MicrosoftAgentFramework/ms_client/demo_conversation.py",
        "MicrosoftAgentFramework/test.py",
        "adk_server/remote_a2a/check_prime_agent/agent.py",
    ])
    def test_python_script_syntax(self, script_path):
        """All Python scripts should parse without syntax errors."""
        script_file = LAB_DIR / script_path
        assert script_file.is_file(), f"Script missing: {script_path}"
        content = script_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {script_path}: {e}")

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "LAB110" in content

    def test_readme_mentions_a2a(self):
        """README should document A2A protocol."""
        content = (LAB_DIR / "README.md").read_text()
        assert "A2A" in content

    def test_readme_mentions_agent_card(self):
        """README should document agent cards."""
        content = (LAB_DIR / "README.md").read_text()
        assert "agent card" in content.lower() or "agent_card" in content

    def test_readme_mentions_discovery(self):
        """README should document agent discovery."""
        content = (LAB_DIR / "README.md").read_text()
        assert "discovery" in content.lower() or "discover" in content.lower()

    def test_readme_mentions_interoperability(self):
        """README should document cross-vendor interoperability."""
        content = (LAB_DIR / "README.md").read_text()
        assert "interoperab" in content.lower() or "cross-vendor" in content.lower() or "cross vendor" in content.lower()

    def test_readme_mentions_openai_or_gemini(self):
        """README should mention vendor support."""
        content = (LAB_DIR / "README.md").read_text()
        assert "OpenAI" in content or "Gemini" in content or "openai" in content.lower() or "gemini" in content.lower()

    def test_readme_mentions_well_known_endpoint(self):
        """README should document the well-known endpoint."""
        content = (LAB_DIR / "README.md").read_text()
        assert ".well-known" in content or "well-known" in content

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    def test_no_emdashes_in_demo_py(self):
        content = (LAB_DIR / "MicrosoftAgentFramework/ms_client/demo.py").read_text()
        assert "\u2014" not in content, "demo.py contains em-dashes"

    def test_no_emdashes_in_test_py(self):
        content = (LAB_DIR / "MicrosoftAgentFramework/test.py").read_text()
        assert "\u2014" not in content, "test.py contains em-dashes"

    def test_no_emdashes_in_agent_py(self):
        content = (LAB_DIR / "adk_server/remote_a2a/check_prime_agent/agent.py").read_text()
        assert "\u2014" not in content, "agent.py contains em-dashes"
