from typing import Dict, Any
from sqlalchemy import text
from langchain_core.tools import tool
from .db_connection import get_db

from pydantic import BaseModel

class PatientInfo(BaseModel):
    first_name: str
    last_name: str
    dob: str  # Date of Birth in 'YYYY-MM-DD' format
    email: str


@tool
def fetch_patient_record(patient_info: PatientInfo) -> Any:
    """Fetch a patient record from the database using first name, last name, DOB(YYYY-MM-DD), and email."""
    try:
        db = next(get_db())
        query = text(
            """
            SELECT * FROM patients
            WHERE first_name = :first_name
              AND last_name = :last_name
              AND dob = :dob
              AND email = :email
            LIMIT 1
            """
        )
        patient = db.execute(
            query,
            {
                "first_name": patient_info["first_name"],
                "last_name": patient_info["last_name"],
                "dob": patient_info["dob"],
                "email": patient_info["email"],
            },
        ).fetchone()
        if patient:
            return {
                "exists": True,
                "patient":{
                    "patient_id": patient.patient_id,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "dob": patient.dob,
                    "email": patient.email,
                    "phone": patient.phone,
                    "patient_type": patient.patient_type,
                },
                "message": "Patient record found." 
            }
        else:
            return {"exists": False, "message": "No matching patient record found."}
    except Exception as e:
        return f"Error fetching patient record: {str(e)}"


@tool
def insert_patient_record(patient_data: Dict[str, Any]) -> str:
    """Insert a new patient record into the database with first name, last name, DOB, email, and phone."""
    try:
        db = next(get_db())
        insert_query = text(
            """
            INSERT INTO patients (first_name, last_name, dob, email, phone, patient_type)
            VALUES (:first_name, :last_name, :dob, :email, :phone, :patient_type)
            RETURNING patient_id
            """
        )
        result = db.execute(
            insert_query,
            {
                "first_name": patient_data.get("first_name"),
                "last_name": patient_data.get("last_name"),
                "dob": patient_data.get("dob"),
                "email": patient_data.get("email"),
                "phone": patient_data.get("phone"),
                "patient_type": "new",
            },
        )
        db.commit()
        new_id = result.fetchone()[0]
        return f"New patient record inserted with ID: {new_id}"
    except Exception as e:
        return f"Error inserting patient record: {str(e)}"
