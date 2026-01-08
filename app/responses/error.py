from typing import Dict


def error_response(code: str, message: str) -> Dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
