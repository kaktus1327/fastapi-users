from dataclasses import dataclass
from uuid import UUID

from starlette.concurrency import run_in_threadpool

from app.core.errors import NotFoundError
from app.core.text import fold
from app.domain.models import User, apply_changes, new_user_id
from app.ports.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

READINESS_PROBE_ID = UUID("00000000-0000-0000-0000-000000000000")


@dataclass(frozen=True, slots=True)
class UserPage:
    items: list[User]
    total: int


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def create(self, payload: UserCreate) -> User:
        user = User(name=payload.name, age=payload.age, id=new_user_id())
        await run_in_threadpool(self._repository.upsert_user, user)
        return user

    async def get(self, user_id: UUID) -> User:
        user = await run_in_threadpool(self._repository.get_user, user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def search(self, name_prefix: str | None, limit: int, offset: int) -> UserPage:
        prefix = (name_prefix or "").strip()
        users = await run_in_threadpool(self._repository.get_users_by_name_prefix, prefix)
        ordered = sorted(users, key=lambda user: (fold(user.name), user.name))
        return UserPage(items=ordered[offset : offset + limit], total=len(ordered))

    async def replace(self, user_id: UUID, payload: UserCreate) -> User:
        current = await self.get(user_id)
        updated = apply_changes(current, name=payload.name, age=payload.age)
        await run_in_threadpool(self._repository.upsert_user, updated)
        return updated

    async def update(self, user_id: UUID, payload: UserUpdate) -> User:
        current = await self.get(user_id)
        changes = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not changes:
            return current
        updated = apply_changes(current, **changes)
        await run_in_threadpool(self._repository.upsert_user, updated)
        return updated

    async def delete(self, user_id: UUID) -> None:
        await self.get(user_id)
        await run_in_threadpool(self._repository.delete_user, user_id)

    async def ping(self) -> None:
        await run_in_threadpool(self._repository.get_user, READINESS_PROBE_ID)
