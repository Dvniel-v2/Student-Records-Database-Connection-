# Start Here

This guide explains how to run UniRecords, the University Records Management
System, on a local computer.

UniRecords needs two things before it can show records in the browser:

1. A local PostgreSQL database containing the approved university data.
2. A local Python environment that can run the Flask application.

PostgreSQL normally listens on `localhost:5432`. `localhost` means the current
computer only. Each person running the project creates their own local database
and uses their own private PostgreSQL password.

## Setup Flow

```text
Download or clone the repository
  -> install PostgreSQL and pgAdmin
  -> create use_records
  -> run approved SQL scripts
  -> create Python virtual environment
  -> install Python dependencies
  -> create local .env
  -> add local PostgreSQL credentials
  -> run Flask
  -> use the frontend
```

The dependency order is:

```text
Database
  -> Python environment
  -> Local configuration
  -> Application startup
  -> Connection verification
```

## 1. Download Or Clone The Repository

Download the project ZIP or clone the repository.

Open PowerShell in the project root before running project commands.

## 2. Install PostgreSQL And pgAdmin

Install PostgreSQL and pgAdmin on your computer.

During PostgreSQL installation:

1. Keep port `5432` unless you have a reason to use another port.
2. Create and remember the local `postgres` password.
3. Install pgAdmin so you can create the database and run SQL scripts.

Do not commit or share the PostgreSQL password.

## 3. Open pgAdmin

Open pgAdmin and connect to the local PostgreSQL server.

You may be asked for the local `postgres` password created during installation.

## 4. Create The Database

Create a database named:

```text
use_records
```

After creating it, pgAdmin should show a structure like:

```text
Databases
  -> use_records
```

## 5. Open Query Tool For `use_records`

In pgAdmin, select the `use_records` database and open Query Tool.

The approved SQL files must be run while connected to `use_records`.

## 6. Run The Approved SQL Scripts

Run these files in numbered order:

```text
sql/postgresql/01_create_use_full_schema_postgresql.sql
sql/postgresql/02_insert_use_master_data_postgresql.sql
sql/postgresql/03_insert_use_activity_records_postgresql.sql
sql/postgresql/04_use_validation_queries_postgresql.sql
```

File 01 drops and recreates the `use_record_management` schema. Do not run it
against a database that contains work you need to keep.

## 7. Confirm The Schema Exists

After running the scripts, pgAdmin should show:

```text
use_records
  -> Schemas
      -> use_record_management
          -> Tables
          -> Views
          -> Procedures
```

The application expects this structure:

```text
PostgreSQL 18
  -> database: use_records
  -> schema: use_record_management
  -> tables, views, procedures and approved data
```

## 8. Create The Python Virtual Environment

```powershell
py -m venv .venv
```

## 9. Activate The Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## 10. Install Requirements

```powershell
pip install -r requirements.txt
```

## 11. Create The Local Environment File

```powershell
Copy-Item .env.example .env
```

## 12. Add Local PostgreSQL Credentials

Update only the local `.env` file:

```env
FLASK_APP=run.py
SECRET_KEY=replace-with-a-secure-local-key
DATABASE_URL=postgresql+psycopg://postgres:YOUR_LOCAL_PASSWORD@localhost:5432/use_records
```

Replace `YOUR_LOCAL_PASSWORD` with the PostgreSQL password for your computer.

Credential rules:

1. Do not commit `.env`.
2. Do not commit real PostgreSQL passwords.
3. Do not hard-code credentials.
4. Do not share another developer's local PostgreSQL password.
5. Each user supplies their own local PostgreSQL credentials.

## 13. Run Flask

```powershell
python run.py
```

Port `5000` is the default. If it is unavailable, the application starts on the
next available local port and prints the correct URL.

## 14. Open The Application

Open the exact URL printed in the terminal.

The frontend is served through Flask. Do not open the HTML files directly in a
browser.

## 15. Check Database Health

Add `/health/database` to the printed base URL.

```text
<printed-base-url>/health/database
```

The endpoint checks that Flask can connect to PostgreSQL, that the
`use_record_management` schema exists and that the approved `student` table can
be queried.

## 16. Verify The Main Pages

Confirm these pages load:

1. Dashboard
2. Students
3. Reports

Expected visual result:

1. Dashboard shows metrics and charts.
2. Students shows approved Student records.
3. Reports shows the assignment report catalogue.

## Project Handover

The repository or submission package contains:

1. Flask application
2. Frontend files
3. Approved PostgreSQL SQL scripts
4. `requirements.txt`
5. `.env.example`
6. Start Here guide
7. Assignment requirements and final checklist documents

The package does not contain:

1. A live PostgreSQL server
2. A developer's `.env`
3. A developer's PostgreSQL password
4. A developer's `.venv`

The PostgreSQL database is live locally only while the PostgreSQL service is
running. It is not publicly hosted and is not accessible through the internet.

## Common Errors

### Unable To Read Approved Student Records

Likely causes:

1. PostgreSQL is not running.
2. `.env` does not exist.
3. `DATABASE_URL` contains the wrong password.
4. `use_records` does not exist.
5. The SQL scripts were run against a different database.
6. `use_record_management` does not exist.
7. `vw_student_directory_masked` does not exist.

### PowerShell Cannot Activate The Virtual Environment

If `.venv` has not been created, run:

```powershell
py -m venv .venv
```

If PowerShell blocks activation for the current session, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```
