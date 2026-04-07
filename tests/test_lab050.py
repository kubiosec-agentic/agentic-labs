"""
Tests for lab050_OpenAI_Tools.
Smoke tests validate structure, syntax, and content without API calls.
"""

import ast
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab050_OpenAI_Tools"

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.lab050
class TestLab050Smoke:
    """Structure, syntax, and content checks (no network needed)."""

    # -- file existence -----------------------------------------------------

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir()

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    @pytest.mark.parametrize("script", [
        "OA_01.py", "OA_02.py", "OA_03.py", "OA_04.py",
    ])
    def test_script_exists(self, script):
        assert (LAB_DIR / script).is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    def test_requirements_vulnerable_exists(self):
        assert (LAB_DIR / "requirements-vulnerable.txt").is_file()

    def test_lab_setup_exists(self):
        assert (LAB_DIR / "lab_setup.sh").is_file()

    def test_lab_cleanup_exists(self):
        assert (LAB_DIR / "lab_cleanup.sh").is_file()

    # -- syntax checks ------------------------------------------------------

    @pytest.mark.parametrize("script", [
        "OA_01.py", "OA_02.py", "OA_03.py", "OA_04.py",
    ])
    def test_script_syntax(self, script):
        src = (LAB_DIR / script).read_text()
        ast.parse(src)

    # -- requirements -------------------------------------------------------

    def test_requirements_has_openai(self):
        reqs = (LAB_DIR / "requirements.txt").read_text().lower()
        assert "openai" in reqs

    def test_requirements_has_wikipedia(self):
        reqs = (LAB_DIR / "requirements.txt").read_text().lower()
        assert "wikipedia" in reqs

    def test_requirements_has_pip_audit(self):
        reqs = (LAB_DIR / "requirements.txt").read_text().lower()
        assert "pip-audit" in reqs

    def test_requirements_no_logging(self):
        """logging is a stdlib module, not a pip package."""
        reqs = (LAB_DIR / "requirements.txt").read_text()
        for line in reqs.strip().splitlines():
            stripped = line.split("#")[0].strip()
            assert stripped != "logging", "requirements.txt should not include 'logging' (stdlib)"

    def test_requirements_no_flask(self):
        """flask is not used by any script in lab050."""
        reqs = (LAB_DIR / "requirements.txt").read_text()
        for line in reqs.strip().splitlines():
            stripped = line.split("#")[0].strip().lower()
            assert not stripped.startswith("flask"), "requirements.txt should not include flask"

    def test_requirements_vulnerable_has_pillow(self):
        reqs = (LAB_DIR / "requirements-vulnerable.txt").read_text().lower()
        assert "pillow" in reqs

    # -- OA_01: directory analysis ------------------------------------------

    def test_oa01_has_tool_schema(self):
        src = (LAB_DIR / "OA_01.py").read_text()
        assert "summarize_directory" in src
        assert '"type": "function"' in src

    def test_oa01_uses_gpt4o(self):
        src = (LAB_DIR / "OA_01.py").read_text()
        assert "gpt-4o" in src

    def test_oa01_has_tool_call_handling(self):
        src = (LAB_DIR / "OA_01.py").read_text()
        assert "tool_calls" in src
        assert '"role": "tool"' in src

    # -- OA_02: SQL simulation ----------------------------------------------

    def test_oa02_has_tool_schema(self):
        src = (LAB_DIR / "OA_02.py").read_text()
        assert "find_product" in src
        assert "sql_query" in src

    def test_oa02_uses_gpt4o(self):
        src = (LAB_DIR / "OA_02.py").read_text()
        assert "gpt-4o" in src

    def test_oa02_supports_base_url(self):
        """OA_02 is used with mitmproxy, must support OPENAI_BASE_URL."""
        src = (LAB_DIR / "OA_02.py").read_text()
        assert "OpenAI()" in src  # client reads env vars automatically

    # -- OA_03: vulnerability scanner ---------------------------------------

    def test_oa03_has_pip_audit(self):
        src = (LAB_DIR / "OA_03.py").read_text()
        assert "pip-audit" in src or "pip_audit" in src

    def test_oa03_has_tool_schema(self):
        src = (LAB_DIR / "OA_03.py").read_text()
        assert "check_package_vulnerabilities" in src
        assert '"type": "function"' in src

    def test_oa03_has_devsecops_system_prompt(self):
        src = (LAB_DIR / "OA_03.py").read_text()
        assert "DevSecOps" in src or "security" in src.lower()

    def test_oa03_has_dual_mode(self):
        src = (LAB_DIR / "OA_03.py").read_text()
        assert "OPENAI_API_KEY" in src

    # -- OA_04: Wikipedia research ------------------------------------------

    def test_oa04_has_wikipedia_import(self):
        src = (LAB_DIR / "OA_04.py").read_text()
        assert "import wikipedia" in src

    def test_oa04_has_tool_schema(self):
        src = (LAB_DIR / "OA_04.py").read_text()
        assert "search_security_innovators" in src
        assert '"type": "function"' in src

    def test_oa04_handles_disambiguation(self):
        src = (LAB_DIR / "OA_04.py").read_text()
        assert "DisambiguationError" in src

    # -- README content -----------------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB050" in readme

    def test_readme_documents_all_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        for script in ["OA_01.py", "OA_02.py", "OA_03.py", "OA_04.py"]:
            assert script in readme, f"{script} not mentioned in README"

    def test_readme_has_step_numbering(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "Step 1" in readme
        assert "Step 5" in readme

    def test_readme_has_mitmproxy(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "mitmproxy" in readme.lower()

    def test_readme_has_setup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "set up" in readme or "setup" in readme

    def test_readme_has_cleanup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "cleanup" in readme

    # -- no emoji in scripts ------------------------------------------------

    @pytest.mark.parametrize("script", [
        "OA_01.py", "OA_02.py", "OA_03.py", "OA_04.py",
    ])
    def test_no_emoji_in_scripts(self, script):
        src = (LAB_DIR / script).read_text()
        emoji_chars = [c for c in src if ord(c) > 0x1F600]
        assert not emoji_chars, f"{script} contains emoji characters"

    # -- no em-dashes -------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    @pytest.mark.parametrize("script", [
        "OA_01.py", "OA_02.py", "OA_03.py", "OA_04.py",
    ])
    def test_no_emdashes_in_scripts(self, script):
        src = (LAB_DIR / script).read_text()
        assert "\u2014" not in src, f"{script} contains em-dashes"
