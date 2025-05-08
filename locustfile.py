import uuid
import time
from locust import HttpUser, SequentialTaskSet, task, between
import logging

logger = logging.getLogger(__name__)


class UserBehavior(SequentialTaskSet):
    def on_start(self):
        time.sleep(0.5)

        self.email = f"user_{uuid.uuid4().hex}@example.com"
        self.password = "Password123!"
        self.name = "locust_user"

        try:
            r = self.client.post(
                "/api/v1/auth/register/",
                json={
                    "email": self.email,
                    "password": self.password,
                    "name": self.name,
                },
            )
            if r.status_code != 200:
                logger.error(f"Register failed: {r.status_code} {r.text}")
                return
        except Exception as e:
            logger.error(f"Register exception: {str(e)}")
            return

        try:
            r = self.client.post(
                "/api/v1/auth/login/",
                json={"email": self.email, "password": self.password},
            )
            if r.status_code != 200:
                logger.error(f"Login failed: {r.status_code} {r.text}")
                return
        except Exception as e:
            logger.error(f"Login exception: {str(e)}")
            return

        try:
            data = r.json()
            if "ok" in data and data["ok"] and "detail" in data:
                if "auth_token" in data["detail"]:
                    token = data["detail"]["auth_token"]
                else:
                    logger.error(f"No auth_token in login detail: {data}")
                    return
            else:
                token = data.get("auth_token")
                if not token:
                    logger.error(f"No auth_token in login response: {data}")
                    return

            self.client.headers.update({"Authorization": f"Bearer {token}"})
            self.logged_in = True
        except Exception as e:
            logger.error(f"Token extraction exception: {str(e)}")
            return

    @task
    def check_status(self):
        if not hasattr(self, "logged_in") or not self.logged_in:
            return
        try:
            self.client.get("/api/v1/status/")
        except Exception as e:
            logger.error(f"Status check exception: {str(e)}")

    @task
    def check_secured(self):
        if not hasattr(self, "logged_in") or not self.logged_in:
            return
        try:
            self.client.get("/api/v1/status/secured_status/")
        except Exception as e:
            logger.error(f"Secured status exception: {str(e)}")

    @task
    def notes_crud(self):
        if not hasattr(self, "logged_in") or not self.logged_in:
            return
        try:
            r = self.client.post(
                "/api/v1/notes/",
                json={"title": "Locust Test", "content": "Performance testing content"},
            )
            if r.status_code != 201:
                logger.error(f"Note creation failed: {r.status_code} {r.text}")
                return

            try:
                note = r.json()
                if isinstance(note, dict):
                    note_id = note.get("id") or note.get("note_id")
                    if not note_id and "detail" in note:
                        detail = note["detail"]
                        if isinstance(detail, dict):
                            note_id = detail.get("id") or detail.get("note_id")
                else:
                    note_id = note

                if not note_id:
                    logger.error(f"Could not extract note_id from response: {note}")
                    return
            except Exception as e:
                logger.error(f"Note ID extraction exception: {str(e)}")
                return

            r = self.client.get(f"/api/v1/notes/{note_id}")
            if r.status_code != 200:
                logger.error(f"Note retrieval failed: {r.status_code} {r.text}")

            r = self.client.patch(
                f"/api/v1/notes/{note_id}",
                json={"title": "Updated Title", "content": "Updated content"},
            )
            if r.status_code != 200:
                logger.error(f"Note update failed: {r.status_code} {r.text}")

            r = self.client.delete(f"/api/v1/notes/{note_id}")
            if r.status_code != 204 and r.status_code != 200:
                logger.error(f"Note deletion failed: {r.status_code} {r.text}")

        except Exception as e:
            logger.error(f"Notes CRUD exception: {str(e)}")

    @task
    def translation_flow(self):
        if not hasattr(self, "logged_in") or not self.logged_in:
            return
        try:
            r = self.client.post(
                "/api/v1/translation/detection", params={"text": "Hello world"}
            )
            if r.status_code != 200:
                logger.error(f"Language detection failed: {r.status_code} {r.text}")

            r = self.client.post(
                "/api/v1/translation/",
                json={"text": "Hello world", "source": "en", "target": "es"},
            )
            if r.status_code != 200:
                logger.error(f"Translation failed: {r.status_code} {r.text}")

            r = self.client.get("/api/v1/translation/languages")
            if r.status_code != 200:
                logger.error(f"Language list failed: {r.status_code} {r.text}")

        except Exception as e:
            logger.error(f"Translation flow exception: {str(e)}")


class NotesUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(3, 5)
