CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    UNIQUE(first_name, last_name, dob,email), 
    patient_type VARCHAR(20) CHECK(patient_type IN ('new','returning'))
);

CREATE TABLE insurance(
    insurance_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id) on DELETE CASCADE,
    carrier VARCHAR(100) NOT NULL,
    member_id VARCHAR(50) NOT NULL,
    group_number VARCHAR(50),
    is_primary BOOLEAN DEFAULT TRUE
);

CREATE TABLE doctors(
    doctor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE doctor_schedules(
    schedule_id SERIAL PRIMARY KEY,
    doctor_id INT REFERENCES doctors(doctor_id) on DELETE CASCADE,
    available_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    UNIQUE(doctor_id, available_date, start_time),
    is_booked BOOLEAN DEFAULT FALSE
);

CREATE TABLE appointments(
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id) on DELETE CASCADE,
    doctor_id INT REFERENCES doctors(doctor_id) on DELETE CASCADE,
    schedule_id INT REFERENCES doctor_schedules(schedule_id) on DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_duration INT NOT NULL CHECK (appointment_duration IN (30,60)),
    reason TEXT,
    status VARCHAR(20) CHECK(status IN ('scheduled','completed','canceled')) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reminders(
    reminder_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id) on DELETE CASCADE,
    reminder_number INT CHECK(reminder_number IN (1,2,3)),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response VARCHAR(50) CHECK(status IN ('confirmed','form_pending','cancelled'))
);

INSERT INTO patients (first_name, last_name, dob, gender, phone, email, patient_type) VALUES
('John', 'Doe', '1985-02-14', 'Male', '555-123-1111', 'john.doe@example.com', 'returning'),
('Jane', 'Smith', '1990-07-22', 'Female', '555-123-2222', 'jane.smith@example.com', 'new'),
('Michael', 'Johnson', '1978-03-05', 'Male', '555-123-3333', 'michael.j@example.com', 'returning');

INSERT INTO insurance (patient_id, carrier, member_id, group_number, is_primary) VALUES
(1, 'BlueCross', 'BC12345', '1001', TRUE),
(2, 'Aetna', 'AE56789', '2002', TRUE),
(3, 'UnitedHealth', 'UH24680', '3003', TRUE);

INSERT INTO doctors (first_name, last_name, specialty, phone, email) VALUES
('Alice', 'Williams', 'Allergist', '555-321-1111', 'alice.williams@clinic.com'),
('Robert', 'Brown', 'Pulmonologist', '555-321-2222', 'robert.brown@clinic.com');

INSERT INTO doctor_schedules (doctor_id, available_date, start_time, end_time, is_booked) VALUES
(1, '2025-09-05', '09:00', '10:00', FALSE),
(1, '2025-09-05', '10:00', '11:00', FALSE),
(2, '2025-09-05', '14:00', '15:00', FALSE);


INSERT INTO appointments (patient_id, doctor_id, schedule_id, appointment_date, appointment_time, appointment_duration, reason, status) VALUES
(1, 1, 1, '2025-09-05', '09:00', 30, 'Follow-up on allergies', 'scheduled'),
(2, 1, 2, '2025-09-05', '10:00', 60, 'Initial consultation', 'scheduled');

INSERT INTO reminders (appointment_id, reminder_number, response) VALUES
(1, 1, 'confirmed'),
(2, 1, 'form_pending');

