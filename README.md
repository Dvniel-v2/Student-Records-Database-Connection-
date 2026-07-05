# Student Records Database Connection

A complete starter repository for a three-layer, database-enabled Flask web application using PostgreSQL, SQLAlchemy, and a simple HTML/CSS/JavaScript frontend.

## Overview

This project demonstrates a clean separation of concerns across three layers:

- Presentation layer: Flask templates, CSS, and JavaScript
- Application layer: Flask routes and service classes with validation and error handling
- Data layer: SQLAlchemy models and repository functions backed by PostgreSQL

## Technology stack

- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- psycopg
- python-dotenv
- PostgreSQL
- pytest
- Ruff
- Black

## Repository structure

```text
project-root/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── example_model.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── example_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── example_repository.py
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── tests/
├── scripts/
├── migrations/
├── docs/
├── .github/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── run.py
└── wsgi.py
```

## Prerequisites

- Python 3.11+
- PostgreSQL installed and running
- Optional: pgAdmin for database administration

## PostgreSQL setup

1. Create a database in PostgreSQL, for example:

   ```sql
   CREATE DATABASE student_records;
   ```

2. Update the connection string in `.env` to match your local setup.

3. For local development, you can use pgAdmin to inspect the `records` table after running the app.

## Virtual environment setup

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux terminal

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Dependency installation

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Environment variable setup

Copy the example file and update the values:

```bash
cp .env.example .env
```

Example values:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=replace-with-a-secure-key
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/student_records
```

## Run the application

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000/`.

## Seed the database

```bash
python scripts/seed_database.py
```

## Run tests

```bash
pytest
```

## Run formatting and linting

```bash
ruff check .
black --check .
```

To format code:

```bash
black .
```

## Git and GitHub workflow

1. Create a repository on GitHub.
2. Initialise git locally.
3. Commit and push your changes.

```bash
git init
git add .
git commit -m "Initial project structure"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

## Troubleshooting

- If the database connection fails, confirm that PostgreSQL is running and the `DATABASE_URL` is correct.
- If the app fails to start, ensure that the virtual environment is activated and dependencies are installed.
- If tests fail, verify that `pytest` is using the application test configuration in `tests/conftest.py`.
