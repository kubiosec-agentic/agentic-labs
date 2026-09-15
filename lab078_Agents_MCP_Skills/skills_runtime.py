"""
A tiny "skills" runtime for the OpenAI Agents SDK.

The Agents SDK has no built-in notion of skills. This file bolts the
Claude-Code / Anthropic SKILL.md pattern onto it by hand, so you can see the
moving parts that a batteries-included harness (like deepagents in lab066)
hides:

  - A skill is a folder under skills/ with a SKILL.md that has YAML front
    matter (name, description) and a body of instructions.
  - Progressive disclosure: at startup we inject ONLY each skill's name and
    description into the agent's instructions (build_instructions). The full
    SKILL.md body, any helper scripts, and any reference files are pulled in
    on demand, through function tools, only when a task actually needs them.

The function tools below are the "on demand" half:
  read_skill(skill)                 -> the SKILL.md body
  run_skill_script(skill, script,   -> run skills/<skill>/<script>, feed it
                   stdin_text)          stdin_text, return stdout+stderr
  read_reference(skill, path)       -> a file under skills/<skill>/reference/

Security note: run_skill_script executes code that a SKILL.md points at. If an
attacker can write to skills/, that is remote code execution. Same trust
boundary as lab066 Exercise 3, made explicit here because we wrote the loader
ourselves. _safe(...) keeps paths inside the skill folder; it is the minimum,
not a sandbox.
"""

import subprocess
import sys
from pathlib import Path

from agents import function_tool

SKILLS_DIR = Path(__file__).parent / "skills"


# --------------------------------------------------------------------------
# Front-matter parsing and the startup index (progressive disclosure, level 1)
# --------------------------------------------------------------------------
def _front_matter(skill_md: Path) -> dict:
    """Read the name/description from a SKILL.md YAML front-matter block.

    Deliberately a 10-line parser, not PyYAML: the point is to show there is
    no magic, just 'read the top of the file'."""
    text = skill_md.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    if text.startswith("---"):
        _, fm, _body = text.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    meta.setdefault("name", skill_md.parent.name)
    meta.setdefault("description", "(no description)")
    return meta


def discover_skills() -> list[dict]:
    """Return [{name, description, dir}] for every skills/*/SKILL.md."""
    out = []
    if not SKILLS_DIR.is_dir():
        return out
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        meta = _front_matter(skill_md)
        out.append({"name": meta["name"], "description": meta["description"], "dir": skill_md.parent.name})
    return out


def build_instructions(base: str) -> str:
    """Append the skill index (names + descriptions only) to a base prompt.

    This is what makes it 'progressive disclosure': the model always sees the
    menu, and reads a full SKILL.md only when a task matches."""
    skills = discover_skills()
    if not skills:
        return base
    lines = [base, "", "## Available skills",
             "You have skills in the skills/ directory. You see only their name and "
             "description here. When a task matches one, call read_skill(<dir>) to load "
             "its full instructions, then follow them. Do not guess a skill's steps; read it.",
             ""]
    for s in skills:
        lines.append(f"- {s['dir']}: {s['description']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Path containment
# --------------------------------------------------------------------------
def _safe(skill: str, *parts: str) -> Path:
    """Resolve skills/<skill>/<parts...> and refuse to escape the skill dir."""
    base = (SKILLS_DIR / skill).resolve()
    target = (base.joinpath(*parts)).resolve()
    if base != target and base not in target.parents:
        raise ValueError(f"path escapes skill directory: {skill}/{'/'.join(parts)}")
    if not base.is_dir():
        raise ValueError(f"no such skill: {skill}")
    return target


# --------------------------------------------------------------------------
# The on-demand tools (progressive disclosure, levels 2 and 3)
# --------------------------------------------------------------------------
@function_tool
def read_skill(skill: str) -> str:
    """Return the full SKILL.md instructions for a skill directory (e.g.
    'http-header-audit'). Call this once a task matches the skill's
    description, before doing the work."""
    md = _safe(skill, "SKILL.md")
    if not md.is_file():
        return f"error: skills/{skill}/SKILL.md not found"
    return md.read_text(encoding="utf-8")


@function_tool
def read_reference(skill: str, path: str) -> str:
    """Read a reference file bundled with a skill, e.g.
    read_reference('http-header-audit', 'grading.md'). Reference files live
    under skills/<skill>/reference/ and hold detail the SKILL.md keeps out of
    the way until it is needed."""
    try:
        ref = _safe(skill, "reference", path)
    except ValueError as e:
        return f"error: {e}"
    if not ref.is_file():
        return f"error: reference {skill}/reference/{path} not found"
    return ref.read_text(encoding="utf-8")


@function_tool
def run_skill_script(skill: str, script: str, stdin_text: str = "") -> str:
    """Run a helper script bundled with a skill and return its output.

    Example: run_skill_script('http-header-audit', 'audit_headers.py',
    stdin_text=<json of the response headers>). The script is executed with
    the same Python interpreter; stdin_text is passed on stdin. Returns stdout,
    and stderr appended if the script failed."""
    try:
        path = _safe(skill, script)
    except ValueError as e:
        return f"error: {e}"
    if not path.is_file():
        return f"error: script {skill}/{script} not found"
    proc = subprocess.run(
        [sys.executable, str(path)],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = proc.stdout
    if proc.returncode != 0:
        out += f"\n[script exited {proc.returncode}]\n{proc.stderr}"
    return out.strip() or "(no output)"


# Convenience: the three skill tools as a list to hand to an Agent.
SKILL_TOOLS = [read_skill, read_reference, run_skill_script]
