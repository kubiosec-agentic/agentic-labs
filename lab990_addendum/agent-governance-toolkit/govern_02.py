"""
Exercise 2: AGT Supply Chain Guard.

Scans dependency manifests (requirements.txt, package.json,
pyproject.toml, Cargo.toml) for supply chain risks:

  - Missing version pins ("requests" without ==x.y.z)
  - Version ranges that allow untested upgrades
  - Typosquatting detection (fuzzy match against known packages)
  - Lockfile drift (lockfile disagrees with manifest)

No API keys needed. Pure static analysis.

Run:
    python3 govern_02.py
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from agent_compliance import SupplyChainGuard, SupplyChainConfig


def print_findings(label: str, findings: list) -> None:
    """Pretty-print supply chain findings."""
    print(f"\n  --- {label} ---")
    if not findings:
        print("  [+] No issues found.")
        return
    for f in findings:
        icon = "[!]" if f.severity in ("high", "critical") else "[~]"
        print(f"  {icon} {f.severity.upper():8s}  {f.package or f.finding_type}: "
              f"{f.message}")


def main() -> None:
    print("=" * 64)
    print("  AGT Supply Chain Guard")
    print("=" * 64)
    print()
    print("Scans dependency manifests for supply chain risks:")
    print("unpinned versions, version ranges, typosquatting, etc.")
    print()

    guard = SupplyChainGuard(SupplyChainConfig(
        allow_ranges=False,        # flag >= or ~= specifiers
        typosquat_threshold=0.85,  # fuzzy match sensitivity
    ))

    # --- Create sample requirements files ---
    with tempfile.TemporaryDirectory() as tmp:

        # 1. A risky requirements.txt
        risky = Path(tmp) / "risky_requirements.txt"
        risky.write_text(
            "# An agent's dependencies (intentionally bad)\n"
            "requests\n"
            "flask>=2.0\n"
            "openai~=1.30\n"
            "requets==2.31.0\n"   # typosquat
            "numpy==1.26.4\n"
            "pyjwt\n"
        )

        # 2. A properly pinned requirements.txt
        clean = Path(tmp) / "clean_requirements.txt"
        clean.write_text(
            "# Properly pinned dependencies\n"
            "requests==2.32.3\n"
            "flask==3.1.0\n"
            "openai==1.90.0\n"
            "numpy==1.26.4\n"
            "pyjwt==2.10.1\n"
        )

        print("  Scanning risky_requirements.txt ...")
        findings_risky = guard.check_requirements(str(risky))
        print_findings("risky_requirements.txt", findings_risky)

        print()
        print("  Scanning clean_requirements.txt ...")
        findings_clean = guard.check_requirements(str(clean))
        print_findings("clean_requirements.txt", findings_clean)

    # --- Also scan this lab's own requirements ---
    lab_req = Path(__file__).parent / "requirements.txt"
    if lab_req.exists():
        print()
        print("  Scanning this lab's requirements.txt ...")
        findings_lab = guard.check_requirements(str(lab_req))
        print_findings("lab requirements.txt", findings_lab)

    # --- Typosquatting check ---
    print()
    print("-" * 64)
    print("  Standalone typosquatting check")
    print("-" * 64)
    suspect_names = ["requets", "openaii", "numpy", "reqeusts", "tenserflow"]
    for pkg in suspect_names:
        finding = guard.check_typosquatting(pkg)
        if finding:
            print(f"  [!] '{pkg}': {finding.message}")
        else:
            print(f"  [+] '{pkg}': looks legitimate")

    print()
    print("Takeaway: run SupplyChainGuard in CI before pip install.")
    print("Catches unpinned deps, version ranges, and typosquats")
    print("before they reach your agent's runtime.")
    print()


if __name__ == "__main__":
    main()
