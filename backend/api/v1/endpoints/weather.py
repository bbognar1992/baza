"""
Weather Data API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.weather_data import WeatherData
from schemas.weather import WeatherDataCreate, WeatherDataUpdate, WeatherDataResponse, WeatherDataList

router = APIRouter()


@router.get("/", response_model=WeatherDataList)
async def get_weather_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    location: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get all weather data with pagination and optional filtering"""
    query = db.query(WeatherData)
    
    if location:
        query = query.filter(WeatherData.location == location)
    if start_date:
        query = query.filter(WeatherData.date >= start_date)
    if end_date:
        query = query.filter(WeatherData.date <= end_date)
    
    weather_data = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return WeatherDataList(
        weather_data=[WeatherDataResponse.from_orm(wd) for wd in weather_data],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{weather_id}", response_model=WeatherDataResponse)
async def get_weather_data_by_id(weather_id: int, db: Session = Depends(get_db)):
    """Get specific weather data by ID"""
    weather = db.query(WeatherData).filter(WeatherData.weather_id == weather_id).first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return WeatherDataResponse.from_orm(weather)


@router.get("/location/{location}/date/{date}", response_model=WeatherDataResponse)
async def get_weather_by_location_and_date(location: str, date: date, db: Session = Depends(get_db)):
    """Get weather data by location and date"""
    weather = db.query(WeatherData).filter(
        WeatherData.location == location,
        WeatherData.date == date
    ).first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found for this location and date")
    return WeatherDataResponse.from_orm(weather)


@router.post("/", response_model=WeatherDataResponse)
async def create_weather_data(weather: WeatherDataCreate, db: Session = Depends(get_db)):
    """Create new weather data"""
    # Check if weather data already exists for this location and date
    existing = db.query(WeatherData).filter(
        WeatherData.location == weather.location,
        WeatherData.date == weather.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Weather data already exists for this location and date")
    
    db_weather = WeatherData(**weather.dict())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    
    return WeatherDataResponse.from_orm(db_weather)


@router.put("/{weather_id}", response_model=WeatherDataResponse)
async def update_weather_data(weather_id: int, weather_update: WeatherDataUpdate, db: Session = Depends(get_db)):
    """Update weather data"""
    weather = db.query(WeatherData).filter(WeatherData.weather_id == weather_id).first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    update_data = weather_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(weather, field, value)
    
    db.commit()
    db.refresh(weather)
    
    return WeatherDataResponse.from_orm(weather)


@router.delete("/{weather_id}")
async def delete_weather_data(weather_id: int, db: Session = Depends(get_db)):
    """Delete weather data"""
    weather = db.query(WeatherData).filter(WeatherData.weather_id == weather_id).first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    db.delete(weather)
    db.commit()
    
    return {"message": "Weather data deleted successfully"}
