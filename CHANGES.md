# Changes

Maintenance log for the labs (not part of the student material).

## 2026-09-02

### lab004_transformers
- `roberta.py`: rewritten with `AutoModelForQuestionAnswering` (tokenize → model → argmax start/end → decode). The `question-answering` pipeline was removed in `transformers` 5.x (verified on 5.16.1).
- `demo.py`: verified working on `transformers` 5.16.1 / `torch` 2.14; the earlier "degraded output on 5.x" observation was sampling variance, not a bug.
- Dropped the `transformers<5` pin in `requirements_docker.txt`; added `requirements.txt` so `lab_setup.sh` creates the venv for Option A.
- README: documented Option A commands.
- Added optional Example 3: `transformers serve` (OpenAI-compatible endpoint, CPU). Requires `transformers[serving]` + `requests` (the `serving` extra in 5.16.1 forgets `requests`); both added to the requirements files. A vLLM version was tried first and dropped (needs an NVIDIA GPU, nobody can test it).
