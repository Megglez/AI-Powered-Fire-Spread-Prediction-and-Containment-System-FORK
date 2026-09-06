import os
import random
import uuid
from locust import HttpUser, task, between, events
from sqlalchemy import create_engine, text

TEST_USER_POOL_SIZE = 200
FIREFIGHTER_POOL_SIZE = 20
ADMIN_POOL_SIZE = 3

CAPE_TOWN_BOUNDS = {"lat": (-34.5, -33.5), "lng": (18.0, 19.5)}

def random_report_payload():
    return {
        "lat": round(random.uniform(*CAPE_TOWN_BOUNDS["lat"]), 6),
        "lng": round(random.uniform(*CAPE_TOWN_BOUNDS["lng"]), 6),
        "location_text": "Sector Test Area",
        "description": "Simulated wildfire report under load test",
        "image_url": None,
        "boundary_radius": round(random.uniform(0.5, 5.0), 2),
        "photo_hash": None,
    }

def random_location():
    return {
        "latitude": round(random.uniform(*CAPE_TOWN_BOUNDS["lat"]), 6),
        "longitude": round(random.uniform(*CAPE_TOWN_BOUNDS["lng"]), 6),
    }

@events.test_start.add_listener
def truncate_on_start(environment, **kwargs):
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE fire_reports CASCADE"))
    print("Truncated fire_reports before test run.")

def try_login(client, email, password):
    """Returns (success: bool, token, str|None)"""
    with client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        name="POST /api/auth/login",
        catch_response=True,
    ) as response:
        if response.status_code != 200:
            response.failure(f"Login failed with status: {response.status_code}")
            return False, None
        body = response.json()
        if body.get("requires_2fa"):
            response.failure("Account required 2FA - check seeding data")
            return False, None
        token = body.get("access_token")
        if not token:
            response.failure("Login succeedd but no access_token in response")
            return False, None
        return True, token

# Guests, possibly anonymous traffic, no login
# Possibly largest share of real users on public incident map
class GuestUser(HttpUser):
    weight = 5
    wait_time = between(0.5, 1.5)

    @task(4)
    def view_public_map_feed(self):
        with self.client.get(
            "/api/guests/reported-fires?limit=50",
            name="GET /api/guests/reported-fires",
            timeout=5.0,
            catch_response=True,
        ) as response:
            if response.status_code !=200:
                response.failure(f"Failed with status: {response.status_code}")

    @task(1)
    def submit_fire_report(self):
        with self.client.post(
            "/api/guests/reported-fires",
            json=random_report_payload(),
            name="POST /api/guests/reported-fires",
            timeout=5.0,
            catch_response=True
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Failed with status: {response.status_code}")

    @task(2)
    def guest_dashboard(self):
        loc = random_location()
        with self.client.get(
            "/api/guests/dashboard",
            params={"lat": loc["latitude"], "lng": loc["longitude"], "radius_km": 20},
            name="GET /api/gusets/dashboard",
            timeout=5.0,
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 500):
                response.failure(f"Failed with status: {response.status_code}")
            elif response.status_code == 500:
                response.failure("Dashboard returned 500 (documented possible failure mode)")

    @task(1)
    def guest_fire_report(self):
        with self.client.post(
            "/api/guests/nearby-fires",
            json=random_location(),
            name="POST /api/guests/nearby-fires",
            timeout=5.0,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status: {response.status_code}")

# Logged in, own reports, location updates, notifications
class RegisteredUser(HttpUser):
    weight = 4
    # wait time in seconds, btw users
    wait_time = between(0.5, 1.5)

    def on_start(self):
        idx = random.randint(0, TEST_USER_POOL_SIZE - 1)
        email = f"loadtest_user_{idx}@test.com"
        success, token = try_login(self.client, email, TEST_USER_PASSWORD)
        self.logged_in = success
        if success:
            self.client.headers.update({"Authorisation": f"Bearer {token}"})

    @task(3)
    def view_my_reports(self):
        if not self.logged_in:
            return
        with self.client.get(
            "/api/users/reported-fires",
            name="GET /api/users/reported-fires",
            timeout=5.0,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status: {response.status_code}")

    @task(1)
    def submit_authenticated_report(self):
        with self.client.post(
            "/api/users/reported-fires",
            json=random_report_payload(),
            name="POST /api/users/reported-fires",
            timeout=5.0,
            catch_response=True
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Failed with status: {response.status_code}")

    @task(2)
    def update_my_location(self):
        if not self.logged_in:
            return
        with self.client.patch(
            "/api/users/me/location",
            json=random_location(),
            name="PATCH /api/users/me/location",
            timeout=5.0,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status: {response.status_code}")