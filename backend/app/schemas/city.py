from pydantic import BaseModel, field_validator
from datetime import datetime
from app.schemas.weather import WeatherOut


class CityCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("City name cannot be empty")
        if len(v) > 100:
            raise ValueError("City name cannot exceed 100 characters")
        return v


class CityOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    weather: WeatherOut | None = None

    model_config = {"from_attributes": True}
