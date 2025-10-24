"""
Pydantic schemas for WeatherData model
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class WeatherDataBase(BaseModel):
    """Base weather data schema"""
    location: str
    date: date
    precipitation_probability: Optional[int] = None
    precipitation_hours: int = 0
    temperature_min: Optional[Decimal] = None
    temperature_max: Optional[Decimal] = None
    wind_speed: Optional[Decimal] = None
    can_work_outdoor: Optional[bool] = None

    @validator('precipitation_probability')
    def validate_precipitation_probability(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Precipitation probability must be between 0 and 100')
        return v


class WeatherDataCreate(WeatherDataBase):
    """Schema for creating weather data"""
    pass


class WeatherDataUpdate(BaseModel):
    """Schema for updating weather data"""
    location: Optional[str] = None
    date: Optional[date] = None
    precipitation_probability: Optional[int] = None
    precipitation_hours: Optional[int] = None
    temperature_min: Optional[Decimal] = None
    temperature_max: Optional[Decimal] = None
    wind_speed: Optional[Decimal] = None
    can_work_outdoor: Optional[bool] = None


class WeatherDataResponse(WeatherDataBase):
    """Schema for weather data response"""
    weather_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherDataList(BaseModel):
    """Schema for weather data list response"""
    weather_data: list[WeatherDataResponse]
    total: int
    page: int
    size: int
