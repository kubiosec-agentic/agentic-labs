"""
A minimal Docker sandbox backend for Deep Agents.

deepagents ships BaseSandbox: implement execute(), upload_files(),
download_files() and id, and the harness derives ls/read/write/edit/glob/grep
from those primitives (they run as shell commands inside the sandbox). The
agent's `execute` tool then lands here.

This is a teaching implementation. It starts one throwaway container per
backend instance and runs every command with `docker exec`. Hardening choices
are explicit and commented so you can weaken them one by one in Exercise 5
and watch what the agent can reach.
"""

from __future__ import annotations

import base64
import shlex
import subprocess
import uuid

from deepagents.backends.sandbox import BaseSandbox
from deepagents.backends.protocol import ExecuteResponse, FileDownloadResponse, FileUploadResponse

MAX_OUTPUT = 100_000


class DockerSandbox(BaseSandbox):
    """One container per instance; commands run via `docker exec`."""

    # Large `execute` output is captured to a file in the sandbox and only a
    # preview returned (context offloading, Exercise 7). Needs sh + coreutils,
    # which python:3.12-slim has.
    enable_capture_offload = True

    def __init__(
        self,
        image: str = "python:3.12-slim",
        *,
        network: str = "none",       # no egress at all; set "bridge" to allow it
        memory: str = "512m",
        cpus: str = "1",
        pids_limit: int = 256,
        read_only_root: bool = True,  # only /work (tmpfs) is writable
        timeout: int = 60,
        workdir: str = "/work",
    ) -> None:
        self._id = f"da-sandbox-{uuid.uuid4().hex[:8]}"
        self._timeout = timeout
        self._workdir = workdir
        cmd = [
            "docker", "run", "-d", "--rm",
            "--name", self._id,
            "--network", network,
            "--memory", memory,
            "--cpus", cpus,
            "--pids-limit", str(pids_limit),
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--user", "65534:65534",              # nobody
            "--tmpfs", f"{workdir}:rw,exec,size=64m,uid=65534,gid=65534",
            "--tmpfs", "/tmp:rw,size=16m,uid=65534,gid=65534",
            # FilesystemMiddleware captures large `execute` output to
            # /large_tool_results/<call_id> INSIDE the sandbox. With a
            # read-only root that directory must exist and be writable.
            "--tmpfs", "/large_tool_results:rw,size=64m,uid=65534,gid=65534",
            "-w", workdir,
        ]
        if read_only_root:
            cmd.append("--read-only")
        cmd += [image, "sleep", "infinity"]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    # --- SandboxBackendProtocol -------------------------------------------

    @property
    def id(self) -> str:
        return self._id

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        try:
            proc = subprocess.run(
                ["docker", "exec", "-w", self._workdir, self._id, "sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout or self._timeout,
            )
        except subprocess.TimeoutExpired:
            return ExecuteResponse(output=f"[timeout after {timeout or self._timeout}s]", exit_code=None)
        out = proc.stdout + proc.stderr
        truncated = len(out) > MAX_OUTPUT
        return ExecuteResponse(output=out[:MAX_OUTPUT], exit_code=proc.returncode, truncated=truncated)

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        results = []
        for path, content in files:
            q = shlex.quote(path)
            # Stream the bytes over stdin so large files do not hit ARG_MAX.
            proc = subprocess.run(
                ["docker", "exec", "-i", "-w", self._workdir, self._id, "sh", "-c", f"mkdir -p $(dirname {q}) && cat > {q}"],
                input=content,
                capture_output=True,
                timeout=self._timeout,
            )
            err = None if proc.returncode == 0 else (proc.stderr.decode(errors="replace").strip() or "upload_failed")
            results.append(FileUploadResponse(path=path, error=err))
        return results

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        results = []
        for path in paths:
            r = self.execute(f"base64 < {shlex.quote(path)}")
            if r.exit_code != 0:
                results.append(FileDownloadResponse(path=path, content=None, error="file_not_found"))
            else:
                results.append(FileDownloadResponse(path=path, content=base64.b64decode(r.output)))
        return results

    # --- housekeeping -------------------------------------------------------

    def close(self) -> None:
        subprocess.run(["docker", "rm", "-f", self._id], capture_output=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
