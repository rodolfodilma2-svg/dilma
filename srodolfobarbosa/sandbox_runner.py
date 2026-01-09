import sys
import json
import resource
import traceback
from pathlib import Path

# Limits
CPU_SECONDS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
MEM_BYTES = int(sys.argv[3]) if len(sys.argv) > 3 else 100 * 1024 * 1024  # 100MB

code_path = Path(sys.argv[1])
if not code_path.exists():
    print(json.dumps({"error": "file_not_found"}))
    sys.exit(2)

# Apply resource limits
try:
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (MEM_BYTES, MEM_BYTES))
except Exception:
    pass

# Minimal safe builtins
safe_builtins = {
    "print": print,
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "enumerate": enumerate,
}

ns = {"__builtins__": safe_builtins}

try:
    code = code_path.read_text(encoding="utf-8")
    # Execute code
    exec(code, ns, ns)
    out = ns.get("resultado", None)
    print(json.dumps({"status": "ok", "resultado": str(out)}))
except SystemExit as e:
    print(json.dumps({"status": "error", "detail": f"system exit {e}"}))
    sys.exit(1)
except Exception as e:
    tb = traceback.format_exc()
    print(json.dumps({"status": "error", "detail": str(e), "trace": tb}))
    sys.exit(1)
