-- hexhytfvb TimeTracker - Supabase Database Initialization Script
-- Paste this into the Supabase SQL Editor and Click "Run"

-- 1. Create Roles Table
CREATE TABLE IF NOT EXISTS roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- 2. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT TRUE,
    parent_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token VARCHAR(255),
    requires_password_change BOOLEAN NOT NULL DEFAULT FALSE,
    otp_code VARCHAR(6),
    otp_expires_at TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create User_Roles Table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- 4. Create Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    client VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT TRUE,
    manager_id BIGINT REFERENCES users(id) ON DELETE RESTRICT,
    reporting_area VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create Project_Members Table
CREATE TABLE IF NOT EXISTS project_members (
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    bill_rate DECIMAL(10, 2),
    PRIMARY KEY (project_id, user_id)
);

-- 6. Create Time_Entries Table
CREATE TABLE IF NOT EXISTS time_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    hours DECIMAL(5, 2) NOT NULL CHECK (hours >= 0 AND hours <= 24),
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    approved_by_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    approval_date TIMESTAMP,
    rejection_reason TEXT,
    resubmission_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_time_entries_user_project_date UNIQUE (user_id, project_id, work_date)
);

-- 7. Create Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Seed Default Roles
INSERT INTO roles (id, name) VALUES (1, 'Admin'), (2, 'Manager'), (3, 'Member') ON CONFLICT (id) DO NOTHING;

-- 9. Seed Initial Admin User
-- Password: hexhytfvb@Admin123
INSERT INTO users (id, name, email, password_hash, status, email_verified)
VALUES (1, 'Initial Admin', 'hexhytfvb@gmail.com', '$2b$12$GpvpQpud7OAdeWwnsFMsQObopgL3NvvW5aulyERFlK42PswmGmx2S', TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 10. Assign Admin Role to Initial Admin
INSERT INTO user_roles (user_id, role_id) VALUES (1, 1) ON CONFLICT DO NOTHING;

-- 11. Adjust Sequences
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));
