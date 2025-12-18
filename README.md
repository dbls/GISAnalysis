# GIS Satellite Analysis Application

AI-powered satellite and aerial imagery analysis system with natural language query capabilities.

## Overview

This application analyzes satellite/aerial imagery using computer vision (YOLOv8) and natural language processing (Claude AI) to enable intuitive querying of geospatial data. Users can upload GeoTIFF images, ask questions in plain English (e.g., "number of cars"), and receive instant AI-powered analysis.

## Features

- **Image Upload & Management**: Upload GeoTIFF and other geospatial image formats
- **Geospatial Metadata Extraction**: Automatically extract CRS, bounds, resolution, and other GIS metadata
- **Object Detection**: YOLOv8-based detection for vehicles, buildings, and 80+ object classes
- **Natural Language Queries**: Ask questions in plain English using Claude AI
- **Geographic Coordinates**: Convert detected objects to lat/lon coordinates
- **Results Caching**: Store and retrieve previous analyses
- **REST API**: Full API for programmatic access
- **React Frontend**: Clean, modern UI for demo purposes

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Rasterio/GDAL**: Geospatial data processing
- **YOLOv8 (Ultralytics)**: Object detection
- **Claude API (Anthropic)**: Natural language understanding
- **SQLAlchemy + SQLite**: Database and ORM

### Frontend
- **React**: UI framework
- **Axios**: HTTP client

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Database models
│   │   ├── database.py          # Database configuration
│   │   ├── gis.py               # GeoTIFF metadata extraction
│   │   ├── detection.py         # YOLOv8 object detection
│   │   └── claude_query.py      # Claude API integration
│   ├── uploads/                 # Uploaded images
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   └── App.css             # Styles
│   ├── public/
│   └── package.json            # Node dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- GDAL library (system dependency)
- Anthropic API key

### Backend Setup

1. **Install GDAL** (required for geospatial processing):

   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install gdal-bin libgdal-dev python3-gdal

   # macOS
   brew install gdal

   # Verify installation
   gdalinfo --version
   ```

2. **Create virtual environment and install dependencies**:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key:
   # ANTHROPIC_API_KEY=your_key_here
   ```

4. **Run the backend**:

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**:

   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:

   ```bash
   npm start
   ```

   Frontend will open at `http://localhost:3000`

## Cloud Deployment

### Deploy to DigitalOcean Droplet (Recommended)

Deploy to your own VPS with full control:

**Quick Start**:
1. Create Ubuntu 22.04 droplet ($12/month)
2. Run automated setup script
3. Configure domain and SSL
4. Deploy application

**Cost**: ~$12-15/month | **Setup time**: 15-20 minutes

**Full guide**: See [DIGITALOCEAN_DEPLOYMENT.md](./DIGITALOCEAN_DEPLOYMENT.md) for complete step-by-step instructions.

### Alternative: Deploy to Railway (PaaS)

Quick deployment without server management:

**Quick Start**:
1. Sign up at https://railway.app
2. Deploy from GitHub
3. Add PostgreSQL database
4. Set environment variables

**Cost**: $5 credit/month (free tier) | **Setup time**: 5-10 minutes

**Full guide**: See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

### Other Platforms

The application is ready for:
- **Render.com**: Similar to Railway, free tier available
- **Google Cloud Run**: Serverless, pay-per-use
- **AWS Elastic Beanstalk**: Enterprise-grade AWS deployment
- **DigitalOcean App Platform**: PaaS alternative to droplet

All platforms require:
- PostgreSQL database
- GDAL support (via Docker)
- Anthropic API key

## Usage

### 1. Upload Image

- Click "Upload Image" section
- Select a GeoTIFF file (recommended: 0.3-1m resolution)
- Click "Upload Image" button
- Metadata will be automatically extracted and stored

### 2. Query the Image

- Select an uploaded image from the list
- Type a natural language query in the text box:
  - "number of cars"
  - "how many vehicles"
  - "count trucks"
  - "what's the resolution"
- Press Enter or click "Analyze"
- View AI-generated response and detection details

### 3. API Access

Access the API directly at `http://localhost:8000`:

- `GET /`: API information
- `POST /api/images/upload`: Upload image
- `GET /api/images`: List all images
- `GET /api/images/{id}`: Get image details
- `POST /api/query`: Process natural language query
- `GET /api/detections/{image_id}`: Get detections for an image
- `GET /api/supported-classes`: List detectable object classes

API documentation: `http://localhost:8000/docs`

## Finding Sample Imagery

For testing with 1m resolution imagery:

### Option 1: USGS Earth Explorer
1. Visit https://earthexplorer.usgs.gov/
2. Search for location
3. Select "Aerial Imagery" → NAIP (National Agriculture Imagery Program)
4. Download GeoTIFF files (1m resolution)

### Option 2: Public Datasets
- **xView Dataset**: http://xviewdataset.org/ (satellite imagery with labeled objects)
- **DOTA Dataset**: https://captain-whu.github.io/DOTA/ (aerial object detection)
- **SpaceNet**: https://spacenet.ai/ (various satellite imagery challenges)

### Option 3: Sample Tiles
Download pre-processed sample tiles from research repositories or use synthetic test data.

## Supported Object Classes

The system uses YOLOv8 trained on COCO dataset, supporting 80 classes including:

**Vehicles**: car, truck, bus, motorcycle, bicycle, airplane, boat, train

**Infrastructure**: traffic light, fire hydrant, stop sign, parking meter, bench

**People & Animals**: person, bird, cat, dog, horse, sheep, cow, etc.

**Objects**: backpack, umbrella, handbag, suitcase, sports equipment, furniture, etc.

Full list available via API: `GET /api/supported-classes`

## Example Queries

- "number of cars"
- "how many vehicles are there"
- "count the trucks"
- "how many airplanes"
- "what is the image resolution"
- "show me the coordinate system"
- "what are the image bounds"

## Architecture

### Data Flow

1. **Upload**: User uploads GeoTIFF → Backend extracts metadata → Stores in database
2. **Query**: User asks question → Claude parses intent → Backend runs detection if needed → Results returned
3. **Caching**: Detections saved to database with geographic coordinates for future queries

### Geographic Coordinate Conversion

- Detections are made in pixel coordinates
- Backend uses Rasterio to convert pixel → lat/lon
- Each detection stored with both pixel bbox and geographic coordinates

## Future Enhancements

- Custom model training for specialized objects
- Multi-cloud deployment (AWS, Azure, GCP)
- Advanced analytics (change detection, time series)
- Support for additional image formats
- Batch processing capabilities
- User authentication and multi-tenancy
- Visualization overlays on maps

## Troubleshooting

### GDAL Installation Issues

If you encounter GDAL errors:

```bash
# Check GDAL version
gdalinfo --version

# Set GDAL_CONFIG (if needed)
export GDAL_CONFIG=/usr/bin/gdal-config

# Reinstall rasterio with specific GDAL version
pip install rasterio --no-binary :all:
```

### Port Already in Use

If port 8000 or 3000 is already in use:

```bash
# Backend: Change port in main.py or use:
uvicorn app.main:app --port 8001

# Frontend: Create .env file with:
PORT=3001
```

### Claude API Errors

Ensure your `.env` file has a valid Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Get your key from: https://console.anthropic.com/

## License

MIT

## Contributing

This is a demo/prototype application. For production use, consider:
- Adding authentication and authorization
- Implementing rate limiting
- Using production-grade database (PostgreSQL)
- Adding comprehensive error handling
- Implementing logging and monitoring
- Securing API endpoints
- Optimizing for large-scale image processing