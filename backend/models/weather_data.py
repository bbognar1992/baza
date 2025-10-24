"""
Weather Data model for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class WeatherData(Base, TimestampMixin):
    """Weather information for scheduling decisions"""
    __tablename__ = 'weather_data'
    
    weather_id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    precipitation_probability = Column(Integer)  # 0-100
    precipitation_hours = Column(Integer, default=0)
    temperature_min = Column(Numeric(5, 2))
    temperature_max = Column(Numeric(5, 2))
    wind_speed = Column(Numeric(5, 2))
    can_work_outdoor = Column(Boolean)  # Computed field
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('location', 'date', name='uq_weather_location_date'),
    )
    
    def __repr__(self):
        return f"<WeatherData(id={self.weather_id}, location='{self.location}', date='{self.date}')>"
    
    @property
    def is_suitable_for_outdoor_work(self):
        """Check if weather is suitable for outdoor work"""
        return (
            self.precipitation_probability < 40 and 
            self.precipitation_hours <= 2
        )
    
    @property
    def temperature_range(self):
        """Get temperature range as string"""
        if self.temperature_min and self.temperature_max:
            return f"{self.temperature_min}°C - {self.temperature_max}°C"
        return "N/A"
    
    @property
    def weather_summary(self):
        """Get weather summary"""
        if self.precipitation_probability is not None:
            return f"Csapadék esély: {self.precipitation_probability}%, esős órák: {self.precipitation_hours}"
        return "Időjárási adatok nem elérhetők"
    
    @property
    def work_recommendation(self):
        """Get work recommendation based on weather"""
        if self.is_suitable_for_outdoor_work:
            return "✅ Kiváló időjárás a kültéri munkákhoz"
        elif self.precipitation_probability and self.precipitation_probability < 60:
            return "⚠️ Óvatosan, enyhe csapadék várható"
        else:
            return "❌ Nem ajánlott kültéri munka"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'weather_id': self.weather_id,
            'location': self.location,
            'date': self.date.isoformat() if self.date else None,
            'precipitation_probability': self.precipitation_probability,
            'precipitation_hours': self.precipitation_hours,
            'temperature_min': float(self.temperature_min) if self.temperature_min else None,
            'temperature_max': float(self.temperature_max) if self.temperature_max else None,
            'wind_speed': float(self.wind_speed) if self.wind_speed else None,
            'can_work_outdoor': self.can_work_outdoor,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
