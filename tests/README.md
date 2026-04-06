# Agentic-Labs Test Suite

Automated tests for lab exercises. Each lab has its own test file (`test_lab004.py`, `test_lab010.py`, etc.).

## Setup

```bash
pip install -r tests/requirements.txt
```

### API Keys

Most labs require API keys (OpenAI, Google, etc.). The test suite loads these from a `.env` file at the repo root:

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

Tests that need a missing key are **skipped** (not failed) — so you can always run the suite even with partial keys.

To see which keys are set and which labs are ready:

```bash
pytest --check-env
```

This prints a status report like:

```
  [+] OPENAI_API_KEY              SET
  [-] GOOGLE_API_KEY              MISSING
  ...
  Lab Readiness:
    lab004     READY  (no API keys needed)
    lab010     READY
    lab061     BLOCKED — missing: GOOGLE_API_KEY, SERP_API_KEY
```

## Running tests

```bash
# Smoke tests only (fast, no model downloads, no API calls)
pytest

# All tests including slow (model downloads ~1-3 min first run)
pytest --run-all

# Single lab
pytest -m lab004

# Single lab, smoke only
pytest -m "lab004 and smoke"

# Single lab, slow only (downloads models)
pytest -m "lab004 and slow"

# Full suite, all labs, all tests
pytest --run-all -v
```

## Test categories

| Marker | What it tests | Speed |
|--------|--------------|-------|
| `smoke` | File existence, syntax, imports, structural checks | Seconds |
| `slow` | Model downloads, inference, API calls | Minutes |

Smoke tests run by default. Slow tests are skipped unless you pass `--run-all` or select them explicitly with `-m slow`.

## Adding tests for a new lab

1. Create `tests/test_lab{NNN}.py`
2. Mark every test with `@pytest.mark.lab{NNN}` and either `@pytest.mark.smoke` or `@pytest.mark.slow`
3. Register the marker in `pytest.ini`
4. Add any new dependencies to `tests/requirements.txt`
5. If the lab needs API keys, use `require_env` or `env_key` from conftest:
   ```python
   from tests.conftest import require_env

   @require_env("OPENAI_API_KEY")
   def test_openai_call():
       ...
   ```
6. Add the lab's key requirements to `LAB_REQUIRED_KEYS` in `conftest.py`
