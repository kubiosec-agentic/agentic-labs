"""
Tests for lab105_evaluations - Prompt Evaluation with OpenAI Evals.

Smoke tests: file existence, JSON validity, documentation checks (~seconds)
Slow tests: live API calls to OpenAI (require OPENAI_API_KEY) (~seconds per call)
"""

import ast
import json
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab105_evaluations"

# ============================================================================
# SMOKE TESTS - fast, no API calls
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab105
class TestLab105Smoke:
    """Quick structural checks that run in seconds."""

    # --- Directory and file existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_lab_setup_sh_exists(self):
        assert (LAB_DIR / "lab_setup.sh").is_file()

    def test_lab_cleanup_sh_exists(self):
        assert (LAB_DIR / "lab_cleanup.sh").is_file()

    def test_request_json_exists(self):
        assert (LAB_DIR / "request.json").is_file()

    def test_tickets_jsonl_exists(self):
        assert (LAB_DIR / "tickets.jsonl").is_file()

    # --- JSON validity ---

    def test_request_json_is_valid_json(self):
        content = (LAB_DIR / "request.json").read_text()
        data = json.loads(content)
        assert isinstance(data, dict)

    def test_tickets_jsonl_valid_lines(self):
        """Each line in tickets.jsonl should be valid JSON."""
        lines = (LAB_DIR / "tickets.jsonl").read_text().strip().splitlines()
        assert len(lines) > 0, "tickets.jsonl should not be empty"
        for i, line in enumerate(lines):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                pytest.fail(f"Line {i} is not valid JSON: {e}")

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "LAB105" in content

    def test_readme_mentions_evaluation(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "eval" in content.lower() or "evaluation" in content.lower()

    def test_readme_mentions_openai(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "openai" in content.lower() or "OpenAI" in content

    def test_readme_mentions_evals(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "evals" in content.lower() or "Evals" in content

    def test_readme_has_setup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "lab_setup" in content or "setup" in content.lower()

    def test_readme_has_cleanup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "lab_cleanup" in content or "cleanup" in content.lower()

    def test_readme_mentions_curl(self):
        """This is a curl-based lab."""
        content = (LAB_DIR / "README.md").read_text()
        assert "curl" in content.lower()

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    def test_no_emdashes_in_lab_setup_sh(self):
        content = (LAB_DIR / "lab_setup.sh").read_text()
        assert "\u2014" not in content, "lab_setup.sh contains em-dashes"

    def test_no_emdashes_in_lab_cleanup_sh(self):
        content = (LAB_DIR / "lab_cleanup.sh").read_text()
        assert "\u2014" not in content, "lab_cleanup.sh contains em-dashes"
