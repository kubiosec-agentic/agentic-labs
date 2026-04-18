"""
Exercise 3: File integrity verification for governance code.

Demonstrates the concept behind AGT's IntegrityVerifier:
generate SHA-256 hashes of your governance files in a trusted
build step, then verify them at agent startup to detect tampering.

AGT's IntegrityVerifier (v3.1.0) is scoped to its own internal
governance modules. This exercise implements the same pattern for
your own code, which is how you would use it in practice for any
agent project.

No API keys needed.

Run:
    python3 govern_03.py
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def hash_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def generate_manifest(directory: Path, pattern: str = "*.py") -> dict:
    """Generate a hash manifest for all matching files."""
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "directory": str(directory),
        "files": {},
    }
    for f in sorted(directory.glob(pattern)):
        manifest["files"][f.name] = hash_file(f)
    return manifest


def verify_manifest(directory: Path, manifest: dict) -> list[dict]:
    """Verify files against a manifest. Returns list of violations."""
    violations = []
    for filename, expected_hash in manifest["files"].items():
        filepath = directory / filename
        if not filepath.exists():
            violations.append({
                "file": filename,
                "status": "MISSING",
                "expected": expected_hash[:16] + "...",
            })
            continue
        actual_hash = hash_file(filepath)
        if actual_hash != expected_hash:
            violations.append({
                "file": filename,
                "status": "TAMPERED",
                "expected": expected_hash[:16] + "...",
                "actual": actual_hash[:16] + "...",
            })
    return violations


def main() -> None:
    print("=" * 64)
    print("  Governance Code Integrity Verification")
    print("=" * 64)
    print()
    print("Same pattern as AGT's IntegrityVerifier: hash files in a")
    print("trusted build, verify at startup to detect tampering.")
    print()

    lab_dir = Path(__file__).resolve().parent
    manifest_path = Path(tempfile.mktemp(suffix=".json"))

    # --- Step 1: generate manifest from current code ---
    print("  [1] Generating manifest from trusted code ...")
    manifest = generate_manifest(lab_dir, "govern_*.py")
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"      Files hashed: {len(manifest['files'])}")
    for name, h in manifest["files"].items():
        print(f"        {name}: {h[:24]}...")
    print()

    # --- Step 2: verify (should pass) ---
    print("  [2] Verifying integrity (nothing changed) ...")
    violations = verify_manifest(lab_dir, manifest)
    if violations:
        for v in violations:
            print(f"      [!] {v['status']}: {v['file']}")
    else:
        print("      [+] PASS: all files match manifest")
    print()

    # --- Step 3: simulate tampering ---
    print("  [3] Simulating tampering ...")
    first_file = next(iter(manifest["files"]))
    original_hash = manifest["files"][first_file]
    manifest["files"][first_file] = "deadbeef" + original_hash[8:]
    print(f"      Modified manifest hash for: {first_file}")
    print()

    # --- Step 4: re-verify ---
    print("  [4] Re-verifying after tampering ...")
    violations = verify_manifest(lab_dir, manifest)
    if violations:
        for v in violations:
            print(f"      [!] {v['status']}: {v['file']}")
            if v["status"] == "TAMPERED":
                print(f"          Expected: {v['expected']}")
                print(f"          Actual:   {v['actual']}")
    else:
        print("      [+] PASS (unexpected)")
    print()

    # --- Step 5: show AGT's built-in verifier (limited scope) ---
    print("-" * 64)
    print("  Note on AGT's IntegrityVerifier")
    print("-" * 64)
    print()
    print("  AGT v3.1.0 includes IntegrityVerifier, but it is scoped")
    print("  to AGT's own internal governance modules (agentmesh.*,")
    print("  agent_os.*, etc.). For your own agent code, implement")
    print("  the same SHA-256 manifest pattern as shown above.")
    print()
    print("  In production:")
    print("    1. CI generates the manifest during a trusted build")
    print("    2. Manifest is signed and stored alongside the deployment")
    print("    3. Agent startup calls verify_manifest()")
    print("    4. If any file is TAMPERED or MISSING, agent refuses to start")
    print()

    # Cleanup
    manifest_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
