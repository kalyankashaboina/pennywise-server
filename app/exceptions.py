from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )


class ForbiddenException(HTTPException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )
