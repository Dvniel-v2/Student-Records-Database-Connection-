"""Service layer for dashboard data."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError

from app.repositories.approved_student_repository import ApprovedStudentRecord
from app.repositories.dashboard_repository import DashboardMetrics, DashboardRepository


class DashboardServiceError(RuntimeError):
    """Raised when approved dashboard data cannot be read."""


@dataclass(frozen=True)
class DashboardData:
    """Dashboard page data."""

    metrics: DashboardMetrics
    students: list[ApprovedStudentRecord]


class DashboardService:
    """Coordinate approved PostgreSQL dashboard reads."""

    def __init__(self, repository: DashboardRepository | None = None) -> None:
        self.repository = repository or DashboardRepository()

    def get_dashboard(self) -> DashboardData:
        """Return metrics and Student overview records for the dashboard."""
        try:
            return DashboardData(
                metrics=self.repository.get_metrics(),
                students=self.repository.get_student_overview(),
            )
        except SQLAlchemyError as exc:
            raise DashboardServiceError("Unable to read dashboard data.") from exc
