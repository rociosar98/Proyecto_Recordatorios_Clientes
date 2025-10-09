import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

class ErrorHandler(BaseHTTPMiddleware):
    async def dispatch(selfs, request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": "Ocurrió un error inesperado"},
            )