from typing import Any, Dict


def error_response(code: str, message: str) -> Dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
