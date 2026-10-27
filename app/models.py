from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    plants: Mapped[list["Plant"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    species: Mapped[str | None] = mapped_column(String(100), nullable=True)
    watering_interval_days: Mapped[int] = mapped_column(Integer)
    last_watered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship(back_populates="plants")

    waterings: Mapped[list["Watering"]] = relationship(
        back_populates="plant", cascade="all, delete-orphan"
    )


class Watering(Base):
    __tablename__ = "waterings"

    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"))
    watered_at: Mapped[date] = mapped_column(Date)
    amount_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)

    plant: Mapped["Plant"] = relationship(back_populates="waterings")
