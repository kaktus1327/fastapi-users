import random
import uuid
from datetime import UTC, datetime

from locust import HttpUser, between, task

HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
RETURN_STATUSES = ["200", "201", "204", "404", "409", "422", "500"]
HOSTS = ["web-1", "web-2", "web-3"]


def random_name() -> str:
    return f"locust-{uuid.uuid4().hex[:12]}"


class UserCrudTask:
    """Full lifecycle on /users: create -> get -> update -> delete."""

    def __init__(self, client):
        self.client = client

    def run(self):
        payload = {"name": random_name(), "age": random.randint(0, 99)}
        response = self.client.post("/users", json=payload, name="/users [create]")
        if response.status_code != 201:
            return
        user_id = response.json()["id"]

        self.client.get(f"/users/{user_id}", name="/users/[id] [get]")
        self.client.get("/users", params={"limit": 10}, name="/users [list]")
        self.client.get("/users", params={"q": payload["name"][:8]}, name="/users [search]")

        self.client.patch(
            f"/users/{user_id}",
            json={"age": random.randint(0, 99)},
            name="/users/[id] [patch]",
        )

        self.client.delete(f"/users/{user_id}", name="/users/[id] [delete]")


class LogTask:
    """Create a log line, then list and fetch it."""

    def __init__(self, client):
        self.client = client

    def run(self):
        payload = {
            "host": random.choice(HOSTS),
            "timestamp": datetime.now(UTC).isoformat(),
            "method": random.choice(HTTP_METHODS),
            "return_status": random.choice(RETURN_STATUSES),
            "message": "locust load test",
        }
        response = self.client.post("/logs", json=payload, name="/logs [create]")
        if response.status_code != 201:
            return
        log_id = response.json()["id"]

        self.client.get(f"/logs/{log_id}", name="/logs/[id] [get]")
        self.client.get(
            "/logs",
            params={"host": payload["host"], "limit": 10},
            name="/logs [list]",
        )


class AppUser(HttpUser):
    wait_time = between(1, 3)

    @task(7)
    def users_crud(self):
        UserCrudTask(self.client).run()

    @task(3)
    def logs_flow(self):
        LogTask(self.client).run()
