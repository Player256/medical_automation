# tools.py
from typing import Dict, Any
from sqlalchemy import text
from langchain_core.tools import tool
from pydantic import BaseModel
from .db_connection import get_db
import re
import html
import uuid


class PatientInfo(BaseModel):
    first_name: str
    last_name: str
    dob: str  # YYYY-MM-DD
    email: str


@tool
def fetch_patient_record(patient_info: PatientInfo) -> Dict[str, Any]:
    """Fetch a patient record by first_name, last_name, dob (YYYY-MM-DD), and email."""
    try:
        db = next(get_db())
        query = text(
            """
            SELECT patient_id, first_name, last_name, dob, email, phone, patient_type
            FROM patients
            WHERE first_name = :first_name
              AND last_name = :last_name
              AND dob = :dob
              AND email = :email
            LIMIT 1
        """
        )
        row = db.execute(
            query,
            {
                "first_name": patient_info.first_name,
                "last_name": patient_info.last_name,
                "dob": patient_info.dob,
                "email": patient_info.email,
            },
        ).fetchone()
        if row:
            return {
                "exists": True,
                "patient": {
                    "patient_id": row.patient_id,
                    "first_name": row.first_name,
                    "last_name": row.last_name,
                    "dob": str(row.dob),
                    "email": row.email,
                    "phone": row.phone,
                    "patient_type": row.patient_type,
                },
                "message": "Patient record found.",
            }
        return {"exists": False, "message": "No matching patient record found."}
    except Exception as e:
        return {"error": f"Error fetching patient record: {str(e)}"}


@tool
def insert_patient_record(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new patient record (first_name, last_name, dob, email, phone) as patient_type='new'."""
    try:
        db = next(get_db())
        result = db.execute(
            text(
                """
            INSERT INTO patients (first_name, last_name, dob, email, phone, patient_type)
            VALUES (:first_name, :last_name, :dob, :email, :phone, 'new')
            RETURNING patient_id
        """
            ),
            {
                "first_name": patient_data.get("first_name"),
                "last_name": patient_data.get("last_name"),
                "dob": patient_data.get("dob"),
                "email": patient_data.get("email"),
                "phone": patient_data.get("phone"),
            },
        )
        db.commit()
        new_id = result.fetchone()
        return {"inserted": True, "patient_id": new_id}
    except Exception as e:
        return {"error": f"Error inserting patient record: {str(e)}"}


@tool
def fetch_doctors_by_specialty(specialty: str) -> Dict[str, Any]:
    """Fetch doctors by specialty with Calendly URLs."""
    try:
        db = next(get_db())
        rows = db.execute(
            text(
                """
            SELECT first_name, last_name, specialty, calendly_30_url, calendly_60_url
            FROM doctors
            WHERE specialty ILIKE :specialty
            ORDER BY last_name ASC
        """
            ),
            {"specialty": f"%{specialty}%"},
        ).fetchall()
        doctors = [
            {
                "name": f"{r.first_name} {r.last_name}",
                "specialty": r.specialty,
                "calendly_30_url": getattr(r, "calendly_30_url", None),
                "calendly_60_url": getattr(r, "calendly_60_url", None),
            }
            for r in rows
        ]
        return {"doctors": doctors}
    except Exception as e:
        return {"error": f"Error fetching doctors: {str(e)}"}


CALENDLY_SCRIPT_TAG = '<script src="https://assets.calendly.com/assets/external/widget.js" async></script>'

# @tool
# def build_calendly_embed(payload: dict) -> dict:
#     """
#     Input: {"patient": {...}, "doctors": [ { "name":..., "specialty":..., "calendly_30_url":..., "calendly_60_url":... } ]}
#     Output: {"patient": {...}, "doctors": [ { ... , "embed_html": "<a ...>Schedule</a>" } ] }
#     Rules:
#      - Use patient.patient_type to pick 60 (new) vs 30 (returning).
#      - Validate that the chosen URL contains 'calendly' (very conservative).
#      - Do NOT fabricate urls or doctor data.
#     """
#     try:
#         patient = payload.get("patient", {}) or {}
#         patient_type = (patient.get("patient_type") or "new").lower()
#         duration_key = "60" if patient_type == "new" else "30"

#         doctors_in = payload.get("doctors", []) or []
#         doctors_out = []

#         for doc in doctors_in:
#             # safe copy of existing fields
#             out = dict(doc)
#             url = doc.get(f"calendly_{duration_key}_url") or doc.get(f"calendly_{duration_key}")
#             if not url:
#                 out["embed_html"] = None
#                 out["error"] = "missing_calendly_url_for_duration"
#                 doctors_out.append(out)
#                 continue

#             # very conservative validation: require substring 'calendly'
#             if "calendly" not in url.lower():
#                 out["embed_html"] = None
#                 out["error"] = "invalid_calendly_url"
#                 doctors_out.append(out)
#                 continue

#             # ensure URL is HTML-escaped when injected into attribute
#             safe_url = html.escape(url, quote=True)
#             # generate a unique id so multiple widgets/buttons won't clash
#             uid = uuid.uuid4().hex[:8]

#             # Build a single "Schedule" button which opens Calendly popup using their JS API.
#             # This approach uses Calendly.initPopupWidget({url: '...'}) and doesn't inject inline <div> widgets.
#             embed = (
#                 f'{CALENDLY_SCRIPT_TAG}\n'
#                 f'<a href="#" '
#                 f'class="calendly-schedule-button" '
#                 f'onclick="Calendly.initPopupWidget({{url: \'{safe_url}\'}}); return false;" '
#                 f'data-doctor-id="{html.escape(str(doc.get("doctor_id", "")), quote=True)}" '
#                 f'data-duration="{duration_key}" id="cal-btn-{uid}">Schedule</a>'
#             )

#             out["embed_html"] = embed
#             doctors_out.append(out)

#         return {"patient": patient, "doctors": doctors_out}
#     except Exception as e:
#         return {"error": f"build_calendly_embed_error: {str(e)}"}


from langchain_core.tools import tool
import re


@tool
def build_calendly_embed(payload: dict) -> dict:
    """
    Takes {patient, doctors[]} JSON and injects Calendly inline widget HTML
    for each doctor based on patient_type.

    URL format:
    https://calendly.com/dattucodes/{doctor-full-name-hyphenated}-{duration}min-consultation-1
    where duration = 60 if patient_type = 'new', else 30.
    """
    patient = payload.get("patient", {})
    patient_type = (patient.get("patient_type") or "new").lower()
    duration = "60" if patient_type == "new" else "30"

    doctors_with_embeds = []
    for doc in payload.get("doctors", []):
        # doctor full name -> slug (lowercase, hyphenated)
        name_slug = re.sub(r"[^a-z0-9]+", "-", doc["name"].lower()).strip("-")

        url = (
            f"https://calendly.com/dattucodes/{name_slug}-{duration}min-consultation-1"
        )

        embed_html = f"""<!-- Calendly inline widget begin -->
<div class="calendly-inline-widget" data-url="{url}" style="min-width:320px;height:700px;"></div>
<script type="text/javascript" src="https://assets.calendly.com/assets/external/widget.js" async></script>
<!-- Calendly inline widget end -->"""

        doctors_with_embeds.append({**doc, "embed_html": embed_html})

    return {"patient": patient, "doctors": doctors_with_embeds}
