from uuid import UUID

from cassandra.cluster import Session

from app.domain.models import User
from app.repositories.cass.common import get_cluster_session
from app.repositories.interface_users import UserRepository
from loguru import logger


class CassandraUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def upsert_user(self, user: User) -> None:
        query = """
                INSERT INTO app.users (id, name, age)
                VALUES (%s, %s, %s) \
                """
        self.session.execute(query, (user.id, user.name, user.age))

    def get_user(self, user_id: UUID) -> User | None:
        query = """
                SELECT id, name, age
                FROM app.users
                WHERE id = %s \
                """
        row = self.session.execute(query, (user_id,)).one()
        if row is None:
            return None
        return User(id=row.id, name=row.name, age=row.age)

    def get_users_by_name_prefix(self, name_prefix: str) -> list[User]:
        query = """
                SELECT id, name, age
                FROM app.users
                WHERE name LIKE %s \
                """
        rows = self.session.execute(query, (f"{name_prefix}%",))
        return [User(id=row.id, name=row.name, age=row.age) for row in rows]

    def delete_user(self, user_id: UUID) -> None:
        query = """
                DELETE \
                FROM app.users
                WHERE id = %s \
                """
        self.session.execute(query, (user_id,))



if __name__ == '__main__':
    cluster, session = get_cluster_session()
    logger.info("Connected to Cassandra")

    repo = CassandraUserRepository(session)

    user = User(id=UUID("123e4567-e89b-12d3-a456-426655440000"), name="John Doe", age=30)
    repo.upsert_user(user)

    cluster.shutdown()
    logger.info("Disconnected from Cassandra")
