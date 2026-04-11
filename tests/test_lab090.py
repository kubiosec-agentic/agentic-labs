"""
Tests for lab090_Enterprise - Enterprise-Ready Agent Systems.
Smoke tests validate structure, syntax, and content without API calls.
"""

import ast
import os
import pathlib

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab090_Enterprise"

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.smoke
@pytest.mark.lab090
class TestLab090Smoke:
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

    @pytest.mark.parametrize("script", [
        "traceloop_01.py",
        "traceloop_02.py",
        "openai_trace_01.py",
        "openai_trace_02.py",
        "rag_metadata_01.py",
        "rag_metadata_02.py",
        "rag_metadata_03.py",
        "rag_metadata_04.py",
        "verify_persistence.py",
    ])
    def test_script_exists(self, script):
        assert (LAB_DIR / script).is_file()

    # -- syntax validation --------------------------------------------------

    @pytest.mark.parametrize("script", [
        "traceloop_01.py",
        "traceloop_02.py",
        "openai_trace_01.py",
        "openai_trace_02.py",
        "rag_metadata_01.py",
        "rag_metadata_02.py",
        "rag_metadata_03.py",
        "rag_metadata_04.py",
        "verify_persistence.py",
    ])
    def test_script_valid_syntax(self, script):
        source = (LAB_DIR / script).read_text()
        ast.parse(source, filename=script)

    # -- setup scripts are executable ---------------------------------------

    def test_lab_setup_is_executable(self):
        assert os.access(LAB_DIR / "lab_setup.sh", os.X_OK)

    def test_lab_cleanup_is_executable(self):
        assert os.access(LAB_DIR / "lab_cleanup.sh", os.X_OK)

    # -- docker subdirectory ------------------------------------------------

    def test_docker_agent_directory_exists(self):
        assert (LAB_DIR / "docker_agent").is_dir()

    # -- requirements checks ------------------------------------------------

    def test_requirements_has_traceloop_or_opentelemetry(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "traceloop-sdk" in req or "opentelemetry" in req, \
            "requirements.txt should have traceloop-sdk or opentelemetry"

    def test_requirements_has_openai(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "openai" in req

    def test_requirements_has_chromadb(self):
        req = (LAB_DIR / "requirements.txt").read_text()
        assert "chromadb" in req

    # -- README content checks ----------------------------------------------

    def test_readme_has_title(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "LAB090" in readme

    def test_readme_documents_traceloop_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "traceloop" in readme.lower()

    def test_readme_documents_openai_trace_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "openai_trace" in readme or "OpenAI" in readme

    def test_readme_documents_rag_metadata_scripts(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "rag_metadata" in readme or "RAG" in readme

    def test_readme_has_setup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "set up" in readme or "setup" in readme

    def test_readme_has_cleanup_section(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "cleanup" in readme

    def test_readme_mentions_enterprise(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "enterprise" in readme or "production" in readme

    def test_readme_mentions_observability_or_tracing(self):
        readme = (LAB_DIR / "README.md").read_text().lower()
        assert "observ" in readme or "trac" in readme or "monitor" in readme

    # -- em-dash check ------------------------------------------------------

    def test_no_emdashes_in_readme(self):
        readme = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in readme, "README contains em-dashes"

    def test_no_emdashes_in_scripts(self):
        for py in LAB_DIR.glob("*.py"):
            if py.name != "__pycache__":
                src = py.read_text()
                assert "\u2014" not in src, f"{py.name} contains em-dashes"
