from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    weather: Mapped[list["WeatherData"]] = relationship(
        back_populates="city",
        order_by="WeatherData.fetched_at.desc()",
    )
