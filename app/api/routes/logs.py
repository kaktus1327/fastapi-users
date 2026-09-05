from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import LogServiceDep, PaginationDep
from app.services.logs import LogFilters
from app.schemas.common import ErrorResponse, Page
from app.schemas.log import HTTPMethod, LogLineCreate, LogLineRead

router = APIRouter(prefix="/logs", tags=["logs"])

NOT_FOUND = {404: {"model": ErrorResponse}}
INVALID = {422: {"model": ErrorResponse}}


def get_log_filters(
    host: Annotated[str | None, Query(max_length=255)] = None,
    method: Annotated[HTTPMethod | None, Query()] = None,
    return_status: Annotated[str | None, Query(pattern=r"^[1-5]\d{2}$")] = None,
    since: Annotated[datetime | None, Query()] = None,
    until: Annotated[datetime | None, Query()] = None,
) -> LogFilters:
    return LogFilters(
        host=host,
        method=method.value if method else None,
        return_status=return_status,
        since=since,
        until=until,
    )


@router.post(
    "",
    response_model=LogLineRead,
    status_code=status.HTTP_201_CREATED,
    responses={**INVALID},
)
async def create_log(payload: LogLineCreate, service: LogServiceDep) -> LogLineRead:
    return LogLineRead.model_validate(await service.create(payload))


@router.get("", response_model=Page[LogLineRead], responses={**INVALID})
async def list_logs(
    service: LogServiceDep,
    pagination: PaginationDep,
    filters: Annotated[LogFilters, Depends(get_log_filters)],
) -> Page[LogLineRead]:
    page = await service.list(
        filters=filters, limit=pagination.limit, offset=pagination.offset
    )
    return Page[LogLineRead](
        items=[LogLineRead.model_validate(log) for log in page.items],
        total=page.total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{log_id}", response_model=LogLineRead, responses={**NOT_FOUND, **INVALID})
async def get_log(log_id: UUID, service: LogServiceDep) -> LogLineRead:
    return LogLineRead.model_validate(await service.get(log_id))
