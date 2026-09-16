"""
Tests for lab078_Agents_MCP_Skills.

Smoke tests: existence, syntax, skill structure, and the deterministic grader
logic (no key, no network). One slow test runs agent_01 end to end and needs
OPENAI_API_KEY.
"""

import ast
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from tests.conftest import require_env

LAB_DIR = pathlib.Path(__file__).resolve().parent.parent / "lab078_Agents_MCP_Skills"

SCRIPTS = [
    "common.py",
    "mcp_server.py",
    "skills_runtime.py",
    "agent_01_mcp.py",
    "agent_02_simple_skill.py",
    "agent_03_power_skill.py",
    "skills/http-header-audit/scripts/audit_headers.py",
    "native/anthropic_skill_example.py",
]

FIXTURES = [
    "skills/incident-note/SKILL.md",
    "skills/http-header-audit/SKILL.md",
    "skills/http-header-audit/references/grading.md",
    "native/openai_uploaded_skill.sh",
]

GRADER = "skills/http-header-audit/scripts/audit_headers.py"


@pytest.mark.smoke
@pytest.mark.lab078
class TestLab078Smoke:
    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir()

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    @pytest.mark.parametrize("script", SCRIPTS)
    def test_script_exists_and_parses(self, script):
        p = LAB_DIR / script
        assert p.is_file(), f"missing {script}"
        ast.parse(p.read_text(), filename=script)

    @pytest.mark.parametrize("fixture", FIXTURES)
    def test_fixture_exists(self, fixture):
        assert (LAB_DIR / fixture).is_file(), f"missing {fixture}"

    def test_requirements(self):
        c = (LAB_DIR / "requirements.txt").read_text().lower()
        assert "openai-agents" in c and "fastmcp" in c

    def test_readme_title(self):
        assert "# LAB078" in (LAB_DIR / "README.md").read_text()

    def test_no_em_dashes(self):
        for p in [LAB_DIR / "README.md", *(LAB_DIR / s for s in SCRIPTS)]:
            assert "—" not in p.read_text(), f"em-dash in {p.name}"

    def test_skill_front_matter(self):
        for f in ["skills/incident-note/SKILL.md", "skills/http-header-audit/SKILL.md"]:
            head = (LAB_DIR / f).read_text().splitlines()
            assert head[0] == "---" and any(l.startswith("name:") for l in head[:6])
            assert any(l.startswith("description:") for l in head[:6])

    def test_mcp_server_defines_http_get(self):
        assert "def http_get" in (LAB_DIR / "mcp_server.py").read_text()

    def test_native_skill_layout(self):
        """Skill folders match the OpenAI/Anthropic native layout (scripts/, references/)."""
        base = LAB_DIR / "skills/http-header-audit"
        assert (base / "SKILL.md").is_file()
        assert (base / "scripts/audit_headers.py").is_file()
        assert (base / "references/grading.md").is_file()

    def test_native_examples_reference_correct_api(self):
        sh = (LAB_DIR / "native/openai_uploaded_skill.sh").read_text()
        assert "/v1/skills" in sh and "skill_reference" in sh and "container_auto" in sh
        py = (LAB_DIR / "native/anthropic_skill_example.py").read_text()
        assert "code_execution_20250825" in py and "container=" in py and "files_from_dir" in py

    def test_runtime_exposes_three_skill_tools(self):
        c = (LAB_DIR / "skills_runtime.py").read_text()
        for name in ["read_skill", "read_reference", "run_skill_script", "SKILL_TOOLS"]:
            assert name in c


# --- grader logic, deterministic, no key ---

def _load_grader():
    spec = importlib.util.spec_from_file_location(
        "audit_headers", LAB_DIR / GRADER
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.smoke
@pytest.mark.lab078
class TestHeaderGrader:
    def test_empty_is_F(self):
        g = _load_grader().grade({})
        assert g["grade"] == "F" and g["score"] == 0.0

    def test_full_stack_is_A(self):
        g = _load_grader().grade({
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=()",
        })
        assert g["grade"] == "A" and g["score"] == 100.0

    def test_case_insensitive_lookup(self):
        g = _load_grader().grade({"x-content-type-options": "nosniff"})
        row = next(r for r in g["rows"] if r["header"] == "X-Content-Type-Options")
        assert row["note"] == "good"

    def test_hsts_maxage_zero_is_broken(self):
        g = _load_grader().grade({"Strict-Transport-Security": "max-age=0"})
        row = next(r for r in g["rows"] if r["header"] == "Strict-Transport-Security")
        assert row["score"] < 25

    def test_disclosure_flagged_not_scored(self):
        g = _load_grader().grade({"Server": "nginx/1.18.0", "X-Powered-By": "PHP/7.4"})
        assert {d["header"] for d in g["disclosures"]} == {"Server", "X-Powered-By"}

    def test_cli_accepts_wrapper_and_raw(self):
        script = LAB_DIR / GRADER
        for payload in ['{"X-Content-Type-Options":"nosniff"}', '{"headers":{"X-Content-Type-Options":"nosniff"}}']:
            r = subprocess.run([sys.executable, str(script)], input=payload, capture_output=True, text=True)
            assert r.returncode == 0 and "Overall:" in r.stdout


# --- slow: real agent run ---

@pytest.mark.slow
@pytest.mark.lab078
class TestLab078Live:
    @require_env("OPENAI_API_KEY")
    def test_agent_01_runs(self):
        pytest.importorskip("agents")
        r = subprocess.run(
            [sys.executable, "agent_01_mcp.py"],
            cwd=LAB_DIR, capture_output=True, text=True, timeout=300,
        )
        assert r.returncode == 0, r.stderr[-2000:]
        assert "MCP tools discovered" in r.stdout
