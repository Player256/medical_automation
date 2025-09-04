import os
from sqlalchemy import create_engine, text
from calendly_service import CalendlyService

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/medical_db"
)


def main():
    engine = create_engine(DATABASE_URL, future=True)
    svc = CalendlyService()

    with engine.begin() as conn:
        doctors = (
            conn.execute(
                text(
                    "SELECT doctor_id, first_name, last_name FROM doctors WHERE calendly_30_url IS NULL OR calendly_60_url IS NULL"
                )
            )
            .mappings()
            .all()
        )

        for doc in doctors:
            doctor_id = doc["doctor_id"]
            doctor_name = f"{doc['first_name']} {doc['last_name']}"
            print(f"Setting up Calendly for {doctor_name}...")

            urls = svc.sync_doctor(doctor_id, doctor_name)

            conn.execute(
                text(
                    """
                    UPDATE doctors
                    SET calendly_30_url = :u30, calendly_60_url = :u60
                    WHERE doctor_id = :id
                """
                ),
                {"u30": urls["30min"], "u60": urls["60min"], "id": doctor_id},
            )

if __name__ == "__main__":
    main()
