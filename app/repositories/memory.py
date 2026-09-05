import threading
from uuid import UUID

from app.core.text import fold
from app.domain.models import User
from app.ports.user_repository import UserRepository


def _key(user_id: UUID | str) -> UUID:
    return user_id if isinstance(user_id, UUID) else UUID(str(user_id))


class MemoryUserRepository(UserRepository):
    def __init__(self, users: list[User] | None = None) -> None:
        self._users: dict[UUID, User] = {}
        self._lock = threading.Lock()
        for user in users or []:
            self.upsert_user(user)

    def upsert_user(self, user: User):
        with self._lock:
            self._users[_key(user.id)] = user

    def get_user(self, user_id: UUID) -> User | None:
        with self._lock:
            return self._users.get(_key(user_id))

    def get_users_by_name_prefix(self, name_prefix: str) -> list[User]:
        prefix = fold(name_prefix or "")
        with self._lock:
            users = list(self._users.values())
        if prefix:
            users = [user for user in users if fold(user.name).startswith(prefix)]
        return sorted(users, key=lambda user: (fold(user.name), user.name))

    def delete_user(self, user_id: UUID):
        with self._lock:
            self._users.pop(_key(user_id), None)

    def clear(self) -> None:
        with self._lock:
            self._users.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._users)
