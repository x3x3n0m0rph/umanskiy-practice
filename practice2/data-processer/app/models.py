from datetime import datetime

from sqlalchemy.orm import registry
from sqlalchemy import Column
from sqlalchemy import ForeignKey

from sqlalchemy.orm import registry, relationship
from sqlalchemy.types import Integer, Float, String, DateTime, LargeBinary

mapping_registry = registry() 
Base = mapping_registry.generate_base()

class Location(Base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

class WeatherStatus(Base):
    __tablename__ = "weather_status"
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey(f"{Location.__tablename__}.id"))
    location = relationship(Location)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    status_code = Column(Integer, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)


class WeatherReport(Base):
    __tablename__ = "weather_report"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    interval_start = Column(DateTime, nullable=False)
    interval_stop = Column(DateTime, nullable=False)
    image_blob = Column(LargeBinary, nullable=False)

    uploaded_at = Column(DateTime)
    upload_status = Column(Integer)
    upload_url = Column(String)