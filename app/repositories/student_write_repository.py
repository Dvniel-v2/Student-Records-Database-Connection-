"""Write repository for approved PostgreSQL Student workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text

from app.config import APPROVED_DATABASE_SCHEMA
from app.extensions import db
from app.repositories.approved_student_repository import ProgrammeOption


@dataclass(frozen=True)
class EditableStudentRecord:
    """Editable Student fields from the approved normalised schema."""

    student_id: int
    person_id: int
    student_number: str
    first_name: str
    last_name: str
    masked_email: str
    phone: str | None
    nationality: str | None
    programme_code: str
    programme_name: str
    date_of_birth: str
    enrolment_year: int
    year_of_study: int
    admission_type: str
    student_status: str
    graduation_status: str


class StudentWriteRepository:
    """Persist Student writes to person and student tables."""

    def __init__(self, schema_name: str = APPROVED_DATABASE_SCHEMA) -> None:
        self.schema_name = schema_name

    def list_programmes(self) -> list[ProgrammeOption]:
        """Return active programmes for Student forms."""
        rows = db.session.execute(
            text(
                f"""
                SELECT programme_code, programme_name
                FROM {self.schema_name}.programme
                WHERE is_active IS TRUE
                ORDER BY programme_code
                """
            )
        ).mappings()
        return [ProgrammeOption(**dict(row)) for row in rows]

    def get_student_for_edit(self, student_id: int) -> EditableStudentRecord | None:
        """Return normalised Student fields for editing."""
        row = (
            db.session.execute(
                text(
                    f"""
                    SELECT
                        s.student_id,
                        p.person_id,
                        s.student_number,
                        p.first_name,
                        p.last_name,
                        CONCAT(LEFT(p.email, 2), '***@', split_part(p.email, '@', 2))
                            AS masked_email,
                        p.phone,
                        p.nationality,
                        pr.programme_code,
                        pr.programme_name,
                        s.date_of_birth::text AS date_of_birth,
                        s.enrolment_year,
                        s.year_of_study,
                        s.admission_type,
                        s.student_status,
                        s.graduation_status
                    FROM {self.schema_name}.student s
                    JOIN {self.schema_name}.person p
                        ON p.person_id = s.person_id
                    JOIN {self.schema_name}.programme pr
                        ON pr.programme_id = s.programme_id
                    WHERE s.student_id = :student_id
                    """
                ),
                {"student_id": student_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        return EditableStudentRecord(**dict(row))

    def student_number_exists(
        self, student_number: str, exclude_student_id: int | None = None
    ) -> bool:
        """Return whether a Student number is already used."""
        params: dict[str, Any] = {"student_number": student_number}
        exclude_sql = ""
        if exclude_student_id is not None:
            exclude_sql = "AND student_id <> :student_id"
            params["student_id"] = exclude_student_id
        return bool(
            db.session.execute(
                text(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM {self.schema_name}.student
                        WHERE student_number = :student_number
                        {exclude_sql}
                    )
                    """
                ),
                params,
            ).scalar_one()
        )

    def email_exists(self, email: str, exclude_person_id: int | None = None) -> bool:
        """Return whether a person email is already used."""
        params: dict[str, Any] = {"email": email}
        exclude_sql = ""
        if exclude_person_id is not None:
            exclude_sql = "AND person_id <> :person_id"
            params["person_id"] = exclude_person_id
        return bool(
            db.session.execute(
                text(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM {self.schema_name}.person
                        WHERE email = :email
                        {exclude_sql}
                    )
                    """
                ),
                params,
            ).scalar_one()
        )

    def create_student(self, data: dict[str, Any]) -> int:
        """Create a Student through person and student in one transaction."""
        try:
            programme_id = self._programme_id(data["programme_code"])
            person_id = db.session.execute(
                text(
                    f"""
                    INSERT INTO {self.schema_name}.person
                        (first_name, last_name, email, phone, nationality)
                    VALUES
                        (:first_name, :last_name, :email, :phone, :nationality)
                    RETURNING person_id
                    """
                ),
                data,
            ).scalar_one()
            params = {**data, "person_id": person_id, "programme_id": programme_id}
            student_id = db.session.execute(
                text(
                    f"""
                    INSERT INTO {self.schema_name}.student
                        (
                            person_id,
                            student_number,
                            programme_id,
                            date_of_birth,
                            enrolment_year,
                            year_of_study,
                            admission_type,
                            student_status,
                            graduation_status
                        )
                    VALUES
                        (
                            :person_id,
                            :student_number,
                            :programme_id,
                            :date_of_birth,
                            :enrolment_year,
                            :year_of_study,
                            :admission_type,
                            :student_status,
                            :graduation_status
                        )
                    RETURNING student_id
                    """
                ),
                params,
            ).scalar_one()
            self._upsert_contact(person_id, "Email", data["email"], True)
            if data.get("phone"):
                self._upsert_contact(person_id, "Mobile", data["phone"], True)
            db.session.commit()
            return int(student_id)
        except Exception:
            db.session.rollback()
            raise

    def update_student(self, student_id: int, data: dict[str, Any]) -> None:
        """Update approved Student fields in one transaction."""
        try:
            current = self.get_student_for_edit(student_id)
            if current is None:
                raise LookupError("Student not found.")
            programme_id = self._programme_id(data["programme_code"])
            person_params = {
                **data,
                "person_id": current.person_id,
            }
            email_sql = ", email = :email" if data.get("email") else ""
            db.session.execute(
                text(
                    f"""
                    UPDATE {self.schema_name}.person
                    SET
                        first_name = :first_name,
                        last_name = :last_name,
                        phone = :phone,
                        nationality = :nationality
                        {email_sql}
                    WHERE person_id = :person_id
                    """
                ),
                person_params,
            )
            db.session.execute(
                text(
                    f"""
                    UPDATE {self.schema_name}.student
                    SET
                        student_number = :student_number,
                        programme_id = :programme_id,
                        date_of_birth = :date_of_birth,
                        enrolment_year = :enrolment_year,
                        year_of_study = :year_of_study,
                        admission_type = :admission_type,
                        student_status = :student_status,
                        graduation_status = :graduation_status
                    WHERE student_id = :student_id
                    """
                ),
                {**data, "student_id": student_id, "programme_id": programme_id},
            )
            if data.get("email"):
                self._upsert_contact(current.person_id, "Email", data["email"], True)
            if data.get("phone"):
                self._upsert_contact(current.person_id, "Mobile", data["phone"], True)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def withdraw_student(self, student_id: int) -> None:
        """Mark a Student as withdrawn without deleting academic history."""
        try:
            result = db.session.execute(
                text(
                    f"""
                    UPDATE {self.schema_name}.student
                    SET student_status = 'Withdrawn',
                        graduation_status = 'Not eligible'
                    WHERE student_id = :student_id
                    """
                ),
                {"student_id": student_id},
            )
            if result.rowcount == 0:
                raise LookupError("Student not found.")
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def _programme_id(self, programme_code: str) -> int:
        programme_id = db.session.execute(
            text(
                f"""
                SELECT programme_id
                FROM {self.schema_name}.programme
                WHERE programme_code = :programme_code
                    AND is_active IS TRUE
                """
            ),
            {"programme_code": programme_code},
        ).scalar_one_or_none()
        if programme_id is None:
            raise LookupError("Programme not found.")
        return int(programme_id)

    def _upsert_contact(
        self,
        person_id: int,
        contact_type: str,
        contact_value: str,
        is_primary: bool,
    ) -> None:
        existing_id = db.session.execute(
            text(
                f"""
                SELECT contact_id
                FROM {self.schema_name}.person_contact
                WHERE person_id = :person_id
                    AND contact_type = :contact_type
                ORDER BY is_primary DESC, contact_id
                LIMIT 1
                """
            ),
            {"person_id": person_id, "contact_type": contact_type},
        ).scalar_one_or_none()
        params = {
            "person_id": person_id,
            "contact_type": contact_type,
            "contact_value": contact_value,
            "is_primary": is_primary,
        }
        if existing_id is None:
            db.session.execute(
                text(
                    f"""
                    INSERT INTO {self.schema_name}.person_contact
                        (person_id, contact_type, contact_value, is_primary)
                    VALUES
                        (:person_id, :contact_type, :contact_value, :is_primary)
                    """
                ),
                params,
            )
            return
        db.session.execute(
            text(
                f"""
                UPDATE {self.schema_name}.person_contact
                SET contact_value = :contact_value,
                    is_primary = :is_primary
                WHERE contact_id = :contact_id
                """
            ),
            {**params, "contact_id": existing_id},
        )
