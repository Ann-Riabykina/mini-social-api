from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.likes import router as likes_router
from app.api.posts import router as posts_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid request data",
            "errors": exc.errors(),
        },
    )


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(posts_router, prefix=settings.api_v1_prefix)
app.include_router(likes_router, prefix=settings.api_v1_prefix)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
    )

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses", {})

            if "422" in responses:
                responses.pop("422")

            if "400" not in responses:
                responses["400"] = {
                    "description": "Bad Request",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Invalid request data",
                                "errors": [
                                    {
                                        "loc": ["body", "email"],
                                        "msg": "value is not a valid email address",
                                        "type": "value_error",
                                    }
                                ],
                            }
                        }
                    },
                }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
