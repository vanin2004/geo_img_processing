from fastapi import Request
from fastapi.responses import JSONResponse


async def resource_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "Ресурс не найден"},
    )


async def resource_already_exists_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "Ресурс уже существует"},
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )
