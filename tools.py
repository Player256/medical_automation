from typing import Dict, Any
from sqlalchemy import text
from langchain_core.tools import tool
from .db_connection import get_db


@tool
def fetch_patient_record(patient_info: Dict[str, Any]) -> Any:
    try:
        db = next(get_db())
        query = text(
            """
                    Select * from patients
                    where first_name = :first_name
                        and last_name = :last_name
                        and dob = :dob
                        and email = :email
                        limit 1
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
    try:
        db = next(get_db())
        insert_query = text(
            """
            INSERT INTO patients (first_name, last_name, dob, email, phone)
            VALUES (:first_name, :last_name, :dob, :email, :phone, :patient_type)
            RETURNING id
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
