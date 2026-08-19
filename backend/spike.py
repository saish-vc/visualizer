from pathlib import Path
import json
import sys

from app.services.trace_service import trace_cpp


if __name__ == "__main__":
    code = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else '#include <iostream>\nint main() {\n  int x = 2;\n  x += 3;\n  std::cout << x << "\\n";\n  return 0;\n}\n'
    print(json.dumps(trace_cpp(code).model_dump(), indent=2))
