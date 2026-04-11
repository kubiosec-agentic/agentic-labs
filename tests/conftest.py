"""
Shared fixtures and configuration for agentic-labs tests.

Usage:
    pytest                          # Run smoke tests only (fast, no model downloads)
    pytest -m slow                  # Run only slow tests (model downloads, API calls)
    pytest -m "smoke or slow"       # Run everything
    pytest -m lab004                # Run only lab004 tests
    pytest -m "lab004 and smoke"    # Run only lab004 smoke tests
    pytest -m "lab004 and slow"     # Run only lab004 slow tests (downloads models)
    pytest --run-all                # Run all tests including slow
    pytest --check-env              # Show which API keys are set / missing
"""

import os
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Repo root so labs can be imported / located
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Load .env from repo root (if python-dotenv is available)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass  # python-dotenv not installed — rely on shell-exported vars


# ---------------------------------------------------------------------------
# API key registry — maps each lab to the env vars it requires
# ---------------------------------------------------------------------------
LAB_REQUIRED_KEYS: dict[str, list[str]] = {
    "lab004": [],                                        # local models only
    "lab010": ["OPENAI_API_KEY"],
    "lab020": ["OPENAI_API_KEY"],
    "lab032": ["OPENAI_API_KEY"],
    "lab035": ["OPENAI_API_KEY"],
    "lab040": ["OPENAI_API_KEY"],
    "lab050": ["OPENAI_API_KEY"],
    "lab054": ["OPENAI_API_KEY"],
    "lab060": ["OPENAI_API_KEY"],
    "lab061": ["GOOGLE_API_KEY", "SERP_API_KEY"],
    "lab064": ["OPENAI_API_KEY"],
    "lab070": ["OPENAI_API_KEY"],                        # mcp_05 also needs MCPCLOUD_API_TOKEN
    "lab071": [],                                        # inspector / debugging only
    "lab075": ["OPENAI_API_KEY"],
    "lab080": ["OPENAI_API_KEY"],                        # CrewAI optionally needs SERPER_API_KEY
    "lab085": ["OPENAI_API_KEY"],
    "lab087": ["OPENAI_API_KEY"],                        # managed mode also needs MEM0_API_KEY
    "lab090": ["OPENAI_API_KEY"],
    "lab105": ["OPENAI_API_KEY"],
    "lab110": ["OPENAI_API_KEY", "GOOGLE_API_KEY"],       # MS client + ADK server
    "lab120": ["OPENAI_API_KEY"],
    "lab122": [],                                        # Tetragon + stdlib only
}

# All known keys across every lab (order matches .env.example)
ALL_KNOWN_KEYS: list[str] = [
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "GOOGLE_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "SERP_API_KEY",
    "GITHUB_TOKEN",
    "MEM0_API_KEY",
    "MCP_SSE_URL",
    "MCPCLOUD_API_TOKEN",
]


def _key_is_set(key: str) -> bool:
    """Return True if the env var is set and non-empty."""
    val = os.environ.get(key, "")
    # Don't count placeholder values from .env.example copied as-is
    if not val or val.startswith("sk-your-") or val.startswith("your-") or val.startswith("ghp_your-"):
        return False
    return True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def repo_root():
    """Return the absolute path to the agentic-labs repo root."""
    return REPO_ROOT


@pytest.fixture
def lab_path(repo_root):
    """Factory fixture: lab_path('lab004_transformers') → full path."""
    def _get(lab_dir: str) -> Path:
        p = repo_root / lab_dir
        assert p.is_dir(), f"Lab directory not found: {p}"
        return p
    return _get


def require_env(*keys: str):
    """Decorator / marker helper: skip a test if any of the given keys are missing.

    Usage:
        @require_env("OPENAI_API_KEY")
        def test_openai_call():
            ...
    """
    missing = [k for k in keys if not _key_is_set(k)]
    return pytest.mark.skipif(
        len(missing) > 0,
        reason=f"Missing env var(s): {', '.join(missing)} — see .env.example",
    )


@pytest.fixture
def env_key():
    """Fixture that returns an env var value or skips the test if missing.

    Usage:
        def test_something(env_key):
            api_key = env_key("OPENAI_API_KEY")
    """
    def _get(key: str) -> str:
        if not _key_is_set(key):
            pytest.skip(f"Missing env var: {key} — see .env.example")
        return os.environ[key]
    return _get


# ---------------------------------------------------------------------------
# CLI options
# ---------------------------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--run-all",
        action="store_true",
        default=False,
        help="Run all tests including slow (model download) tests.",
    )
    parser.addoption(
        "--check-env",
        action="store_true",
        default=False,
        help="Print API key status report and exit.",
    )


# ---------------------------------------------------------------------------
# --check-env: print key status and exit
# ---------------------------------------------------------------------------
def pytest_sessionstart(session):
    if session.config.getoption("--check-env", default=False):
        print("\n" + "=" * 60)
        print("  API Key Status Report")
        print("=" * 60)

        for key in ALL_KNOWN_KEYS:
            status = "SET" if _key_is_set(key) else "MISSING"
            icon = "+" if _key_is_set(key) else "-"
            print(f"  [{icon}] {key:<25s} {status}")

        print("-" * 60)

        # Per-lab readiness
        print("\n  Lab Readiness:")
        for lab, keys in sorted(LAB_REQUIRED_KEYS.items()):
            if not keys:
                print(f"    {lab:<10s} READY  (no API keys needed)")
            else:
                missing = [k for k in keys if not _key_is_set(k)]
                if missing:
                    print(f"    {lab:<10s} BLOCKED — missing: {', '.join(missing)}")
                else:
                    print(f"    {lab:<10s} READY")

        print("=" * 60 + "\n")
        pytest.exit("--check-env complete", returncode=0)


def pytest_collection_modifyitems(config, items):
    """By default, skip tests marked 'slow' unless --run-all or -m slow."""
    if config.getoption("--run-all"):
        return

    # If user explicitly selected slow with -m, don't skip
    markexpr = config.getoption("-m", default="")
    if "slow" in markexpr:
        return

    skip_slow = pytest.mark.skip(reason="Needs --run-all or -m slow (downloads models)")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
