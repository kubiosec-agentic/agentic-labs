"""
Tests for lab122_runtime - Runtime Security Monitoring with Tetragon.

Smoke tests: file existence, script syntax, README checks, treejson logic validation (~seconds)
"""

import ast
import pathlib
import sys

import pytest

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab122_runtime"

# ============================================================================
# SMOKE TESTS - fast, no external tools required
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab122
class TestLab122Smoke:
    """Quick structural checks that run in seconds."""

    # --- Directory and file existence ---

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_treejson_py_exists(self):
        assert (LAB_DIR / "treejson.py").is_file()

    # --- No requirements.txt, no setup/cleanup scripts (pure stdlib) ---

    def test_no_requirements_txt(self):
        """lab122 is pure Python stdlib, no requirements.txt."""
        assert not (LAB_DIR / "requirements.txt").exists()

    def test_no_lab_setup_sh(self):
        """lab122 does not have a setup script."""
        assert not (LAB_DIR / "lab_setup.sh").exists()

    def test_no_lab_cleanup_sh(self):
        """lab122 does not have a cleanup script."""
        assert not (LAB_DIR / "lab_cleanup.sh").exists()

    # --- Python script syntax ---

    def test_treejson_py_syntax(self):
        """treejson.py should parse without syntax errors."""
        content = (LAB_DIR / "treejson.py").read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in treejson.py: {e}")

    # --- README content checks ---

    def test_readme_has_title(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "LAB122" in content

    def test_readme_mentions_tetragon(self):
        """README should document Tetragon."""
        content = (LAB_DIR / "README.md").read_text()
        assert "Tetragon" in content

    def test_readme_mentions_runtime_security(self):
        """README should discuss runtime security."""
        content = (LAB_DIR / "README.md").read_text()
        assert "runtime" in content.lower() or "security" in content.lower()

    def test_readme_mentions_ebpf(self):
        """README should mention eBPF."""
        content = (LAB_DIR / "README.md").read_text()
        assert "eBPF" in content or "ebpf" in content.lower()

    def test_readme_mentions_process_tree(self):
        """README should document process tree analysis."""
        content = (LAB_DIR / "README.md").read_text()
        assert "process" in content.lower() and "tree" in content.lower()

    def test_readme_mentions_docker(self):
        """README should mention Docker/containers."""
        content = (LAB_DIR / "README.md").read_text()
        assert "docker" in content.lower() or "container" in content.lower()

    def test_readme_mentions_linux(self):
        """README should note Linux requirement."""
        content = (LAB_DIR / "README.md").read_text()
        assert "Linux" in content or "linux" in content.lower()

    # --- No em-dashes ---

    def test_no_emdashes_in_readme(self):
        content = (LAB_DIR / "README.md").read_text()
        assert "\u2014" not in content, "README.md contains em-dashes"

    def test_no_emdashes_in_treejson_py(self):
        content = (LAB_DIR / "treejson.py").read_text()
        assert "\u2014" not in content, "treejson.py contains em-dashes"

    # --- treejson.py logic validation ---

    def test_treejson_build_tree(self):
        """Test treejson.build_tree with synthetic process event data."""
        # Import treejson from the lab directory
        sys.path.insert(0, str(LAB_DIR))
        try:
            from treejson import load_events, build_tree
        finally:
            sys.path.pop(0)

        # Synthetic process events matching Tetragon event structure
        events = [
            {
                "process_exec": {
                    "process": {
                        "exec_id": "p1",
                        "binary": "/bin/bash",
                        "pid": 1,
                    },
                    "parent": {
                        "exec_id": "p0",
                        "binary": "/init",
                        "pid": 0,
                    },
                }
            },
            {
                "process_exec": {
                    "process": {
                        "exec_id": "p2",
                        "binary": "/usr/bin/python3",
                        "pid": 2,
                    },
                    "parent": {
                        "exec_id": "p1",
                        "binary": "/bin/bash",
                        "pid": 1,
                    },
                }
            },
        ]

        # Build the tree
        procs, children = build_tree(events)

        # Verify process entries exist
        assert "p0" in procs, "Root process p0 should be in procs"
        assert "p1" in procs, "Process p1 should be in procs"
        assert "p2" in procs, "Process p2 should be in procs"

        # Verify process metadata
        assert procs["p0"]["binary"] == "/init"
        assert procs["p1"]["binary"] == "/bin/bash"
        assert procs["p2"]["binary"] == "/usr/bin/python3"

        # Verify parent-child relationships
        assert "p1" in children["p0"], "p1 should be a child of p0"
        assert "p2" in children["p1"], "p2 should be a child of p1"

    def test_treejson_load_events(self):
        """Test treejson.load_events with JSON lines."""
        sys.path.insert(0, str(LAB_DIR))
        try:
            from treejson import load_events
        finally:
            sys.path.pop(0)

        # Sample JSONL input
        json_lines = [
            '{"process_exec": {"process": {"exec_id": "p1", "binary": "/bin/sh", "pid": 100}, "parent": {"exec_id": "p0", "binary": "/init", "pid": 1}}}',
            '{"process_exit": {"process": {"exec_id": "p1", "binary": "/bin/sh", "pid": 100}}}',
            'invalid json line',  # Should be skipped
            '{"process_exec": {"process": {"exec_id": "p2", "binary": "/usr/bin/python", "pid": 101}, "parent": {"exec_id": "p1", "binary": "/bin/sh", "pid": 100}}}',
        ]

        # Load events (should skip invalid JSON)
        events = load_events(json_lines)

        # Should have 3 valid events (skipped the invalid line)
        assert len(events) == 3, f"Expected 3 events, got {len(events)}"
        assert events[0]["process_exec"]["process"]["exec_id"] == "p1"
        assert events[1]["process_exit"]["process"]["exec_id"] == "p1"
        assert events[2]["process_exec"]["process"]["exec_id"] == "p2"

    def test_treejson_handles_empty_events(self):
        """Test treejson.build_tree with empty event list."""
        sys.path.insert(0, str(LAB_DIR))
        try:
            from treejson import build_tree
        finally:
            sys.path.pop(0)

        procs, children = build_tree([])
        assert len(procs) == 0
        assert len(children) == 0

    def test_treejson_handles_process_exit_events(self):
        """Test that process_exit events populate process info."""
        sys.path.insert(0, str(LAB_DIR))
        try:
            from treejson import build_tree
        finally:
            sys.path.pop(0)

        events = [
            {
                "process_exit": {
                    "process": {
                        "exec_id": "p1",
                        "binary": "/bin/sh",
                        "pid": 100,
                    }
                }
            },
        ]

        procs, children = build_tree(events)

        # process_exit should populate the procs dictionary
        assert "p1" in procs
        assert procs["p1"]["binary"] == "/bin/sh"
        assert procs["p1"]["pid"] == 100
