"""
Tests for lab040_RAG.
Smoke tests validate structure, syntax, and content without API calls.
Slow tests make real API calls and require OPENAI_API_KEY.
"""

import ast
import os
import pathlib
import subprocess
import sys

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab040_RAG"

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.lab040
class TestLab040Smoke:
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

    def test_dockerfile_exists(self):
        assert (LAB_DIR / "Dockerfile").is_file()

    def test_docker_compose_exists(self):
        assert (LAB_DIR / "docker-compose.yml").is_file()

    @pytest.mark.parametrize("script", [
        "RAG_01.py", "RAG_02.py", "RAG_03.py", "RAG_04.py", "RAG_05_agentic.py",
    ])
    def test_script_exists(self, script):
        assert (LAB_DIR / script).is_file()

    def test_arag_directory_exists(self):
        assert (LAB_DIR / "ARAG").is_dir()

    def test_arag_doc_exists(self):
        assert (LAB_DIR / "ARAG" / "AgenticRAG.md").is_file()

    def test_data_directory_exists(self):
        assert (LAB_DIR / "data").is_dir()

    def test_data_has_text_file(self):
        assert (LAB_DIR / "data" / "llms-full.txt").is_file()

    # -- syntax validation --------------------------------------------------

    @pytest.mark.parametrize("script", [
        "RAG_01.py", "RAG_02.py", "RAG_03.py", "RAG_04.py", "RAG_05_agentic.py",
    ])
    def test_script_valid_syntax(self, script):
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # -- setup scripts are executable ---------------------------------------

    def test_lab_setup_is_executable(self):
        assert os.access(LAB_DIR / "lab_setup.sh", os.X_OK)

    def test_lab_cleanup_is_executable(self):
        assert os.access(LAB_DIR / "lab_cleanup.sh", os.X_OK)

    # -- embedding model checks ---------------------------------------------

    def test_rag01_uses_embedding_3_small(self):
        """RAG_01 should use text-embedding-3-small, not ada-002."""
        src = (LAB_DIR / "RAG_01.py").read_text()
        assert "text-embedding-3-small" in src
        # ada-002 should not appear as active
        for line in src.splitlines():
            if line.strip().startswith("#"):
                continue
            assert "ada-002" not in line, f"Outdated ada-002 in RAG_01.py: {line}"

    def test_rag05_uses_embedding_3_small(self):
        src = (LAB_DIR / "RAG_05_agentic.py").read_text()
        assert "text-embedding-3-small" in src

    # -- model checks -------------------------------------------------------

    def test_no_gpt35_active(self):
        """No active gpt-3.5-turbo references."""
        for py in LAB_DIR.glob("*.py"):
            src = py.read_text()
            for line in src.splitlines():
                if line.strip().startswith("#"):
                    continue
                assert "gpt-3.5-turbo" not in line, \
                    f"Outdated gpt-3.5-turbo in {py.name}: {line}"

    # -- structural content: RAG_01 (LlamaIndex) ---------------------------

    def test_rag01_uses_llama_index(self):
        src = (LAB_DIR / "RAG_01.py").read_text()
        assert "llama_index" in src

    def test_rag01_uses_vector_store_index(self):
        src = (LAB_DIR / "RAG_01.py").read_text()
        assert "VectorStoreIndex" in src

    def test_rag01_has_use_llm_toggle(self):
        src = (LAB_DIR / "RAG_01.py").read_text()
        assert "USE_LLM" in src

    # -- structural content: RAG_02/03 (LangChain + Chroma) ----------------

    def test_rag02_uses_chroma(self):
        src = (LAB_DIR / "RAG_02.py").read_text()
        assert "Chroma" in src

    def test_rag02_uses_text_splitter(self):
        src = (LAB_DIR / "RAG_02.py").read_text()
        assert "CharacterTextSplitter" in src

    def test_rag03_uses_recursive_splitter(self):
        src = (LAB_DIR / "RAG_03.py").read_text()
        assert "RecursiveCharacterTextSplitter" in src

    def test_rag03_has_prompt_template(self):
        src = (LAB_DIR / "RAG_03.py").read_text()
        assert "PromptTemplate" in src

    def test_rag03_uses_chat_openai(self):
        src = (LAB_DIR / "RAG_03.py").read_text()
        assert "ChatOpenAI" in src

    # -- structural content: RAG_04 (OpenAI Responses API) -----------------

    def test_rag04_uses_responses_api(self):
        src = (LAB_DIR / "RAG_04.py").read_text()
        assert "responses.create" in src

    def test_rag04_uses_file_search(self):
        src = (LAB_DIR / "RAG_04.py").read_text()
        assert "file_search" in src

    # -- structural content: RAG_05 (Agentic RAG) -------------------------

    def test_rag05_has_tool_spec(self):
        src = (LAB_DIR / "RAG_05_agentic.py").read_text()
        assert "tool_spec" in src or "tool_calls" in src

    def test_rag05_has_agent_loop(self):
        src = (LAB_DIR / "RAG_05_agentic.py").read_text()
        assert "while True" in src

    def test_rag05_has_vector_search_function(self):
        src = (LAB_DIR / "RAG_05_agentic.py").read_text()
        assert "def vector_search" in src

    def test_rag05_uses_cosine_similarity(self):
        src = (LAB_DIR / "RAG_05_agentic.py").read_text()
        # L2 normalization for cosine similarity
        assert "norm" in src

    # -- requirements checks ------------------------------------------------

    def test_requirements_has_openai(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in req

    def test_requirements_has_llama_index(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "llama-index-core" in req or "llama_index" in req

    def test_requirements_has_chroma(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "chroma" in req.lower()

    def test_requirements_has_langchain(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "langchain" in req

    def test_requirements_has_text_splitters(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "text-splitters" in req or "text_splitters" in req

    def test_requirements_has_version_pins(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        for line in req.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            assert ">=" in line or "==" in line or "<" in line, \
                f"Missing version pin: {line}"

    # -- README content checks ----------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB040" in readme

    def test_readme_documents_all_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        for script in ["RAG_01.py", "RAG_02.py", "RAG_03.py",
                        "RAG_04.py", "RAG_05_agentic.py"]:
            assert script in readme, f"{script} not mentioned in README"

    def test_readme_has_step_numbering(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "Step 1" in readme
        assert "Step 5" in readme

    def test_readme_has_framework_comparison(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LlamaIndex" in readme
        assert "Chroma" in readme
        assert "file_search" in readme

    def test_readme_references_addendum(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "lab990_addendum" in readme

    def test_readme_has_deprecation_note(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "deprecat" in readme.lower() or "August 2026" in readme

    def test_readme_has_setup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "set up" in readme or "setup" in readme

    def test_readme_has_cleanup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "cleanup" in readme

    def test_readme_has_docker_option(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "docker" in readme.lower()

    # -- em-dash check ------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    def test_no_emdashes_in_scripts(self):
        for py in LAB_DIR.glob("*.py"):
            src = py.read_text()
            assert "\u2014" not in src, f"{py.name} contains em-dashes"

    def test_no_emdashes_in_arag_doc(self):
        content = (LAB_DIR / "ARAG" / "AgenticRAG.md").read_text()
        assert "\u2014" not in content, "ARAG/AgenticRAG.md contains em-dashes"


# ---------------------------------------------------------------------------
# Slow tests (require OPENAI_API_KEY)
# ---------------------------------------------------------------------------

@pytest.mark.slow
@pytest.mark.lab040
class TestLab040Slow:
    """API tests that require OPENAI_API_KEY."""

    @pytest.fixture(autouse=True)
    def _require_key(self, env_key):
        pass

    def test_rag05_agentic_runs(self):
        """RAG_05_agentic.py should produce output (in-memory vector store + agent loop)."""
        result = subprocess.run(
            [sys.executable, str(LAB_DIR / "RAG_05_agentic.py")],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert len(result.stdout.strip()) > 20
