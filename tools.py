from typing import Dict, Any
from sqlalchemy import text
from langchain_core.tools import tool
from .db_connection import get_db


@tool
def fetch_patient_record(patient_info: Dict[str, Any]) -> Any:
    """Fetch a patient record from the database using first name, last name, DOB, and email."""
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
                "first_name": patient_info.get("first_name"),
                "last_name": patient_info.get("last_name"),
                "dob": patient_info.get("dob"),
                "email": patient_info.get("email"),
            },
        ).fetchone()
        return dict(patient) if patient else "No matching patient record found."
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
