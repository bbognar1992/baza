"""
Weather service for weather data management and forecasting
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.weather_data import WeatherData


class WeatherService:
    """Service for weather-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_weather_forecast(self, location: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get weather forecast for a location"""
        start_date = date.today()
        end_date = start_date + timedelta(days=days)
        
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        ).order_by(WeatherData.date).all()
        
        forecast = []
        for weather in weather_data:
            forecast.append({
                'date': weather.date,
                'location': weather.location,
                'precipitation_probability': weather.precipitation_probability,
                'precipitation_hours': weather.precipitation_hours,
                'temperature_min': float(weather.temperature_min) if weather.temperature_min else None,
                'temperature_max': float(weather.temperature_max) if weather.temperature_max else None,
                'wind_speed': float(weather.wind_speed) if weather.wind_speed else None,
                'can_work_outdoor': weather.is_suitable_for_outdoor_work,
                'work_recommendation': weather.work_recommendation,
                'weather_summary': weather.weather_summary
            })
        
        return forecast
    
    def get_work_suitable_days(self, location: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get days suitable for outdoor work"""
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        ).all()
        
        suitable_days = []
        unsuitable_days = []
        
        for weather in weather_data:
            day_info = {
                'date': weather.date,
                'precipitation_probability': weather.precipitation_probability,
                'temperature_range': weather.temperature_range,
                'work_recommendation': weather.work_recommendation
            }
            
            if weather.is_suitable_for_outdoor_work:
                suitable_days.append(day_info)
            else:
                unsuitable_days.append(day_info)
        
        return {
            'location': location,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'suitable_days': suitable_days,
            'unsuitable_days': unsuitable_days,
            'suitability_percentage': (len(suitable_days) / len(weather_data) * 100) if weather_data else 0,
            'total_days': len(weather_data)
        }
    
    def get_weather_alerts(self, location: str) -> List[Dict[str, Any]]:
        """Get weather alerts for a location"""
        # Get weather data for the next 3 days
        start_date = date.today()
        end_date = start_date + timedelta(days=3)
        
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        ).all()
        
        alerts = []
        for weather in weather_data:
            # High precipitation alert
            if weather.precipitation_probability and weather.precipitation_probability > 70:
                alerts.append({
                    'type': 'high_precipitation',
                    'date': weather.date,
                    'message': f'High precipitation probability ({weather.precipitation_probability}%) on {weather.date}',
                    'severity': 'high' if weather.precipitation_probability > 90 else 'medium'
                })
            
            # Temperature alert
            if weather.temperature_max and weather.temperature_max > 35:
                alerts.append({
                    'type': 'high_temperature',
                    'date': weather.date,
                    'message': f'High temperature ({weather.temperature_max}°C) on {weather.date}',
                    'severity': 'high' if weather.temperature_max > 40 else 'medium'
                })
            
            if weather.temperature_min and weather.temperature_min < -5:
                alerts.append({
                    'type': 'low_temperature',
                    'date': weather.date,
                    'message': f'Low temperature ({weather.temperature_min}°C) on {weather.date}',
                    'severity': 'high' if weather.temperature_min < -10 else 'medium'
                })
            
            # Wind alert
            if weather.wind_speed and weather.wind_speed > 50:
                alerts.append({
                    'type': 'high_wind',
                    'date': weather.date,
                    'message': f'High wind speed ({weather.wind_speed} km/h) on {weather.date}',
                    'severity': 'high' if weather.wind_speed > 70 else 'medium'
                })
        
        return alerts
    
    def recommend_work_schedule(self, location: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Recommend optimal work schedule based on weather"""
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        ).order_by(WeatherData.date).all()
        
        recommendations = {
            'location': location,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'optimal_days': [],
            'avoid_days': [],
            'schedule_recommendations': []
        }
        
        for weather in weather_data:
            day_recommendation = {
                'date': weather.date,
                'weather_summary': weather.weather_summary,
                'work_recommendation': weather.work_recommendation,
                'suitable_for_outdoor': weather.is_suitable_for_outdoor_work,
                'priority': 'high' if weather.is_suitable_for_outdoor_work else 'low'
            }
            
            if weather.is_suitable_for_outdoor_work:
                recommendations['optimal_days'].append(day_recommendation)
            else:
                recommendations['avoid_days'].append(day_recommendation)
            
            # Generate specific recommendations
            if weather.precipitation_probability and weather.precipitation_probability > 60:
                recommendations['schedule_recommendations'].append({
                    'date': weather.date,
                    'type': 'indoor_work',
                    'message': f'Plan indoor work on {weather.date} due to high precipitation probability'
                })
            elif weather.temperature_max and weather.temperature_max > 30:
                recommendations['schedule_recommendations'].append({
                    'date': weather.date,
                    'type': 'early_work',
                    'message': f'Start work early on {weather.date} to avoid high temperatures'
                })
            elif weather.is_suitable_for_outdoor_work:
                recommendations['schedule_recommendations'].append({
                    'date': weather.date,
                    'type': 'optimal_conditions',
                    'message': f'Optimal conditions for outdoor work on {weather.date}'
                })
        
        return recommendations
    
    def get_weather_statistics(self, location: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get weather statistics for a location and period"""
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        ).all()
        
        if not weather_data:
            return {}
        
        # Calculate statistics
        precipitation_probs = [w.precipitation_probability for w in weather_data if w.precipitation_probability is not None]
        temperatures_max = [float(w.temperature_max) for w in weather_data if w.temperature_max is not None]
        temperatures_min = [float(w.temperature_min) for w in weather_data if w.temperature_min is not None]
        wind_speeds = [float(w.wind_speed) for w in weather_data if w.wind_speed is not None]
        
        suitable_days = len([w for w in weather_data if w.is_suitable_for_outdoor_work])
        
        statistics = {
            'location': location,
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'total_days': len(weather_data)
            },
            'precipitation': {
                'average_probability': sum(precipitation_probs) / len(precipitation_probs) if precipitation_probs else 0,
                'max_probability': max(precipitation_probs) if precipitation_probs else 0,
                'days_with_high_precipitation': len([p for p in precipitation_probs if p > 70])
            },
            'temperature': {
                'average_max': sum(temperatures_max) / len(temperatures_max) if temperatures_max else 0,
                'average_min': sum(temperatures_min) / len(temperatures_min) if temperatures_min else 0,
                'highest_temperature': max(temperatures_max) if temperatures_max else 0,
                'lowest_temperature': min(temperatures_min) if temperatures_min else 0
            },
            'wind': {
                'average_speed': sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0,
                'max_speed': max(wind_speeds) if wind_speeds else 0,
                'days_with_high_wind': len([w for w in wind_speeds if w > 50])
            },
            'work_suitability': {
                'suitable_days': suitable_days,
                'unsuitable_days': len(weather_data) - suitable_days,
                'suitability_percentage': (suitable_days / len(weather_data) * 100) if weather_data else 0
            }
        }
        
        return statistics
    
    def update_weather_data(self, location: str, date: date, weather_data: Dict[str, Any]) -> WeatherData:
        """Update or create weather data for a location and date"""
        existing = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date == date
        ).first()
        
        if existing:
            # Update existing record
            for field, value in weather_data.items():
                if hasattr(existing, field):
                    setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new record
            new_weather = WeatherData(
                location=location,
                date=date,
                **weather_data
            )
            self.db.add(new_weather)
            self.db.commit()
            self.db.refresh(new_weather)
            return new_weather
