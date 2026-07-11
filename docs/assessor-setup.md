# Assessor Setup Guide

This guide explains how to run the University Records Database Management
System on a Windows computer using PowerShell, pgAdmin and PostgreSQL.

PostgreSQL is the only supported implementation database. The approved SQL
scripts in `sql/postgresql/` are the database source of truth.

## Expected Flow

```text
Browser
  -> Flask
  -> ApprovedStudentService
  -> ApprovedStudentRepository
  -> use_records
  -> use_record_management
  -> vw_student_directory_masked
```

The frontend is served through Flask. Do not open the HTML files directly in a
browser. The Student Directory requires PostgreSQL to be running and the
approved SQL scripts to have been executed.

The application does not create the PostgreSQL database automatically.

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

Do not commit `.env`. It contains local credentials and is ignored by Git.

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
