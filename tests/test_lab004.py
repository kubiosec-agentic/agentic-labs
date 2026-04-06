"""
Tests for lab004_transformers — Decoder generation (Qwen) & Encoder extraction (RoBERTa).

Smoke tests:  file existence, syntax, import checks          (~seconds)
Slow tests:   model download, tokenization, inference         (~1-3 min first run, cached after)
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent / "lab004_transformers"

# ============================================================================
# SMOKE TESTS — fast, no model download
# ============================================================================


@pytest.mark.smoke
@pytest.mark.lab004
class TestLab004Smoke:
    """Quick structural checks that run in seconds."""

    def test_lab_directory_exists(self):
        assert LAB_DIR.is_dir(), f"Lab directory missing: {LAB_DIR}"

    def test_demo_py_exists(self):
        assert (LAB_DIR / "demo.py").is_file()

    def test_roberta_py_exists(self):
        assert (LAB_DIR / "roberta.py").is_file()

    def test_dockerfile_exists(self):
        assert (LAB_DIR / "Dockerfile").is_file()

    def test_docker_compose_exists(self):
        assert (LAB_DIR / "docker-compose.yml").is_file()

    def test_requirements_docker_exists(self):
        assert (LAB_DIR / "requirements_docker.txt").is_file()

    def test_readme_exists(self):
        assert (LAB_DIR / "README.md").is_file()

    def test_demo_py_valid_syntax(self):
        """Parse demo.py to check for syntax errors without executing."""
        source = (LAB_DIR / "demo.py").read_text()
        ast.parse(source, filename="demo.py")

    def test_roberta_py_valid_syntax(self):
        """Parse roberta.py to check for syntax errors without executing."""
        source = (LAB_DIR / "roberta.py").read_text()
        ast.parse(source, filename="roberta.py")

    def test_demo_imports_torch(self):
        """Verify demo.py imports torch (structural check, no execution)."""
        source = (LAB_DIR / "demo.py").read_text()
        assert "import torch" in source

    def test_demo_imports_transformers(self):
        source = (LAB_DIR / "demo.py").read_text()
        assert "from transformers import" in source

    def test_roberta_uses_pipeline(self):
        source = (LAB_DIR / "roberta.py").read_text()
        assert "pipeline" in source

    def test_demo_uses_qwen_model(self):
        source = (LAB_DIR / "demo.py").read_text()
        assert "Qwen" in source

    def test_roberta_uses_roberta_model(self):
        source = (LAB_DIR / "roberta.py").read_text()
        assert "roberta" in source.lower()

    def test_requirements_docker_has_core_deps(self):
        content = (LAB_DIR / "requirements_docker.txt").read_text()
        assert "transformers" in content
        assert "torch" in content

    def test_can_import_torch(self):
        """Verify torch is installed in the current environment."""
        import torch  # noqa: F401

    def test_can_import_transformers(self):
        """Verify transformers is installed in the current environment."""
        import transformers  # noqa: F401


# ============================================================================
# SLOW TESTS — download models, run inference
# ============================================================================


@pytest.mark.slow
@pytest.mark.lab004
class TestLab004Qwen:
    """Functional tests for demo.py — Qwen causal generation."""

    @pytest.fixture(scope="class")
    def qwen_model_and_tokenizer(self):
        """Download and cache the Qwen model + tokenizer (shared across class)."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_id = "Qwen/Qwen2.5-0.5B"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
        model.to(torch.device("cpu"))
        return model, tokenizer

    def test_tokenizer_encodes(self, qwen_model_and_tokenizer):
        """Tokenizer produces non-empty input_ids."""
        _, tokenizer = qwen_model_and_tokenizer
        inputs = tokenizer("Hello world", return_tensors="pt")
        assert inputs["input_ids"].shape[1] > 0

    def test_model_generates_output(self, qwen_model_and_tokenizer):
        """Model generates at least some tokens beyond the prompt."""
        import torch

        model, tokenizer = qwen_model_and_tokenizer
        prompt = "What is AI?"
        inputs = tokenizer(prompt, return_tensors="pt").to(torch.device("cpu"))
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_new_tokens=20,
            do_sample=False,  # deterministic for testing
            pad_token_id=tokenizer.eos_token_id,
        )
        # Output should be longer than input
        assert outputs.shape[1] > inputs["input_ids"].shape[1]

    def test_decoded_output_is_string(self, qwen_model_and_tokenizer):
        """Decoded output is a non-empty string."""
        import torch

        model, tokenizer = qwen_model_and_tokenizer
        inputs = tokenizer("Explain Log4j", return_tensors="pt").to(torch.device("cpu"))
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_new_tokens=10,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        assert isinstance(text, str)
        assert len(text) > 0


@pytest.mark.slow
@pytest.mark.lab004
class TestLab004Roberta:
    """Functional tests for roberta.py — extractive QA."""

    @pytest.fixture(scope="class")
    def qa_pipeline(self):
        """Download and cache the RoBERTa QA pipeline (shared across class)."""
        from transformers import pipeline

        return pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2",
            device="cpu",
        )

    def test_pipeline_returns_dict(self, qa_pipeline):
        """Pipeline returns a dictionary with expected keys."""
        result = qa_pipeline(
            question="Who wrote The Hobbit?",
            context="The Hobbit is a fantasy novel by J. R. R. Tolkien.",
        )
        assert isinstance(result, dict)
        assert "answer" in result
        assert "score" in result
        assert "start" in result
        assert "end" in result

    def test_correct_answer_extracted(self, qa_pipeline):
        """Pipeline extracts the right answer from context."""
        result = qa_pipeline(
            question="Who wrote The Hobbit?",
            context="The Hobbit is a fantasy novel by J. R. R. Tolkien.",
        )
        assert "Tolkien" in result["answer"]

    def test_confidence_score_range(self, qa_pipeline):
        """Confidence score is between 0 and 1."""
        result = qa_pipeline(
            question="Who wrote The Hobbit?",
            context="The Hobbit is a fantasy novel by J. R. R. Tolkien.",
        )
        assert 0.0 <= result["score"] <= 1.0

    def test_unanswerable_question_low_score(self, qa_pipeline):
        """Unanswerable question should produce a low confidence score."""
        result = qa_pipeline(
            question="What is the capital of Mars?",
            context="The Hobbit is a fantasy novel by J. R. R. Tolkien.",
        )
        # RoBERTa SQuAD 2.0 can signal "no answer" — score should be low
        assert result["score"] < 0.5
