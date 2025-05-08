import uuid
from locust import HttpUser, SequentialTaskSet, task, between


class UserBehavior(SequentialTaskSet):
    def on_start(self):
        self.email = f"user_{uuid.uuid4().hex}@example.com"
        self.password = "Password123!"
        self.name = "locust_user"
        r = self.client.post(
            "/api/v1/auth/register/",
            json={"email": self.email, "password": self.password, "name": self.name},
        )
        if r.status_code != 200:
            raise RuntimeError(f"Register failed: {r.status_code} {r.text}")

        r = self.client.post(
            "/api/v1/auth/login/",
            json={"email": self.email, "password": self.password},
        )
        if r.status_code != 200:
            raise RuntimeError(f"Login failed: {r.status_code} {r.text}")

        data = r.json()
        token = data.get("auth_token")
        if not token:
            raise KeyError(f"No auth_token in login response: {data}")

        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task
    def check_status(self):
        self.client.get("/api/v1/status/")

    @task
    def check_secured(self):
        self.client.get("/api/v1/status/secured_status/")

    @task
    def notes_crud(self):
        r = self.client.post(
            "/api/v1/notes/",
            json={"title": "Locust Test", "content": "Performance testing content"},
        )
        if r.status_code != 201:
            return
        note = r.json()
        note_id = note.get("id") or note.get("note_id") or note

        self.client.get(f"/api/v1/notes/{note_id}")

        self.client.patch(
            f"/api/v1/notes/{note_id}",
            json={"title": "Updated Title", "content": "Updated content"},
        )

        self.client.delete(f"/api/v1/notes/{note_id}")

    @task
    def translation_flow(self):
        self.client.post(
            "/api/v1/translation/detection", params={"text": "Hello world"}
        )

        self.client.post(
            "/api/v1/translation/",
            json={"text": "Hello world", "source": "en", "target": "es"},
        )

        self.client.get("/api/v1/translation/languages")


class NotesUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
