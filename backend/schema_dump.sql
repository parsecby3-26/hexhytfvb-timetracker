-- Table: users

CREATE TABLE users (
	id BIGSERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	status BOOLEAN NOT NULL, 
	parent_id BIGINT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	email_verified BOOLEAN NOT NULL, 
	verification_token VARCHAR(255), 
	password_reset_token VARCHAR(255), 
	password_reset_token_expires TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_id) REFERENCES users (id)
)

;

-- Table: roles

CREATE TABLE roles (
	id BIGSERIAL NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)

;

-- Table: user_roles

CREATE TABLE user_roles (
	user_id BIGINT NOT NULL, 
	role_id BIGINT NOT NULL, 
	PRIMARY KEY (user_id, role_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
)

;

-- Table: projects

CREATE TABLE projects (
	id BIGSERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	client VARCHAR(255) NOT NULL, 
	status BOOLEAN NOT NULL, 
	manager_id BIGINT NOT NULL, 
	reporting_area VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(manager_id) REFERENCES users (id)
)

;

-- Table: project_members

CREATE TABLE project_members (
	project_id BIGINT NOT NULL, 
	user_id BIGINT NOT NULL, 
	bill_rate DECIMAL(10, 2), 
	PRIMARY KEY (project_id, user_id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

;

-- Table: time_entries

CREATE TABLE time_entries (
	id BIGSERIAL NOT NULL, 
	user_id BIGINT NOT NULL, 
	project_id BIGINT NOT NULL, 
	work_date DATE NOT NULL, 
	hours DECIMAL(5, 2) NOT NULL, 
	notes TEXT, 
	status VARCHAR(20) NOT NULL, 
	approved_by_id BIGINT, 
	approval_date TIMESTAMP WITHOUT TIME ZONE, 
	rejection_reason TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	resubmission_notes TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_time_entries_user_project_date UNIQUE (user_id, project_id, work_date), 
	CONSTRAINT check_hours_range CHECK (hours >= 0 AND hours <= 24), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(approved_by_id) REFERENCES users (id)
)

;

