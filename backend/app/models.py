"""Database models for GIS analysis application."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Image(Base):
    """Model for storing satellite/aerial imagery metadata."""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    filepath = Column(String, unique=True)
    upload_date = Column(DateTime, default=datetime.utcnow)

    # Geospatial metadata
    crs = Column(String)  # Coordinate Reference System
    bounds_minx = Column(Float)  # Bounding box
    bounds_miny = Column(Float)
    bounds_maxx = Column(Float)
    bounds_maxy = Column(Float)

    # Image properties
    width = Column(Integer)
    height = Column(Integer)
    bands = Column(Integer)
    resolution = Column(Float)  # Pixel resolution in meters

    # Additional metadata (JSON field for flexible storage)
    raw_metadata = Column(JSON)

    # Relationships
    detections = relationship("Detection", back_populates="image", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="image", cascade="all, delete-orphan")


class Detection(Base):
    """Model for storing object detection results."""
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))

    # Detection info
    class_name = Column(String, index=True)  # e.g., "car", "truck", "building"
    confidence = Column(Float)

    # Pixel coordinates (bounding box)
    bbox_x1 = Column(Integer)
    bbox_y1 = Column(Integer)
    bbox_x2 = Column(Integer)
    bbox_y2 = Column(Integer)

    # Geographic coordinates (center point)
    latitude = Column(Float)
    longitude = Column(Float)

    detection_date = Column(DateTime, default=datetime.utcnow)

    # Relationship
    image = relationship("Image", back_populates="detections")


class Analysis(Base):
    """Model for storing analysis results and queries."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))

    # Query information
    query_text = Column(Text)  # Original user query
    query_type = Column(String)  # e.g., "count", "identify", "classify"

    # Results
    result = Column(JSON)  # Flexible JSON storage for various result types

    analysis_date = Column(DateTime, default=datetime.utcnow)

    # Relationship
    image = relationship("Image", back_populates="analyses")
