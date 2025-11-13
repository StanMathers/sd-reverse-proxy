import logging
import uuid
from fastapi import FastAPI, Request
from schemas.request import ExecuteRequestSchema
from providers.openliga import OpenLigaProvider
from decision_mapper import DecisionMapper
from settings import get_settings
from middlewares.record_middleware import request_response_logger
from utils.logger import logger


app = FastAPI()
app.middleware("http")(request_response_logger)

PROVIDER = OpenLigaProvider(cfg=get_settings())
MAPPER = DecisionMapper(provider=PROVIDER)


@app.post("/proxy/execute")
async def execute_proxy_request(request: Request, payload: ExecuteRequestSchema):
    data = await MAPPER.execute(request, op=payload.operationType, payload=payload.payload)
    logger.info(
        f"Executed operation: {payload.operationType} with payload: {payload.payload}"
    )

    return {
        "status": "success",
        "data": {
            "operationType": payload.operationType,
            "requestId": request.state.request_id,
            "result": data,
        },
    }
