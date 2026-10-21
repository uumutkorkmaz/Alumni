from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Parent of every ORM model. Base.metadata describes all tables in ddd.md."""
