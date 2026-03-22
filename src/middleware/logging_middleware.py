import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Handled request {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "duration_ms": round(process_time, 2),
                "status_code": response.status_code
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
