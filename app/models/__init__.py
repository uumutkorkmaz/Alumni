# Importing every model registers it on Base.metadata, so relationships can resolve
# each other by name and Alembic sees all tables.
from app.models.announcement import Announcement
from app.models.application import Application
from app.models.base import Base
from app.models.job_posting import JobPosting
from app.models.registration import RegistrationDocument
from app.models.session import SessionRow
from app.models.user import User

__all__ = ["Base", "User", "Announcement", "JobPosting", "Application", "RegistrationDocument", "SessionRow"]
