from pathlib import Path
import subprocess


def run_program(binary: Path, output: Path, timeout_seconds: float = 5.0) -> tuple[str, bool]:
    try:
        result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as error:
        output.write_text((error.stdout or ""), encoding="utf-8")
        return error.stdout or "", True
    stdout = result.stdout
    output.write_text(stdout, encoding="utf-8")
    return stdout, False

