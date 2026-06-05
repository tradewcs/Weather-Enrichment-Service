import httpx
from celery import Celery
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.city import City
from app.models.weather import WeatherData

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"))


@celery_app.task(
    name="fetch_weather_task",
    autoretry_for=(Exception,),
    retry_backoff=10,
    max_retries=3,
)
def fetch_weather_task(city_id: int) -> None:
    with Session(sync_engine) as session:
        city = session.scalar(select(City).where(City.id == city_id))
        if not city:
            return

        response = httpx.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city.name,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        weather = WeatherData(
            city_id=city_id,
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
        )
        session.add(weather)
        session.commit()
