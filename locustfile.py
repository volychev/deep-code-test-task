import uuid

from locust import HttpUser, between, task

API_PREFIX = "/api"
API_VERSION = "v1"
API_ROOT = f"{API_PREFIX}/{API_VERSION}"


class TelemetryApiUser(HttpUser):
    wait_time = between(0.5, 3.0)

    def on_start(self):
        self.user_id = self._create_user()
        self.device_id = self._create_device(self.user_id)
        self._add_measurement(self.device_id)

    def _create_user(self) -> int:
        unique_suffix = uuid.uuid4().hex[:8]
        payload = {
            "username": f"user-{unique_suffix}",
            "email": f"{unique_suffix}@example.com",
        }

        with self.client.post(
            f"{API_ROOT}/users/",
            json=payload,
            name=f"POST {API_ROOT}/users/",
            catch_response=True
        ) as response:
            if response.status_code != 201:
                response.failure(f"Unexpected status: {response.status_code}, body={response.text}")
                return -1

            data = response.json()
            return int(data["id"])

    def _create_device(self, user_id: int) -> int:
        payload = {
            "name": f"device-{uuid.uuid4().hex[:6]}",
            "user_id": user_id,
        }

        with self.client.post(
            f"{API_ROOT}/devices/",
            json=payload,
            name=f"POST {API_ROOT}/devices/",
            catch_response=True
        ) as response:
            if response.status_code != 201:
                response.failure(f"Unexpected status: {response.status_code}, body={response.text}")
                return -1

            data = response.json()
            return int(data["id"])

    def _add_measurement(self, device_id: int):
        payload = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
        }

        with self.client.post(
            f"{API_ROOT}/analytics/{device_id}/data",
            json=payload,
            name=f"POST {API_ROOT}/analytics/{device_id}/data",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Unexpected status: {response.status_code}, body={response.text}")

    @task(5)
    def add_measurement(self):
        self._add_measurement(self.device_id)

    @task(3)
    def get_device_analytics(self):
        params = {
            "device_id": self.device_id,
            "limit": 25,
            "offset": 0,
        }

        with self.client.get(
            f"{API_ROOT}/analytics/",
            params=params,
            name=f"GET {API_ROOT}/analytics/?device_id",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}, body={response.text}")
                return

            payload = response.json()
            if "data" not in payload:
                response.failure("Response without data field")

    @task(2)
    def get_users(self):
        with self.client.get(
            f"{API_ROOT}/users/",
            params={"limit": 10, "offset": 0},
            name=f"GET {API_ROOT}/users/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}, body={response.text}")

    @task(2)
    def get_devices(self):
        with self.client.get(
            f"{API_ROOT}/devices/",
            params={"limit": 10, "offset": 0},
            name=f"GET {API_ROOT}/devices/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}, body={response.text}")
