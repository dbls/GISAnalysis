"""Main FastAPI application for GIS Satellite Analysis."""
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
from pathlib import Path
import os
from datetime import datetime

from .database import get_db, init_db
from . import models
from .gis import GISMetadataExtractor
from .detection import ObjectDetector
from .claude_query import ClaudeQueryParser

# Initialize FastAPI app
app = FastAPI(
    title="GIS Satellite Analysis API",
    description="API for analyzing satellite imagery with AI-powered natural language queries",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

gis_extractor = GISMetadataExtractor()
detector = ObjectDetector()  # Will download yolov8n.pt on first run
query_parser = ClaudeQueryParser()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GIS Satellite Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/images/upload",
            "query": "/api/query",
            "images": "/api/images",
            "detections": "/api/detections"
        }
    }


@app.post("/api/images/upload")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a satellite/aerial image (GeoTIFF or similar format).

    Returns image metadata and database ID.
    """
    try:
        # Save uploaded file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = UPLOAD_DIR / filename

        with filepath.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract GIS metadata
        try:
            metadata = gis_extractor.extract_metadata(str(filepath))
        except ValueError as e:
            # Clean up file if not valid
            filepath.unlink()
            raise HTTPException(status_code=400, detail=f"Invalid GeoTIFF: {str(e)}")

        # Store in database
        db_image = models.Image(
            filename=filename,
            filepath=str(filepath),
            crs=metadata["crs"],
            bounds_minx=metadata["bounds"]["minx"],
            bounds_miny=metadata["bounds"]["miny"],
            bounds_maxx=metadata["bounds"]["maxx"],
            bounds_maxy=metadata["bounds"]["maxy"],
            width=metadata["width"],
            height=metadata["height"],
            bands=metadata["bands"],
            resolution=metadata["resolution"],
            raw_metadata=metadata
        )

        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return {
            "id": db_image.id,
            "filename": filename,
            "metadata": metadata,
            "message": "Image uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/images")
async def list_images(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all uploaded images."""
    images = db.query(models.Image).offset(skip).limit(limit).all()

    return {
        "count": len(images),
        "images": [
            {
                "id": img.id,
                "filename": img.filename,
                "upload_date": img.upload_date,
                "resolution": img.resolution,
                "size": f"{img.width}x{img.height}",
                "crs": img.crs
            }
            for img in images
        ]
    }


@app.get("/api/images/{image_id}")
async def get_image_details(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific image."""
    image = db.query(models.Image).filter(models.Image.id == image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get detection counts
    detections = db.query(models.Detection).filter(
        models.Detection.image_id == image_id
    ).all()

    detection_summary = {}
    for det in detections:
        detection_summary[det.class_name] = detection_summary.get(det.class_name, 0) + 1

    return {
        "id": image.id,
        "filename": image.filename,
        "upload_date": image.upload_date,
        "metadata": image.raw_metadata,
        "bounds": {
            "minx": image.bounds_minx,
            "miny": image.bounds_miny,
            "maxx": image.bounds_maxx,
            "maxy": image.bounds_maxy
        },
        "detections_summary": detection_summary
    }


@app.post("/api/query")
async def process_query(
    query: str = Query(..., description="Natural language query"),
    image_id: int = Query(..., description="Image ID to query"),
    db: Session = Depends(get_db)
):
    """
    Process a natural language query about an image.

    Examples:
    - "number of cars"
    - "how many vehicles"
    - "count trucks"
    - "what's the resolution"
    """
    # Get image
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Parse query with Claude
        parsed_query = query_parser.parse_query(
            query,
            available_metadata=image.raw_metadata
        )

        result = {}

        # Handle different query types
        if parsed_query.get("query_type") == "count":
            target_object = parsed_query.get("target_object", "car")

            # Check if we already have this analysis
            existing_analysis = db.query(models.Analysis).filter(
                models.Analysis.image_id == image_id,
                models.Analysis.query_type == "count",
                models.Analysis.query_text.like(f"%{target_object}%")
            ).first()

            if existing_analysis:
                # Return cached result
                result = existing_analysis.result
                result["from_cache"] = True
            else:
                # Perform new detection
                count, detections = detector.count_objects(
                    image.filepath,
                    target_object
                )

                # Save detections to database
                for det in detections:
                    # Convert pixel coords to lat/lon
                    lon, lat = gis_extractor.pixel_to_coords(
                        image.filepath,
                        det["center"]["x"],
                        det["center"]["y"]
                    )

                    db_detection = models.Detection(
                        image_id=image_id,
                        class_name=det["class_name"],
                        confidence=det["confidence"],
                        bbox_x1=det["bbox"]["x1"],
                        bbox_y1=det["bbox"]["y1"],
                        bbox_x2=det["bbox"]["x2"],
                        bbox_y2=det["bbox"]["y2"],
                        latitude=lat,
                        longitude=lon
                    )
                    db.add(db_detection)

                result = {
                    "count": count,
                    "object_type": target_object,
                    "detections": detections,
                    "from_cache": False
                }

                # Save analysis
                db_analysis = models.Analysis(
                    image_id=image_id,
                    query_text=query,
                    query_type="count",
                    result=result
                )
                db.add(db_analysis)
                db.commit()

        elif parsed_query.get("query_type") == "metadata":
            # Return metadata
            field = parsed_query.get("field")
            if field:
                result = {field: image.raw_metadata.get(field)}
            else:
                result = image.raw_metadata

        else:
            # Unknown query type
            result = {
                "message": "Query type not recognized",
                "parsed_query": parsed_query
            }

        # Generate natural language response
        nl_response = query_parser.generate_response(query, result)

        return {
            "query": query,
            "parsed_query": parsed_query,
            "result": result,
            "response": nl_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/detections/{image_id}")
async def get_detections(
    image_id: int,
    class_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all detections for an image, optionally filtered by class."""
    query_obj = db.query(models.Detection).filter(
        models.Detection.image_id == image_id
    )

    if class_name:
        query_obj = query_obj.filter(models.Detection.class_name == class_name)

    detections = query_obj.all()

    return {
        "image_id": image_id,
        "count": len(detections),
        "detections": [
            {
                "id": det.id,
                "class_name": det.class_name,
                "confidence": det.confidence,
                "bbox": {
                    "x1": det.bbox_x1,
                    "y1": det.bbox_y1,
                    "x2": det.bbox_x2,
                    "y2": det.bbox_y2
                },
                "coordinates": {
                    "latitude": det.latitude,
                    "longitude": det.longitude
                }
            }
            for det in detections
        ]
    }


@app.get("/api/supported-classes")
async def get_supported_classes():
    """Get list of object classes that can be detected."""
    return {
        "classes": ObjectDetector.get_supported_classes(),
        "recommended_for_satellite": [
            "car", "truck", "bus", "airplane", "boat", "person",
            "bicycle", "motorcycle", "train"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
