CREATE TYPE user_type_enum AS ENUM ('PACIENTE', 'MEDICO', 'RECEPCIONISTA', 'ADMIN');
CREATE TYPE appointment_status_enum AS ENUM ('AGENDADO', 'CONFIRMADO', 'PENDENTE', 'CANCELADO', 'CONCLUÍDO', 'REJEITADA');
CREATE TYPE specialty_enum AS ENUM ('FISIOTERAPEUTA', 'NUTRICIONISTA', 'PISIQUIATRA', 'DERMATOLOGISTA', 'PEDIATRIA');
CREATE TYPE payment_method_enum AS ENUM ('CARTAO', 'CONVENIO');

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type user_type_enum NOT NULL
);

CREATE TABLE patient (
    patient_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,

    CONSTRAINT fk_patient_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    crm VARCHAR(20) UNIQUE NOT NULL,
    specialty specialty_enum NOT NULL,

    CONSTRAINT fk_doctor_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE insurance (
    insurance_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    card_number VARCHAR(20) UNIQUE NOT NULL,
    expiration_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'VALIDO',

    CONSTRAINT fk_insurance_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE insurance_specialty (
    insurance_id INT NOT NULL,
    specialty specialty_enum NOT NULL,

    PRIMARY KEY (insurance_id, specialty),

    CONSTRAINT fk_insurance_specialty_insurance
        FOREIGN KEY (insurance_id)
        REFERENCES insurance(insurance_id)
        ON DELETE CASCADE
);

CREATE TABLE schedule (
    schedule_id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL, 
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    specialty specialty_enum NOT NULL,
    is_available BOOLEAN DEFAULT TRUE, --flag de disponivel genter

    CONSTRAINT fk_schedule_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE CASCADE
);

CREATE TABLE appointment (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    payment_method payment_method_enum NOT NULL,
    insurance_id INT,
    schedule_id INT NOT NULL,
    status appointment_status_enum DEFAULT 'AGENDADO',

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_appointment_insurance
        FOREIGN KEY (insurance_id)
        REFERENCES insurance(insurance_id),

    CONSTRAINT fk_appointment_schedule
        FOREIGN KEY (schedule_id)
        REFERENCES schedule(schedule_id)
        ON DELETE CASCADE
);

CREATE TABLE notification (
    notification_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    appointment_id INT NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    CONSTRAINT fk_notification_appointment
        FOREIGN KEY (appointment_id)
        REFERENCES appointment(appointment_id)
);

CREATE OR REPLACE FUNCTION generate_appointment_notification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO notification (user_id, appointment_id, message)
        VALUES (
            (SELECT user_id
             FROM patient
             WHERE patient_id = NEW.patient_id),
            NEW.appointment_id,
            'Status da consulta alterado para ' || NEW.status
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trigger_appointment_status
AFTER UPDATE OF status ON appointment
FOR EACH ROW
EXECUTE FUNCTION generate_appointment_notification();


CREATE OR REPLACE FUNCTION notify_new_notification()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'new_notification',
        NEW.notification_id::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trigger_new_notification
AFTER INSERT ON notification
FOR EACH ROW
EXECUTE FUNCTION notify_new_notification();

-- MOCKANDO O PRIMEIRO ADMIN 
INSERT INTO users (name, email, password, user_type)
VALUES
('Admin', 'admin@gmail.com', 'admin123', 'ADMIN')

