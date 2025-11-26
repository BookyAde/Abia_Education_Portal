-- Abia State Health Portal Schema

-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Hospitals Table
CREATE TABLE IF NOT EXISTS hospitals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    lga VARCHAR(100) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('General Hospital', 'PHC', 'Private', 'Specialist')),
    bed_capacity INTEGER DEFAULT 0,
    oxygen_tanks INTEGER DEFAULT 0,
    ambulances INTEGER DEFAULT 0,
    contact_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Daily Reports Table
CREATE TABLE IF NOT EXISTS daily_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID REFERENCES hospitals(id),
    report_date DATE DEFAULT CURRENT_DATE,
    births INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    malaria_cases INTEGER DEFAULT 0,
    cholera_cases INTEGER DEFAULT 0,
    notes TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Alerts Table (for Outbreaks)
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lga VARCHAR(100) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    message TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Seed Data (Example Hospitals)
INSERT INTO hospitals (name, lga, type, bed_capacity, oxygen_tanks, ambulances) VALUES
('Federal Medical Centre Umuahia', 'Umuahia North', 'Specialist', 500, 50, 5),
('Abia State Specialist Hospital', 'Umuahia North', 'Specialist', 300, 30, 3),
('General Hospital Aba', 'Aba North', 'General Hospital', 200, 20, 2),
('Living Word Hospital', 'Aba South', 'Private', 150, 15, 2),
('General Hospital Ohafia', 'Ohafia', 'General Hospital', 100, 10, 1);
