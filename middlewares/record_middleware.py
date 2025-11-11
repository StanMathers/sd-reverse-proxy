import time
from fastapi import Request, Response
from uuid import uuid4
from utils.logger import logger

SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "cookie"}

async def request_response_logger(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())

    # Perform performance monitoring when request comes in
    start = time.perf_counter()
    body = await request.body()
    safe_headers = {
        k: ("<redacted>" if k.lower() in SENSITIVE_HEADERS else v)
        for k, v in request.headers.items()
    }

    logger.info(
        f"Incoming request {request.method} {request.url.path}",
        extra={
            "extra_data": {
                "event": "inbound_request",
                "requestId": request_id,
                "method": request.method,
                "path": request.url.path,
                "body_size": len(body)
            }
        }
    )

    # Process
    response: Response = await call_next(request)
    latency_ms = int((time.perf_counter() - start) * 1000)

    # Outbound (after finishing the request)
    logger.info(
        f"Completed request {request.method} {request.url.path}",
        extra={
            "extra_data": {
                "event": "outbound_response",
                "requestId": request_id,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            }
        },
    )

    response.headers["x-request-id"] = request_id
    return response



