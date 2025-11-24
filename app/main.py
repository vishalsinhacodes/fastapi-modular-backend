import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.errors import AppError
from app.schemas.common import ErrorResponse

from app.routers import auth, products, tasks

setup_logging()

logger = logging.getLogger("app")
access_logger = logging.getLogger("app.request")


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    try:
        response = await call_next(request)
    except Exception:
        process_time = (time.time() - start_time) * 1000
        access_logger.error(
            f"{method}{path} -> 500 in {process_time:.2f}ms"
        )
        raise
    
    process_time = (time.time() - start_time) * 1000
    access_logger.info(
        f"{method} {path} -> {response.status_code} in {process_time:.2f}ms"
    )
    return response   

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.error(
        f"AppError on {request.method} {request.url.path} "
        f"code={exc.code} message={exc.message}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.message, code=exc.code).model_dump(),
    )
    
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"HTTPException on {request.method} {request.url.path} "
        f"status={exc.status_code} detail={exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, code=None).model_dump(),
    )    
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation error on {request.method} {request.url.path} errors={exc.errors()}"
    )
    
    # You can customize this further later
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )    


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(tasks.router)