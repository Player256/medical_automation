import os
import requests
from sqlalchemy import create_engine, text

CALENDLY_TOKEN = os.getenv("CALENDLY_TOKEN")
BASE_URL = "https://api.calendly.com"

engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/medical_db")


class CalendlyService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CALENDLY_TOKEN}",
            "Content-Type": "application/json",
        }

    def get_current_user(self):
        """Fetch the authenticated Calendly user/org"""
        resp = requests.get(f"{BASE_URL}/users/me", headers=self.headers)
        resp.raise_for_status()
        return resp.json()["resource"]

    def create_event_type(self, owner, doctor_name, duration):
        payload = {
            "owner": owner,
            "name": f"{doctor_name} - {duration}min Consultation",
            "kind": "solo",
            "duration": duration,
            "visibility": "public",
            "locale": "en",
        }
        resp = requests.post(
            f"{BASE_URL}/event_types", headers=self.headers, json=payload
        )
        resp.raise_for_status()
        return resp.json()["resource"]

    def assign_calendly_url(self, doctor_id, scheduling_url,duration):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE doctors SET calendly_{duration}_url = :url WHERE doctor_id = :id"),
                {"url": scheduling_url, "id": doctor_id},
            )

    def sync_doctor(self, doctor_id, doctor_name):
        user = self.get_current_user()
        owner_uri = user["uri"]

        event_30 = self.create_event_type(owner_uri, doctor_name, 30)
        event_60 = self.create_event_type(owner_uri, doctor_name, 60)

        self.assign_calendly_url(doctor_id, event_30["scheduling_url"],30)
        self.assign_calendly_url(doctor_id, event_60["scheduling_url"],60)

        return {
            "30min": event_30["scheduling_url"],
            "60min": event_60["scheduling_url"],
        }

    def record_booking(self, appointment_id, event_uri):
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE appointments
                    SET status = 'scheduled', calendly_event_uri = :event
                    WHERE appointment_id = :id
                    """
                ),
                {"event": event_uri, "id": appointment_id},
            )
