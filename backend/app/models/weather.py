from sqlalchemy import Float, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    feels_like: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    fetched_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    city: Mapped["City"] = relationship(back_populates="weather")
