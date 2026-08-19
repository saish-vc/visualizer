import subprocess
from pathlib import Path


def compile_cpp(source: Path, output: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["g++", "-g", "-O0", "-fno-omit-frame-pointer", "-ftrivial-auto-var-init=zero", "-std=c++17", str(source), "-o", str(output)],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.returncode == 0, result.stderr

