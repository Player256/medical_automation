# tools.py
from typing import Dict, Any
from sqlalchemy import text
from langchain_core.tools import tool
from pydantic import BaseModel
from .db_connection import get_db


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
