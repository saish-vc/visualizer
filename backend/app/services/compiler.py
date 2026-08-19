import subprocess
from functools import lru_cache
from pathlib import Path

BASE_FLAGS = ["-g", "-O0", "-fno-omit-frame-pointer", "-std=c++17"]
OPTIONAL_FLAGS = ["-ftrivial-auto-var-init=zero"]


@lru_cache(maxsize=None)
def _flag_supported(flag: str) -> bool:
    try:
        result = subprocess.run(
            ["g++", flag, "-fsyntax-only", "-x", "c++", "-"],
            input="int main() { return 0; }",
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def compile_flags() -> list[str]:
    return BASE_FLAGS + [flag for flag in OPTIONAL_FLAGS if _flag_supported(flag)]


def compile_cpp(source: Path, output: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["g++", *compile_flags(), str(source), "-o", str(output)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return result.returncode == 0, result.stderr
