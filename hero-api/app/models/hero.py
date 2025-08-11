from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Hero(Base):
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    intelligence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strength:     Mapped[int | None] = mapped_column(Integer, nullable=True)
    speed:        Mapped[int | None] = mapped_column(Integer, nullable=True)
    power:        Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint("name", name="uq_hero_name"),)


