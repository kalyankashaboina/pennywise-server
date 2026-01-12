from typing import Any, Dict, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "message": message,
    }
