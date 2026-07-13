# How UniRecords Works

UniRecords follows a three-layer structure for the University Records Management
System.

## Browser And Presentation Layer

Flask routes in `app/routes/main.py` receive HTTP requests and render templates.
Templates display the dashboard, Student Directory, Student Detail, Student
write pages, read-only academic records and assignment reports. Static CSS and
JavaScript stay in `app/static`.

Routes do not query SQLAlchemy directly. They call `ApprovedStudentService` and
`StudentWriteService`, then translate unavailable database operations into safe
user-facing messages.

## Service Layer

`app/services/approved_student_service.py` owns the approved read-only Student
application boundary. It validates route input where needed and returns clean
Student records from the repository.

`app/services/student_write_service.py` owns Student create, edit and withdrawal
validation. It normalises form values, checks duplicate Student numbers and email
addresses, validates schema-limited status values and translates database errors
into safe messages.

## Repository Layer

`app/repositories/approved_student_repository.py` performs direct approved
Student database reads. It queries the schema-qualified
`use_record_management.vw_student_directory_masked` view through SQLAlchemy and
psycopg.

`app/repositories/student_write_repository.py` performs direct Student writes
with parameterised SQL. It writes to `person`, `student` and primary
`person_contact` records. Multi-table create and update operations commit only
after all related records succeed and roll back on failure.

`app/services/assignment_report_service.py` and
`app/repositories/assignment_report_repository.py` implement the assignment query
centre. The service validates report filters and the repository keeps all SQL in
the data layer.

## Data Flow

1. A user opens the Student Directory or a Student Detail page.
2. The route calls `ApprovedStudentService`.
3. The service calls `ApprovedStudentRepository`.
4. The repository reads from `use_record_management.vw_student_directory_masked`.
5. The route renders the Student interface.

## Student Write Flow

1. A user opens the Add, Edit or Withdraw Student page.
2. The route validates the CSRF token for POST requests.
3. The route passes form data to `StudentWriteService`.
4. The service validates and normalises the submitted values.
5. The repository writes to `person`, `student` and primary `person_contact`
   records using parameterised SQL.
6. The repository commits the transaction or rolls it back on failure.
7. The route redirects to the Student Detail page or re-renders the form with
   field-level errors.

The approved schema does not define an `Archived` Student status or a Student
delete procedure. The frontend therefore uses Withdraw Student, which sets
`student.student_status` to `Withdrawn` and preserves academic history.

## Report Query Flow

1. A user opens `/reports`.
2. The route displays the report catalogue from `AssignmentReportService`.
3. A user opens a report and submits filters.
4. The service validates the filters.
5. The repository runs parameterised SQL against approved tables or views.
6. The template displays result counts, empty states and responsive tables.

PostgreSQL is the sole supported implementation database. Unit tests do not
perform formal live PostgreSQL validation.

## Entry Points And Configuration

`run.py` is the local entry point and creates the app with the development
configuration.

`wsgi.py` is the deployment entry point and creates the app with the production
configuration.

The production configuration currently sets `DEBUG = False`. Further production
hardening should be added before a real deployment.

## Schema Management

The approved database baseline is the PostgreSQL `use_record_management` schema
in `sql/postgresql/`. The approved SQL scripts create the schema. Flask connects
to that schema through SQLAlchemy and repositories query or update it.

Alembic migrations are not used in this project because the approved SQL package
is the source of truth.

The simplified Student prototype model, repository, service, write templates and
seed script have been removed from the supported application path.

The `/health/database` endpoint checks database connectivity, schema presence
and whether the approved `student` table can be queried. It does not create or
change database objects.
