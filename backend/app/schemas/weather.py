from pydantic import BaseModel
from datetime import datetime


class WeatherOut(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    fetched_at: datetime

    model_config = {"from_attributes": True}
