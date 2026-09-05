from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models import User


class UserRepository(ABC):
    @abstractmethod
    def upsert_user(self, user: User):
        pass

    @abstractmethod
    def get_user(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    def get_users_by_name_prefix(self, name_prefix: str) -> list[User]:
        pass

    @abstractmethod
    def delete_user(self, user_id: UUID):
        pass
