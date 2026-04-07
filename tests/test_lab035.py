"""
Tests for lab035_Langchain.
Smoke tests validate structure, syntax, and content without API calls.
Slow tests make real API calls and require OPENAI_API_KEY.
"""

import ast
import json
import os
import pathlib
import subprocess
import sys
import textwrap

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab035_Langchain"

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.lab035
class TestLab035Smoke:
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

    def test_chat_py_exists(self):
        assert (LAB_DIR / "chat.py").is_file()

    def test_prompt_py_exists(self):
        assert (LAB_DIR / "prompt.py").is_file()

    def test_advanced_prompting_py_exists(self):
        assert (LAB_DIR / "advanced_prompting.py").is_file()

    def test_multi_turn_py_exists(self):
        assert (LAB_DIR / "multi-turn.py").is_file()

    def test_hf_local_py_exists(self):
        assert (LAB_DIR / "hf_local.py").is_file()

    def test_doc_directory_exists(self):
        assert (LAB_DIR / "doc").is_dir()

    @pytest.mark.parametrize("doc_file", [
        "chat.md", "prompt.md", "advanced_prompting.md",
        "multi-turn.md", "huggingface.md",
    ])
    def test_doc_files_exist(self, doc_file):
        assert (LAB_DIR / "doc" / doc_file).is_file()

    # -- syntax validation --------------------------------------------------

    @pytest.mark.parametrize("script", [
        "chat.py", "prompt.py", "advanced_prompting.py",
        "multi-turn.py", "hf_local.py",
    ])
    def test_script_valid_syntax(self, script):
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # -- setup scripts are executable ---------------------------------------

    def test_lab_setup_is_executable(self):
        assert os.access(LAB_DIR / "lab_setup.sh", os.X_OK)

    def test_lab_cleanup_is_executable(self):
        assert os.access(LAB_DIR / "lab_cleanup.sh", os.X_OK)

    # -- model references ---------------------------------------------------

    def test_chat_uses_gpt4o(self):
        src = (LAB_DIR / "chat.py").read_text()
        # Active (uncommented) model instantiation should be gpt-4o
        for line in src.splitlines():
            if line.strip().startswith("#"):
                continue
            if "ChatOpenAI(" in line and "model=" in line:
                assert "gpt-4o" in line, f"Expected gpt-4o, got: {line}"

    def test_prompt_uses_gpt4o(self):
        src = (LAB_DIR / "prompt.py").read_text()
        for line in src.splitlines():
            if line.strip().startswith("#"):
                continue
            if "ChatOpenAI(" in line and "model=" in line:
                assert "gpt-4o" in line, f"Expected gpt-4o, got: {line}"

    def test_no_gpt35_turbo_active(self):
        """gpt-3.5-turbo should not appear as an active model anywhere."""
        for py in LAB_DIR.glob("*.py"):
            src = py.read_text()
            for line in src.splitlines():
                if line.strip().startswith("#"):
                    continue
                assert "gpt-3.5-turbo" not in line, \
                    f"Outdated gpt-3.5-turbo in {py.name}: {line}"

    def test_no_gpt5_mini_active(self):
        """gpt-5-mini is not a valid model name."""
        for py in LAB_DIR.glob("*.py"):
            src = py.read_text()
            for line in src.splitlines():
                if line.strip().startswith("#"):
                    continue
                assert "gpt-5-mini" not in line, \
                    f"Invalid gpt-5-mini in {py.name}: {line}"

    # -- structural content checks ------------------------------------------

    def test_chat_uses_langchain_openai(self):
        src = (LAB_DIR / "chat.py").read_text()
        assert "from langchain_openai" in src

    def test_chat_uses_invoke(self):
        src = (LAB_DIR / "chat.py").read_text()
        assert ".invoke(" in src

    def test_prompt_uses_prompt_template(self):
        src = (LAB_DIR / "prompt.py").read_text()
        assert "PromptTemplate" in src

    def test_prompt_uses_pipe_operator(self):
        src = (LAB_DIR / "prompt.py").read_text()
        assert "|" in src

    def test_advanced_uses_chat_prompt_template(self):
        src = (LAB_DIR / "advanced_prompting.py").read_text()
        assert "ChatPromptTemplate" in src

    def test_advanced_uses_system_message(self):
        src = (LAB_DIR / "advanced_prompting.py").read_text()
        assert "SystemMessagePromptTemplate" in src

    def test_multi_turn_uses_message_history(self):
        src = (LAB_DIR / "multi-turn.py").read_text()
        assert "RunnableWithMessageHistory" in src

    def test_multi_turn_uses_session_id(self):
        src = (LAB_DIR / "multi-turn.py").read_text()
        assert "session_id" in src

    def test_hf_local_uses_huggingface_pipeline(self):
        src = (LAB_DIR / "hf_local.py").read_text()
        assert "HuggingFacePipeline" in src

    def test_hf_local_uses_qwen(self):
        src = (LAB_DIR / "hf_local.py").read_text()
        assert "Qwen" in src

    # -- requirements checks ------------------------------------------------

    def test_requirements_has_langchain_openai(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain-openai" in req

    def test_requirements_has_langchain_core(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain-core" in req

    def test_requirements_has_version_pins(self):
        """Requirements should have version constraints, not bare package names."""
        req = (LAB_DIR / "requirements.txt").read_text()
        for line in req.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            assert ">=" in line or "==" in line or "<" in line, \
                f"Missing version pin: {line}"

    def test_requirements_pins_transformers_below_5(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "<5" in req or "< 5" in req

    # -- README content checks ----------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB035" in readme

    def test_readme_documents_all_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        for script in ["chat.py", "prompt.py", "advanced_prompting.py",
                        "multi-turn.py", "hf_local.py"]:
            assert script in readme, f"{script} not mentioned in README"

    def test_readme_has_step_numbering(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "Step 1" in readme
        assert "Step 5" in readme

    def test_readme_references_lab064_for_langgraph(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "lab064" in readme

    def test_readme_has_cleanup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "cleanup" in readme

    def test_readme_has_setup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "set up" in readme or "setup" in readme

    # -- em-dash check ------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    def test_no_emdashes_in_scripts(self):
        for py in LAB_DIR.glob("*.py"):
            src = py.read_text()
            assert "\u2014" not in src, f"{py.name} contains em-dashes"

    def test_no_emdashes_in_docs(self):
        for md in (LAB_DIR / "doc").glob("*.md"):
            content = md.read_text()
            assert "\u2014" not in content, f"doc/{md.name} contains em-dashes"


# ---------------------------------------------------------------------------
# Slow tests (require OPENAI_API_KEY)
# ---------------------------------------------------------------------------

@pytest.mark.slow
@pytest.mark.lab035
class TestLab035Slow:
    """API tests that require OPENAI_API_KEY."""

    @pytest.fixture(autouse=True)
    def _require_key(self, env_key):
        """Skip if OPENAI_API_KEY is not set."""
        pass

    def test_chat_runs(self):
        """chat.py should produce output."""
        result = subprocess.run(
            [sys.executable, str(LAB_DIR / "chat.py")],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert len(result.stdout.strip()) > 10

    def test_prompt_runs(self):
        """prompt.py should produce an analysis."""
        result = subprocess.run(
            [sys.executable, str(LAB_DIR / "prompt.py")],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "Analysis" in result.stdout or len(result.stdout.strip()) > 20

    def test_advanced_prompting_runs(self):
        """advanced_prompting.py should return a joke."""
        result = subprocess.run(
            [sys.executable, str(LAB_DIR / "advanced_prompting.py")],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert len(result.stdout.strip()) > 10

    def test_multi_turn_runs(self):
        """multi-turn.py should produce multiple responses and message history."""
        result = subprocess.run(
            [sys.executable, str(LAB_DIR / "multi-turn.py")],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "Message History" in result.stdout
