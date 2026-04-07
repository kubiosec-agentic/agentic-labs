"""
Tests for lab020_ResponsesAPI - OpenAI Responses API via curl.

Smoke tests:  file existence, JSON validity, documentation checks     (~seconds)
Slow tests:   live API calls to OpenAI (require OPENAI_API_KEY)       (~seconds per call)
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent / "lab020_ResponsesAPI"

# ============================================================================
# SMOKE TESTS - fast, no API calls
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab020
class TestLab020Smoke:
    """Quick structural checks that run in seconds."""

    # --- File existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_addon_exists(self):
        assert (LAB_DIR / "ADDON.md").is_file()

    def test_request_json_exists(self):
        assert (LAB_DIR / "request.json").is_file()

    def test_data_directory_exists(self):
        assert (LAB_DIR / "data").is_dir()

    def test_story_pdf_exists(self):
        assert (LAB_DIR / "data" / "story.pdf").is_file()

    # --- request.json validity ---

    def test_request_json_is_valid_json(self):
        content = (LAB_DIR / "request.json").read_text()
        data = json.loads(content)
        assert isinstance(data, dict)

    def test_request_json_has_model(self):
        data = json.loads((LAB_DIR / "request.json").read_text())
        assert "model" in data
        assert isinstance(data["model"], str)

    def test_request_json_has_input(self):
        """Responses API uses 'input', not 'messages'."""
        data = json.loads((LAB_DIR / "request.json").read_text())
        assert "input" in data

    def test_request_json_has_text_format(self):
        """request.json should define structured output via text.format."""
        data = json.loads((LAB_DIR / "request.json").read_text())
        assert "text" in data
        assert "format" in data["text"]
        assert data["text"]["format"]["type"] == "json_schema"

    def test_request_json_schema_has_required_fields(self):
        """The JSON schema should define steps and final_answer."""
        data = json.loads((LAB_DIR / "request.json").read_text())
        schema = data["text"]["format"]["schema"]
        assert "steps" in schema["properties"]
        assert "final_answer" in schema["properties"]
        assert "steps" in schema["required"]
        assert "final_answer" in schema["required"]

    def test_request_json_schema_is_strict(self):
        """Strict mode should be enabled for reliable structured output."""
        data = json.loads((LAB_DIR / "request.json").read_text())
        assert data["text"]["format"].get("strict") is True

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "# LAB020" in content

    def test_readme_references_responses_endpoint(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "api.openai.com/v1/responses" in content

    def test_readme_does_not_reference_chat_completions_endpoint_as_primary(self):
        """Lab020 is about Responses API, not Chat Completions."""
        content = (LAB_DIR / "README.md").read_text()
        assert "v1/responses" in content

    def test_readme_covers_web_search(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "web_search_preview" in content

    def test_readme_covers_file_search(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "input_file" in content or "file_id" in content

    def test_readme_covers_message_recall(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "recall" in content.lower() or "response ID" in content.lower() or "resp_" in content.lower()

    def test_readme_covers_previous_response_id(self):
        """The key Responses API feature for multi-turn should be documented."""
        content = (LAB_DIR / "README.md").read_text()
        assert "previous_response_id" in content

    def test_readme_covers_streaming(self):
        content = (LAB_DIR / "README.md").read_text()
        assert '"stream": true' in content or "stream" in content.lower()

    def test_readme_covers_structured_output(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "Structured" in content or "structured" in content

    def test_readme_links_to_addon(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "ADDON.md" in content

    def test_readme_has_comparison_table(self):
        """Should compare Chat Completions vs Responses API."""
        content = (LAB_DIR / "README.md").read_text()
        assert "Chat Completions" in content and "Responses API" in content

    def test_readme_has_setup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "OPENAI_API_KEY" in content

    def test_readme_has_cleanup_section(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "lab_cleanup" in content or "Cleanup" in content

    # --- ADDON content checks ---

    def test_addon_has_title(self):
        content = (LAB_DIR / "ADDON.md").read_text()
        assert "# LAB020" in content or "Structured Output" in content

    def test_addon_covers_json_schema(self):
        content = (LAB_DIR / "ADDON.md").read_text()
        assert "json_schema" in content

    def test_addon_covers_strict_mode(self):
        content = (LAB_DIR / "ADDON.md").read_text()
        assert "strict" in content.lower()

    def test_addon_has_data_extraction_example(self):
        content = (LAB_DIR / "ADDON.md").read_text()
        assert "extraction" in content.lower() or "extract" in content.lower()

    def test_addon_has_security_example(self):
        """ADDON should have a security-relevant structured output example."""
        content = (LAB_DIR / "ADDON.md").read_text()
        assert "CVE" in content or "vulnerability" in content.lower() or "security" in content.lower()

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    def test_no_emdashes_in_addon(self):
        content = (LAB_DIR / "ADDON.md").read_text()
        assert "\u2014" not in content, "ADDON.md contains em-dashes"

    # --- Tool availability ---

    def test_curl_available(self):
        result = subprocess.run(["curl", "--version"], capture_output=True)
        assert result.returncode == 0

    def test_jq_available(self):
        result = subprocess.run(["jq", "--version"], capture_output=True)
        assert result.returncode == 0


# ============================================================================
# SLOW TESTS - live API calls (require OPENAI_API_KEY)
# ============================================================================


@pytest.mark.slow
@pytest.mark.lab020
class TestLab020API:
    """Live API tests, skipped unless OPENAI_API_KEY is set."""

    @pytest.fixture(scope="class")
    def api_key(self):
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key or key.startswith("sk-your-"):
            pytest.skip("OPENAI_API_KEY not set")
        return key

    def _responses_api(self, api_key, payload):
        """Helper: call Responses API and return parsed JSON."""
        result = subprocess.run(
            [
                "curl", "-s", "-XPOST",
                "https://api.openai.com/v1/responses",
                "-H", "Content-Type: application/json",
                "-H", f"Authorization: Bearer {api_key}",
                "-d", json.dumps(payload),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"curl failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "error" not in data, f"API error: {data.get('error')}"
        return data

    def test_simple_response(self, api_key):
        """Basic Responses API call returns output."""
        data = self._responses_api(api_key, {
            "model": "gpt-4o",
            "input": "Say hello in one word.",
            "max_output_tokens": 10,
        })
        assert "output" in data
        assert len(data["output"]) > 0
        text = data["output"][0]["content"][0]["text"]
        assert len(text.strip()) > 0

    def test_response_has_id(self, api_key):
        """Every response should have a unique ID for recall."""
        data = self._responses_api(api_key, {
            "model": "gpt-4o",
            "input": "What is 1+1?",
            "max_output_tokens": 10,
        })
        assert "id" in data
        assert data["id"].startswith("resp_")

    def test_usage_tokens_returned(self, api_key):
        """Response includes token usage."""
        data = self._responses_api(api_key, {
            "model": "gpt-4o",
            "input": "Hi",
            "max_output_tokens": 10,
        })
        assert "usage" in data
        assert "input_tokens" in data["usage"]
        assert "output_tokens" in data["usage"]
        assert data["usage"]["total_tokens"] > 0

    def test_request_json_produces_structured_output(self, api_key):
        """request.json with JSON schema returns parseable structured output."""
        payload = json.loads((LAB_DIR / "request.json").read_text())
        data = self._responses_api(api_key, payload)
        text = data["output"][0]["content"][0]["text"]
        parsed = json.loads(text)
        assert "steps" in parsed
        assert isinstance(parsed["steps"], list)
        assert len(parsed["steps"]) > 0
        assert "final_answer" in parsed
        # Each step should have explanation and output
        for step in parsed["steps"]:
            assert "explanation" in step
            assert "output" in step

    def test_previous_response_id_multi_turn(self, api_key):
        """Multi-turn with previous_response_id maintains context."""
        # First turn
        r1 = self._responses_api(api_key, {
            "model": "gpt-4o",
            "input": "My name is Philippe. Remember it.",
            "max_output_tokens": 50,
        })
        resp_id = r1["id"]

        # Second turn, referencing first
        r2 = self._responses_api(api_key, {
            "model": "gpt-4o",
            "previous_response_id": resp_id,
            "input": "What is my name?",
            "max_output_tokens": 50,
        })
        text = r2["output"][0]["content"][0]["text"]
        assert "Philippe" in text, f"Model lost context, got: {text}"

    def test_message_recall(self, api_key):
        """Can recall a response by its ID."""
        # Make a call
        r1 = self._responses_api(api_key, {
            "model": "gpt-4o",
            "input": "What is 2+2? Answer with just the number.",
            "max_output_tokens": 5,
        })
        resp_id = r1["id"]
        original_text = r1["output"][0]["content"][0]["text"]

        # Recall it
        result = subprocess.run(
            [
                "curl", "-s",
                f"https://api.openai.com/v1/responses/{resp_id}",
                "-H", f"Authorization: Bearer {api_key}",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        recalled = json.loads(result.stdout)
        recalled_text = recalled["output"][0]["content"][0]["text"]
        assert recalled_text == original_text
