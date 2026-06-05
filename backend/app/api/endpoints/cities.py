from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.city import City
from app.models.weather import WeatherData
from app.schemas.city import CityCreate, CityOut
from app.tasks.weather import fetch_weather_task

router = APIRouter(prefix="/cities", tags=["cities"])


@router.post("", response_model=CityOut, status_code=201)
async def add_city(payload: CityCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(City).where(City.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="City already exists")

    city = City(name=payload.name)
    db.add(city)
    await db.commit()
    await db.refresh(city)

    fetch_weather_task.delay(city.id)

    return city


@router.get("", response_model=list[CityOut])
async def get_cities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(City).options(selectinload(City.weather)))
    cities = result.scalars().all()

    output = []
    for city in cities:
        latest_weather = (
            sorted(city.weather, key=lambda w: w.fetched_at, reverse=True)[0]
            if city.weather
            else None
        )
        city_dict = {
            "id": city.id,
            "name": city.name,
            "created_at": city.created_at,
            "weather": latest_weather,
        }
        output.append(city_dict)

    return output


@router.post("/{city_id}/refresh", status_code=202)
async def refresh_weather(city_id: int, db: AsyncSession = Depends(get_db)):
    city = await db.scalar(select(City).where(City.id == city_id))
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    fetch_weather_task.delay(city_id)

    return {"message": "Weather update queued", "city_id": city_id}
