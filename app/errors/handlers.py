from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors.base import AppError
from app.errors.codes import ErrorCode
from app.responses.error import error_response

# Custom handler to show missing fields and other validation errors
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Extract the errors
    errors = exc.errors()

    # List to hold the missing fields and invalid fields
    missing_fields = []
    invalid_fields = []

    # Check each error to find missing fields or invalid ones
    for error in errors:
        if error["type"] == "value_error.missing":
            # This is a missing field error
            field = error["loc"][-1]  # Get the field name from the location
            missing_fields.append(field)
        else:
            # This is a validation error for an invalid field
            field = error["loc"][-1]  # Get the field name
            invalid_fields.append(f"{field}: {error['msg']}")

    # Construct the response message
    if missing_fields:
        message = f"Missing required fields: {', '.join(missing_fields)}"
    elif invalid_fields:
        message = f"Invalid fields: {', '.join(invalid_fields)}"
    else:
        message = "Invalid request data"

    # Return the response with the appropriate error message
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": message
            }
        }
    )

def register_exception_handlers(app: FastAPI) -> None:
    # -----------------------------
    # App-defined errors
    # -----------------------------
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.code, exc.message),
        )

    # -----------------------------
    # Request validation errors
    # -----------------------------
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # -----------------------------
    # HTTP errors
    # -----------------------------
    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            code = ErrorCode.NOT_FOUND
            message = "Resource not found"
        elif exc.status_code == 401:
            code = ErrorCode.UNAUTHORIZED
            message = "Unauthorized"
        elif exc.status_code == 403:
            code = ErrorCode.FORBIDDEN
            message = "Forbidden"
        else:
            code = ErrorCode.INTERNAL_ERROR
            message = "Request failed"

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(code, message),
        )

    # -----------------------------
    # Fallback (last-resort)
    # -----------------------------
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=error_response(
                ErrorCode.INTERNAL_ERROR,
                "Something went wrong",
            ),
        )
