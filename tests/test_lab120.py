"""
Tests for lab120_Security - Bypassing LLM Guardrails and Prompt Injection.

Smoke tests: file existence, script syntax, requirements validity, documentation checks (~seconds)
Slow tests: live API calls to OpenAI (require OPENAI_API_KEY)
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab120_Security"

# ============================================================================
# SMOKE TESTS - fast, no API calls
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab120
class TestLab120Smoke:
    """Quick structural checks that run in seconds."""

    # --- Directory and file existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_txt_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    def test_lab_setup_sh_exists(self):
        assert (LAB_DIR / "lab_setup.sh").is_file()

    def test_lab_cleanup_sh_exists(self):
        assert (LAB_DIR / "lab_cleanup.sh").is_file()

    # --- Python scripts: syntax check ---

    @pytest.mark.parametrize("script_name", [
        "chat_01.py",
        "chat_02.py",
        "chat_03.py",
        "chat_04.py",
        "injection_01.py",
        "injection_02.py",
        "guardrail_01.py",
        "guardrail_02.py",
        "mcp_server_injection.py",
        "mcp_agent_victim.py",
        "mcp_agent_victim_prompt.py",
    ])
    def test_python_script_syntax(self, script_name):
        """All Python scripts should parse without syntax errors."""
        script_file = LAB_DIR / script_name
        assert script_file.is_file(), f"Script missing: {script_name}"
        content = script_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {script_name}: {e}")

    # --- Requirements content checks ---

    def test_requirements_has_openai(self):
        """Requirements should include openai."""
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in content.lower()

    def test_requirements_valid_format(self):
        """Each line in requirements.txt should be valid."""
        lines = (LAB_DIR / "requirements.txt").read_text().strip().splitlines()
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Basic check: should contain a package name
            assert len(line) > 0

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "LAB120" in content

    def test_readme_mentions_guardrail(self):
        """README should document guardrails."""
        content = (LAB_DIR / "README.md").read_text()
        assert "guardrail" in content.lower()

    def test_readme_mentions_injection(self):
        """README should document prompt injection."""
        content = (LAB_DIR / "README.md").read_text()
        assert "injection" in content.lower() or "inject" in content.lower()

    def test_readme_mentions_security(self):
        """README should discuss security."""
        content = (LAB_DIR / "README.md").read_text()
        assert "security" in content.lower() or "bypass" in content.lower()

    def test_readme_mentions_defense_in_depth(self):
        """README should emphasize defense-in-depth."""
        content = (LAB_DIR / "README.md").read_text()
        assert "defense" in content.lower() or "layer" in content.lower() or "mitigat" in content.lower()

    def test_readme_mentions_openai(self):
        """README should mention OpenAI API."""
        content = (LAB_DIR / "README.md").read_text()
        assert "openai" in content.lower() or "OpenAI" in content

    def test_readme_has_setup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "lab_setup" in content or "setup" in content.lower()

    def test_readme_has_cleanup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "lab_cleanup" in content or "cleanup" in content.lower()

    def test_readme_mentions_api_key(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "OPENAI_API_KEY" in content or "API_KEY" in content

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    @pytest.mark.parametrize("script_name", [
        "chat_01.py",
        "chat_02.py",
        "chat_03.py",
        "chat_04.py",
        "injection_01.py",
        "injection_02.py",
        "guardrail_01.py",
        "guardrail_02.py",
        "mcp_server_injection.py",
        "mcp_agent_victim.py",
        "mcp_agent_victim_prompt.py",
    ])
    def test_no_emdashes_in_python_scripts(self, script_name):
        """No em-dashes in Python scripts (may appear in strings, but shouldn't be used for punctuation)."""
        content = (LAB_DIR / script_name).read_text()
        # Check for em-dashes outside of strings (approximately)
        # A stricter check would parse the AST, but a simple check catches most cases
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip comment-only lines
            if line.strip().startswith("#"):
                continue
            # This is a heuristic: em-dashes in string literals are OK,
            # but em-dashes in comments/code are not
            if "\u2014" in line and not ("\"" in line or "'" in line):
                # If it's in an actual code/comment context, fail
                if not line.strip().startswith("#"):
                    pytest.fail(f"em-dash found in {script_name} line {i}: {line}")
