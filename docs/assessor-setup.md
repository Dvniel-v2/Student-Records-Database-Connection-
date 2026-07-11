# Assessor Setup Guide

This guide explains how to run the University Records Database Management
System on a Windows computer using PowerShell, pgAdmin and PostgreSQL.

PostgreSQL is the only supported implementation database. The approved SQL
scripts in `sql/postgresql/` are the database source of truth.

The PostgreSQL server runs locally on the computer where it is installed,
normally at `localhost:5432`. `localhost` means the current computer only. Other
users, group members and assessors cannot access another developer's local
PostgreSQL database.

Each user recreates the database locally by downloading or cloning the
repository, installing PostgreSQL, creating `use_records`, running the approved
SQL scripts, creating their own private `.env`, and supplying their own
PostgreSQL username and password.

The PostgreSQL database is live locally while the PostgreSQL service is running.
It is not publicly hosted and is not accessible through the internet. The
repository provides all approved SQL scripts needed to reproduce the database on
another computer.

## Expected Flow

```text
Browser
  -> Flask
  -> ApprovedStudentService
  -> ApprovedStudentRepository
  -> PostgreSQL 18
  -> database: use_records
  -> schema: use_record_management
  -> tables, views, procedures and approved data
  -> view: vw_student_directory_masked
```

The frontend is served through Flask. Do not open the HTML files directly in a
browser. The Student Directory requires PostgreSQL to be running and the
approved SQL scripts to have been executed.

The application does not create the PostgreSQL database automatically.

## Reproducibility Flow

```text
GitHub repository or submission ZIP
  -> install Python dependencies
  -> install PostgreSQL
  -> create use_records
  -> run approved SQL scripts
  -> create local .env
  -> add local PostgreSQL credentials
  -> run Flask
  -> use the frontend
```

## Handover Package

The submitted repository or full ZIP package contains:

1. Flask application
2. Frontend files
3. Approved PostgreSQL SQL scripts
4. `requirements.txt`
5. `.env.example`
6. Assessor setup guide

The package does not contain:

1. The developer's live local PostgreSQL server
2. The developer's `.env`
3. The developer's PostgreSQL password
4. The developer's `.venv`

Credential rules:

1. Do not commit `.env`.
2. Do not commit real PostgreSQL passwords.
3. Do not hard-code credentials.
4. Do not share the developer's local PostgreSQL password.
5. Each user supplies their own local PostgreSQL credentials.
6. `.env.example` remains a safe template.

## Local Setup

1. Download or clone the repository.

2. Open PowerShell in the project root.

3. Create the virtual environment:

```powershell
py -m venv .venv
```

4. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```powershell
pip install -r requirements.txt
```

6. Open pgAdmin.

7. Create a PostgreSQL database named:

```text
use_records
```

8. Run the approved SQL scripts against `use_records` in this order:

```text
sql/postgresql/01_create_use_full_schema_postgresql.sql
sql/postgresql/02_insert_use_master_data_postgresql.sql
sql/postgresql/03_insert_use_activity_records_postgresql.sql
sql/postgresql/04_use_validation_queries_postgresql.sql
```

9. Create the private local environment file:

```powershell
Copy-Item .env.example .env
```

10. Update only the local `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/use_records
```

Replace `YOUR_PASSWORD` with the local PostgreSQL password for the current
computer. Do not use or share another developer's local PostgreSQL password.
Do not commit `.env`; it contains local credentials and is ignored by Git.

11. Start the application:

```powershell
python run.py
```

12. Open the application:

```text
http://127.0.0.1:5000/
```

13. Check the database health endpoint:

```text
http://127.0.0.1:5000/health/database
```

## Success Conditions

Successful local setup means:

1. The Flask application starts.
2. The homepage loads.
3. The Student Directory displays approved PostgreSQL records.
4. Student detail pages open.
5. The database health endpoint reports success.

These checks must be confirmed on the local computer running the project.

## Common Errors

### Unable to read approved student records.

Likely causes:

1. PostgreSQL is not running.
2. `.env` does not exist.
3. `DATABASE_URL` contains the wrong password.
4. `use_records` does not exist.
5. The SQL scripts were run against a different database.
6. `use_record_management` does not exist.
7. `vw_student_directory_masked` does not exist.

### `.\.venv\Scripts\Activate.ps1` is not recognized

Cause:

`.venv` has not been created.

Fix:

```powershell
py -m venv .venv
```

### PowerShell execution policy error

For the current PowerShell session, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the virtual environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```
