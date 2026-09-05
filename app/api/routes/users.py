from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.deps import PaginationDep, UserServiceDep
from app.schemas.common import ErrorResponse, Page
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

NOT_FOUND = {404: {"model": ErrorResponse}}
INVALID = {422: {"model": ErrorResponse}}


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={**INVALID},
)
async def create_user(payload: UserCreate, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(await service.create(payload))


@router.get("", response_model=Page[UserRead], responses={**INVALID})
async def list_users(
    service: UserServiceDep,
    pagination: PaginationDep,
    q: Annotated[
        str | None,
        Query(max_length=100, description="Name prefix; empty returns every user"),
    ] = None,
) -> Page[UserRead]:
    page = await service.search(q, limit=pagination.limit, offset=pagination.offset)
    return Page[UserRead](
        items=[UserRead.model_validate(user) for user in page.items],
        total=page.total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{user_id}", response_model=UserRead, responses={**NOT_FOUND, **INVALID})
async def get_user(user_id: UUID, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(await service.get(user_id))


@router.put("/{user_id}", response_model=UserRead, responses={**NOT_FOUND, **INVALID})
async def replace_user(user_id: UUID, payload: UserCreate, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(await service.replace(user_id, payload))


@router.patch("/{user_id}", response_model=UserRead, responses={**NOT_FOUND, **INVALID})
async def update_user(user_id: UUID, payload: UserUpdate, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(await service.update(user_id, payload))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**NOT_FOUND, **INVALID},
)
async def delete_user(user_id: UUID, service: UserServiceDep) -> Response:
    await service.delete(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
