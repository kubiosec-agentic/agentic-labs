"""
Tests for lab032_PythonFrameworks - OpenAI SDK, requests library, Responses API.

Smoke tests:  file existence, syntax validation, structural checks    (~seconds)
Slow tests:   live API calls via Python scripts (require OPENAI_API_KEY)
"""

import ast
import json
import os
import subprocess
from pathlib import Path

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent / "lab032_PythonFrameworks"

# ============================================================================
# SMOKE TESTS
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab032
class TestLab032Smoke:
    """Quick structural checks that run in seconds."""

    # --- File existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir()

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_requirements_exists(self):
        assert (LAB_DIR / "requirements.txt").is_file()

    def test_requests_01_exists(self):
        assert (LAB_DIR / "requests_01.py").is_file()

    def test_chat_01_exists(self):
        assert (LAB_DIR / "chat_01.py").is_file()

    def test_chat_02_exists(self):
        assert (LAB_DIR / "chat_02.py").is_file()

    def test_chat_03_exists(self):
        assert (LAB_DIR / "chat_03.py").is_file()

    def test_resp_01_exists(self):
        assert (LAB_DIR / "resp_01.py").is_file()

    def test_resp_02_exists(self):
        assert (LAB_DIR / "resp_02.py").is_file()

    def test_resp_03_exists(self):
        assert (LAB_DIR / "resp_03.py").is_file()

    def test_resp_04_exists(self):
        assert (LAB_DIR / "resp_04.py").is_file()

    # --- Syntax validation ---

    @pytest.mark.parametrize("script", [
        "requests_01.py", "chat_01.py", "chat_02.py", "chat_03.py",
        "resp_01.py", "resp_02.py", "resp_03.py", "resp_04.py",
    ])
    def test_script_valid_syntax(self, script):
        """Every Python script must parse without syntax errors."""
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # --- Structural content checks ---

    def test_requests_01_uses_requests_library(self):
        source = (LAB_DIR / "requests_01.py").read_text()
        assert "import requests" in source
        assert "requests.post" in source

    def test_requests_01_uses_chat_completions_endpoint(self):
        """requests_01.py should hit the Chat Completions endpoint (bridging curl)."""
        source = (LAB_DIR / "requests_01.py").read_text()
        assert "chat/completions" in source

    def test_requests_01_reads_api_key_from_env(self):
        source = (LAB_DIR / "requests_01.py").read_text()
        assert "OPENAI_API_KEY" in source

    def test_chat_01_uses_openai_sdk(self):
        source = (LAB_DIR / "chat_01.py").read_text()
        assert "from openai import OpenAI" in source
        assert "client.chat.completions.create" in source

    def test_chat_02_has_conversation_loop(self):
        source = (LAB_DIR / "chat_02.py").read_text()
        assert "while" in source
        assert "messages" in source
        assert "append" in source

    def test_chat_03_uses_reasoning_model(self):
        source = (LAB_DIR / "chat_03.py").read_text()
        assert "o4-mini" in source or "reasoning" in source.lower()

    def test_chat_03_has_pentest_context(self):
        source = (LAB_DIR / "chat_03.py").read_text()
        assert "hack" in source.lower() or "penetration" in source.lower()

    def test_resp_01_uses_responses_api(self):
        source = (LAB_DIR / "resp_01.py").read_text()
        assert "client.responses.create" in source

    def test_resp_01_uses_previous_response_id(self):
        source = (LAB_DIR / "resp_01.py").read_text()
        assert "previous_response_id" in source

    def test_resp_03_uses_code_interpreter(self):
        source = (LAB_DIR / "resp_03.py").read_text()
        assert "code_interpreter" in source
        assert "containers" in source

    def test_resp_04_uses_pydantic(self):
        source = (LAB_DIR / "resp_04.py").read_text()
        assert "BaseModel" in source
        assert "responses.parse" in source

    # --- Requirements ---

    def test_requirements_has_openai(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in content

    def test_requirements_has_requests(self):
        content = (LAB_DIR / "requirements.txt").read_text()
        assert "requests" in content

    # --- README content ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB032" in content

    def test_readme_documents_all_scripts(self):
        """README should reference all 8 Python scripts."""
        content = (LAB_DIR / "README.md").read_text()
        for script in ["requests_01", "chat_01", "chat_02", "chat_03",
                        "resp_01", "resp_02", "resp_03", "resp_04"]:
            assert script in content, f"README missing reference to {script}"

    def test_readme_covers_mitmproxy(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "mitmproxy" in content

    def test_readme_requests_first(self):
        """requests_01.py should appear before chat_01.py (bridge from curl)."""
        content = (LAB_DIR / "README.md").read_text()
        pos_requests = content.index("requests_01")
        pos_chat = content.index("chat_01")
        assert pos_requests < pos_chat, "requests_01 should come before chat_01"

    def test_readme_has_cleanup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "OPENAI_BASE_URL" in content and "unset" in content

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"


# ============================================================================
# SLOW TESTS - live API calls (require OPENAI_API_KEY)
# ============================================================================


@pytest.mark.slow
@pytest.mark.lab032
class TestLab032API:
    """Live API tests, skipped unless OPENAI_API_KEY is set."""

    @pytest.fixture(scope="class")
    def api_key(self):
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key or key.startswith("sk-your-"):
            pytest.skip("OPENAI_API_KEY not set")
        return key

    def _run_script(self, script_name, timeout=30):
        """Run a lab script and return stdout."""
        result = subprocess.run(
            ["python3", str(LAB_DIR / script_name)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        assert result.returncode == 0, (
            f"{script_name} failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        return result.stdout

    def test_requests_01_runs(self, api_key):
        """requests_01.py produces non-empty output."""
        output = self._run_script("requests_01.py")
        assert len(output.strip()) > 0

    def test_chat_01_runs(self, api_key):
        """chat_01.py produces non-empty output."""
        output = self._run_script("chat_01.py")
        assert len(output.strip()) > 0

    def test_resp_01_runs(self, api_key):
        """resp_01.py produces two response sections."""
        output = self._run_script("resp_01.py")
        assert "First Response" in output
        assert "Second Response" in output

    def test_resp_04_produces_valid_json(self, api_key):
        """resp_04.py should output valid JSON with steps and final_answer."""
        output = self._run_script("resp_04.py")
        parsed = json.loads(output)
        assert "steps" in parsed
        assert "final_answer" in parsed
        assert len(parsed["steps"]) > 0
