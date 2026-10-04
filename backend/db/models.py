import uuid
from datetime import datetime
from uuid import UUID
from sqlalchemy import Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReportORM(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid.uuid4())
    transcription: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())