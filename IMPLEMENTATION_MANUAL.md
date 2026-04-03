# hexhytfvb TimeTracker - Implementation Manual

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup (Python FastAPI)](#backend-setup)
4. [Frontend Setup (React.js)](#frontend-setup)
5. [Database Configuration](#database-configuration)
6. [Email Configuration](#email-configuration)
7. [Running the Application](#running-the-application)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [User Roles & Permissions](#user-roles--permissions)
10. [SOC2 Compliance Features](#soc2-compliance-features)
11. [Deployment Guide](#deployment-guide)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

hexhytfvb TimeTracker is a comprehensive time tracking and management system with:

- **Frontend**: Pure React.js application
- **Backend**: Python FastAPI with SQLAlchemy 2.0
- **Database**: MySQL 8.0
- **Authentication**: JWT Bearer Token
- **Features**: Role-based access control, email verification, weekly reports, approval workflow

### Directory Structure

```
timetracker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── projects.py
│   │   │   ├── time_entries.py
│   │   │   └── reports.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── email_service.py
│   │   │   └── scheduler.py
│   │   └── main.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_migration.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/
    │   │   ├── App.js
    │   │   ├── Layout.js
    │   │   ├── Login.js
    │   │   ├── Register.js
    │   │   ├── Dashboard.js
    │   │   ├── Timesheets.js
    │   │   ├── Approvals.js
    │   │   ├── Projects.js
    │   │   ├── Reports.js
    │   │   └── UserProvisioning.js
    │   ├── services/
    │   │   └── api.js
    │   ├── stores/
    │   │   └── authStore.js
    │   ├── styles/
    │   │   └── index.css
    │   ├── App.js
    │   └── index.js
    └── package.json
```

---

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend build tools |
| MySQL | 8.0+ | Database |
| pip | Latest | Python package manager |
| npm/yarn | Latest | Node package manager |

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Check Node.js version
node --version    # Should be 18.x or higher

# Check MySQL
mysql --version   # Should be 8.0 or higher
```

---

## Backend Setup

### Step 1: Create Python Virtual Environment

```bash
cd timetracker/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
```

**.env file contents:**

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/project_reporting

# JWT Configuration
SECRET_KEY=your-super-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@tickmarks.com

# Frontend URL for email links
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### Step 4: Create MySQL Database

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE project_reporting CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional)
CREATE USER 'timetracker'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON project_reporting.* TO 'timetracker'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations
alembic upgrade head
```

### Step 6: Seed Initial Data

```bash
# Start the server temporarily to seed data
uvicorn app.main:app --reload

# In another terminal, call the seed endpoint
curl -X POST http://localhost:8000/api/seed
```

### Step 7: Run the Backend Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

---

## Frontend Setup

### Step 1: Install Dependencies

```bash
cd timetracker/frontend

# Install npm dependencies
npm install
```

### Step 2: Configure API URL (Optional)

If your backend is not running on localhost:8000, create a `.env` file:

```env
REACT_APP_API_URL=http://your-backend-url:port/api
```

### Step 3: Run the Development Server

```bash
npm start
```

The application will be available at: `http://localhost:3000`

### Step 4: Build for Production

```bash
npm run build
```

The production build will be in the `build/` directory.

---

## Database Configuration

### Schema Overview

The database consists of 6 core tables:

| Table | Description |
|-------|-------------|
| `users` | Employee/user accounts with manager hierarchy |
| `roles` | Role definitions (Admin, Manager, Member) |
| `user_roles` | Many-to-many user-role mapping |
| `projects` | Project records with manager assignment |
| `project_members` | User-project assignment with billing rates |
| `time_entries` | Daily time log entries with approval workflow |

### Entity Relationships

```
users (1) ←→ (N) users (self-ref: parent_id = manager)
users (N) ←→ (N) roles (via user_roles)
users (1) ←→ (N) projects (as manager)
users (N) ←→ (N) projects (via project_members)
users (1) ←→ (N) time_entries
projects (1) ←→ (N) time_entries
```

---

## Email Configuration

### Gmail Setup (Development)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account Settings → Security
   - Under "Signing in to Google", select App Passwords
   - Generate a new app password for "Mail"
3. Use the generated password in your `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM=noreply@tickmarks.com
```

### Email Features

The system sends emails for:
- **Email Verification**: When users register
- **Weekly Reports**: Every Sunday at 9 AM to project managers
- **Approval Notifications**: When entries are approved/rejected

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd timetracker/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd timetracker/frontend
npm start
```

### Default Credentials

After seeding the database:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@tickmarks.com | Admin@123 |
| Manager | manager@tickmarks.com | Manager@123 |
| Member | employee@tickmarks.com | Employee@123 |

---

## API Endpoints Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/register` | User registration |
| GET | `/api/auth/verify-email` | Email verification |
| POST | `/api/auth/resend-verification` | Resend verification email |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/users/me` | Get current user | Any |
| GET | `/api/users` | List all users | Admin/Manager |
| POST | `/api/users` | Create user | Admin |
| PUT | `/api/users/{id}` | Update user | Admin |
| DELETE | `/api/users/{id}` | Deactivate user | Admin |
| PUT | `/api/users/{id}/roles` | Update user roles | Admin |

### Projects

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/projects` | List projects | Any |
| POST | `/api/projects` | Create project | Admin |
| PUT | `/api/projects/{id}` | Update project | Admin |
| DELETE | `/api/projects/{id}` | Deactivate project | Admin |
| GET | `/api/projects/{id}/members` | Get project members | Any |
| POST | `/api/projects/{id}/members` | Add member | Admin/Manager |
| DELETE | `/api/projects/{id}/members/{user_id}` | Remove member | Admin/Manager |

### Time Entries

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/time-entries` | List entries | Any (own entries) |
| POST | `/api/time-entries` | Create entry | Any |
| PUT | `/api/time-entries/{id}` | Update entry | Owner |
| DELETE | `/api/time-entries/{id}` | Delete entry | Owner/Admin |
| POST | `/api/time-entries/{id}/approve` | Approve/Reject | Admin/Manager |
| POST | `/api/time-entries/{id}/resubmit` | Resubmit rejected | Owner |
| GET | `/api/time-entries/pending/approvals` | Pending approvals | Admin/Manager |

### Reports

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/reports/summary` | Project summary | Any |
| GET | `/api/reports/daily` | Daily breakdown | Any |
| GET | `/api/reports/by-reporting-area` | Hours by area | Any |
| GET | `/api/reports/user/{id}` | User report | Any (own) |

---

## User Roles & Permissions

### Admin (Role ID: 1)
- Full system access
- Manage all users, roles, and projects
- Approve/reject any time entry
- View all reports

### Manager (Role ID: 2)
- Manage assigned projects
- Add/remove project members
- Approve/reject time entries for managed projects
- View team reports

### Member (Role ID: 3)
- Log own time entries
- View assigned projects
- View own reports
- Resubmit rejected entries

---

## SOC2 Compliance Features

### 1. Email Verification
- All new registrations require email verification
- Verification tokens expire after 24 hours
- Unverified accounts cannot log in

### 2. Password Security
- Passwords hashed using bcrypt
- Minimum 8 character passwords
- Passwords never stored in plain text

### 3. Audit Trail
- All time entries track creation and approval timestamps
- Approval/rejection reasons logged
- User actions tracked

### 4. Role-Based Access Control
- Granular permissions per role
- Users can only access authorized resources
- API enforces role checks

### 5. Weekly Manager Reports
- Automated emails every Sunday at 9 AM
- Consolidated pending time entries
- Direct links to approval interface

### 6. Resubmission Workflow
- Rejected entries can be resubmitted
- Rejection reasons required
- Resubmission notes tracked

---

## Deployment Guide

### Production Checklist

1. **Environment Variables**
   - Set strong SECRET_KEY (32+ characters)
   - Configure production database URL
   - Set up production SMTP server
   - Set ENVIRONMENT=production

2. **Database**
   - Use managed MySQL (AWS RDS, Google Cloud SQL, etc.)
   - Enable SSL connections
   - Regular backups configured

3. **Backend**
   ```bash
   # Install production dependencies
   pip install gunicorn
   
   # Run with Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

4. **Frontend**
   ```bash
   # Build production bundle
   npm run build
   
   # Serve with nginx or similar
   ```

5. **SSL/TLS**
   - Enable HTTPS for all endpoints
   - Use Let's Encrypt for free certificates

### Docker Deployment

**Dockerfile - Backend:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile - Frontend:**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```
Error: Can't connect to MySQL server
```
- Verify MySQL is running
- Check DATABASE_URL in .env
- Ensure database exists

**2. Email Not Sending**
```
SMTP error
```
- Verify SMTP credentials
- For Gmail, use App Password
- Check firewall for SMTP port

**3. CORS Error in Frontend**
```
Access-Control-Allow-Origin error
```
- Backend CORS is configured for all origins in development
- For production, update CORS settings in main.py

**4. JWT Token Invalid**
```
Invalid or expired token
```
- Token expires in 60 minutes by default
- User needs to log in again

**5. Migration Fails**
```
Target database is not up to date
```
```bash
# Check current migration
alembic current

# Upgrade to latest
alembic upgrade head
```

### Getting Help

1. Check API documentation at `/docs`
2. Review server logs
3. Verify all environment variables are set
4. Ensure all dependencies are installed

---

## Support

For issues or questions:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Database: project_reporting on MySQL 8.0

---

**End of Implementation Manual**
