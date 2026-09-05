from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.deps import get_readiness_checks
from app.schemas.common import HealthStatus, ReadinessStatus

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthStatus)
async def liveness() -> HealthStatus:
    return HealthStatus(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessStatus,
    responses={503: {"model": ReadinessStatus}},
)
async def readiness() -> ReadinessStatus | JSONResponse:
    results: dict[str, str] = {}
    for name, check in get_readiness_checks().items():
        try:
            await check()
        except Exception:
            results[name] = "fail"
        else:
            results[name] = "ok"

    if all(status == "ok" for status in results.values()):
        return ReadinessStatus(status="ready", checks=results)

    body = ReadinessStatus(status="not_ready", checks=results)
    return JSONResponse(status_code=503, content=body.model_dump(mode="json"))
