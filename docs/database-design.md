# Database Design

The application stores student records in a `students` table.

## `students`

| Column | Type | Rules |
| --- | --- | --- |
| `id` | Integer | Primary key |
| `student_number` | String(20) | Required, unique, indexed |
| `first_name` | String(80) | Required |
| `last_name` | String(80) | Required |
| `email` | String(255) | Required, unique, indexed |
| `course` | String(120) | Required |
| `enrolment_date` | Date | Required |

## Validation Responsibilities

The database enforces primary key, required, and unique constraints. The service
layer validates required fields, email format, name lengths, duplicate student
numbers, duplicate emails, and enrolment dates before committing changes.

## PostgreSQL and pgAdmin

Local development uses PostgreSQL with the `student_records` database name.
pgAdmin is useful for inspecting rows and checking schema state, but migrations
are the source of truth for schema changes.
