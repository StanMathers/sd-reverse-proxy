from typing import Any, Dict, List, Optional
from pydantic import ValidationError

def get_structured_error(exc: ValidationError, operation: Optional[str] = None) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    for err in exc.errors():
        path = ".".join(str(p) for p in err.get("loc", []))
        issue = {
            "path": path or None,
            "message": err.get("msg"),
            "type": err.get("type"),
        }
        if "input" in err:  # pydantic v2
            issue["input"] = err.get("input")
        issues.append(issue)

    return {
        "status": "error",
        "error": {
            "code": "VALIDATION_ERROR",
            "operation": operation,
            "message": "Invalid request payload.",
            "issues": issues,
        },
    }
