-- docker exec -it 3d5a6d31c721 psql -U user -d medical_db
-- Patients table
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    UNIQUE(first_name, last_name, dob, email),
    patient_type VARCHAR(20) CHECK(patient_type IN ('new','returning'))
);

-- Insurance table
CREATE TABLE insurance(
    insurance_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE,
    carrier VARCHAR(100) NOT NULL,
    member_id VARCHAR(50) NOT NULL,
    group_number VARCHAR(50),
    is_primary BOOLEAN DEFAULT TRUE
);

-- Doctors table
CREATE TABLE doctors(
    doctor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(100),
    phone TEXT,
    email VARCHAR(100),
    calendly_30_url TEXT,
    calendly_60_url TEXT
);

-- Appointments table
CREATE TABLE appointments(
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id INT REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_duration INT NOT NULL CHECK (appointment_duration IN (30,60)),
    reason TEXT,
    status VARCHAR(20) CHECK(status IN ('scheduled','completed','canceled')) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reminders table
CREATE TABLE reminders(
    reminder_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    reminder_number INT CHECK(reminder_number IN (1,2,3)),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response VARCHAR(50) CHECK(response IN ('confirmed','form_pending','cancelled'))
);

-- Patients seed data
INSERT INTO patients (first_name, last_name, dob, gender, phone, email, patient_type) VALUES
('John', 'Doe', '1985-02-14', 'Male', '555-123-1111', 'john.doe@example.com', 'returning'),
('Jane', 'Smith', '1990-07-22', 'Female', '555-123-2222', 'jane.smith@example.com', 'new'),
('Michael', 'Johnson', '1978-03-05', 'Male', '555-123-3333', 'michael.j@example.com', 'returning'),
('Emily', 'Davis', '1988-09-10', 'Female', '555-123-4444', 'emily.davis@example.com', 'new'),
('David', 'Miller', '1975-06-30', 'Male', '555-123-5555', 'david.miller@example.com', 'returning'),
('Sarah', 'Wilson', '1992-01-15', 'Female', '555-123-6666', 'sarah.wilson@example.com', 'new'),
('Chris', 'Moore', '1980-11-25', 'Male', '555-123-7777', 'chris.moore@example.com', 'returning'),
('Laura', 'Taylor', '1987-05-18', 'Female', '555-123-8888', 'laura.taylor@example.com', 'new'),
('Daniel', 'Anderson', '1972-03-11', 'Male', '555-123-9999', 'daniel.anderson@example.com', 'returning'),
('Sophia', 'Thomas', '1995-12-02', 'Female', '555-321-1010', 'sophia.thomas@example.com', 'new'),
('Ethan', 'Jackson', '1983-07-19', 'Male', '555-321-2020', 'ethan.jackson@example.com', 'returning'),
('Olivia', 'White', '1989-08-22', 'Female', '555-321-3030', 'olivia.white@example.com', 'new'),
('James', 'Harris', '1976-10-05', 'Male', '555-321-4040', 'james.harris@example.com', 'returning'),
('Isabella', 'Martin', '1991-02-14', 'Female', '555-321-5050', 'isabella.martin@example.com', 'new'),
('Alexander', 'Thompson', '1984-06-28', 'Male', '555-321-6060', 'alex.thompson@example.com', 'returning'),
('Mia', 'Garcia', '1993-04-12', 'Female', '555-321-7070', 'mia.garcia@example.com', 'new'),
('William', 'Martinez', '1981-09-17', 'Male', '555-321-8080', 'will.martinez@example.com', 'returning'),
('Charlotte', 'Robinson', '1986-11-29', 'Female', '555-321-9090', 'charlotte.robinson@example.com', 'new'),
('Benjamin', 'Clark', '1979-01-08', 'Male', '555-321-1112', 'ben.clark@example.com', 'returning'),
('Amelia', 'Rodriguez', '1994-05-21', 'Female', '555-321-1212', 'amelia.rodriguez@example.com', 'new');

-- Insurance seed data
INSERT INTO insurance (patient_id, carrier, member_id, group_number, is_primary) VALUES
(1, 'BlueCross', 'BC12345', '1001', TRUE),
(2, 'Aetna', 'AE56789', '2002', TRUE),
(3, 'UnitedHealth', 'UH24680', '3003', TRUE),
(4, 'Cigna', 'CI13579', '4004', TRUE),
(5, 'Humana', 'HU98765', '5005', TRUE),
(6, 'BlueCross', 'BC54321', '6006', TRUE),
(7, 'Aetna', 'AE11223', '7007', TRUE),
(8, 'UnitedHealth', 'UH99887', '8008', TRUE),
(9, 'Cigna', 'CI55667', '9009', TRUE),
(10, 'Humana', 'HU44556', '1010', TRUE),
(11, 'BlueCross', 'BC22334', '1111', TRUE),
(12, 'Aetna', 'AE33445', '1212', TRUE),
(13, 'UnitedHealth', 'UH55678', '1313', TRUE),
(14, 'Cigna', 'CI66789', '1414', TRUE),
(15, 'Humana', 'HU77890', '1515', TRUE),
(16, 'BlueCross', 'BC88901', '1616', TRUE),
(17, 'Aetna', 'AE99012', '1717', TRUE),
(18, 'UnitedHealth', 'UH10112', '1818', TRUE),
(19, 'Cigna', 'CI11122', '1919', TRUE),
(20, 'Humana', 'HU22233', '2020', TRUE);

-- Doctors seed data
INSERT INTO doctors (first_name, last_name, specialty, phone, email) VALUES
('Alice', 'Williams', 'Allergist', '555-321-1111', 'alice.williams@clinic.com'),
('Robert', 'Brown', 'Pulmonologist', '555-321-2222', 'robert.brown@clinic.com'),
('Karen', 'Hall', 'Cardiologist', '555-321-3333', 'karen.hall@clinic.com'),
('Steven', 'Young', 'Dermatologist', '555-321-4444', 'steven.young@clinic.com'),
('Nancy', 'King', 'Endocrinologist', '555-321-5555', 'nancy.king@clinic.com'),
('Mark', 'Wright', 'Gastroenterologist', '555-321-6666', 'mark.wright@clinic.com'),
('Patricia', 'Scott', 'Neurologist', '555-321-7777', 'patricia.scott@clinic.com'),
('George', 'Green', 'Oncologist', '555-321-8888', 'george.green@clinic.com'),
('Linda', 'Adams', 'Pediatrician', '555-321-9999', 'linda.adams@clinic.com'),
('Thomas', 'Baker', 'Psychiatrist', '555-321-1213', 'thomas.baker@clinic.com'),
('Barbara', 'Nelson', 'Radiologist', '555-321-1415', 'barbara.nelson@clinic.com'),
('Paul', 'Carter', 'Surgeon', '555-321-1617', 'paul.carter@clinic.com'),
('Jennifer', 'Mitchell', 'Rheumatologist', '555-321-1819', 'jennifer.mitchell@clinic.com'),
('Kevin', 'Perez', 'Urologist', '555-321-2021', 'kevin.perez@clinic.com'),
('Donna', 'Roberts', 'Ophthalmologist', '555-321-2223', 'donna.roberts@clinic.com'),
('Edward', 'Turner', 'Orthopedic', '555-321-2425', 'edward.turner@clinic.com'),
('Susan', 'Phillips', 'Nephrologist', '555-321-2627', 'susan.phillips@clinic.com'),
('Charles', 'Campbell', 'Immunologist', '555-321-2829', 'charles.campbell@clinic.com'),
('Jessica', 'Parker', 'Gynecologist', '555-321-3031', 'jessica.parker@clinic.com'),
('Brian', 'Evans', 'General Physician', '555-321-3233', 'brian.evans@clinic.com');

-- Appointments seed data
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, appointment_duration, reason, status) VALUES
(1, 1, '2025-09-05', '09:30', 30, 'Follow-up on allergies', 'scheduled'),
(2, 2, '2025-09-05', '10:30', 60, 'Respiratory issues', 'scheduled'),
(3, 3, '2025-09-05', '08:30', 30, 'Heart checkup', 'scheduled'),
(4, 4, '2025-09-05', '12:30', 30, 'Skin rash consultation', 'scheduled'),
(5, 5, '2025-09-05', '09:30', 30, 'Thyroid follow-up', 'scheduled');

-- Reminders seed data
INSERT INTO reminders (appointment_id, reminder_number, response) VALUES
(1, 1, 'confirmed'),
(2, 1, 'form_pending'),
(3, 1, 'confirmed'),
(4, 1, 'form_pending'),
(5, 1, 'confirmed');
