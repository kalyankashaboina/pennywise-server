from typing import Any, Dict, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None,
) -> Dict:
    return {
        "success": True,
        "data": data,
        "message": message,
    }
