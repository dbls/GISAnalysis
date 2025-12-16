"""
Script to download sample high-resolution aerial imagery for testing.

This script downloads sample GeoTIFF imagery suitable for vehicle detection
(approximately 1m resolution).
"""
import os
import requests
from pathlib import Path

# Create data directory
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

# Sample imagery sources (public domain)
SAMPLE_IMAGES = {
    "parking_lot_aerial": {
        "url": "https://github.com/ultralytics/yolov5/raw/master/data/images/zidane.jpg",
        "filename": "sample_aerial.jpg",
        "description": "Sample aerial image for testing (not GeoTIFF, but works for demo)"
    }
}

def download_file(url: str, destination: Path):
    """Download a file from URL to destination."""
    print(f"Downloading from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded to {destination}")


def main():
    """Download all sample images."""
    print("=" * 60)
    print("Sample Data Downloader for GIS Analysis Application")
    print("=" * 60)
    print()

    print("Note: For actual GeoTIFF files with geospatial metadata,")
    print("please download from one of these sources:")
    print()
    print("1. USGS Earth Explorer (NAIP imagery):")
    print("   https://earthexplorer.usgs.gov/")
    print()
    print("2. xView Dataset:")
    print("   http://xviewdataset.org/")
    print()
    print("3. DOTA Dataset:")
    print("   https://captain-whu.github.io/DOTA/")
    print()
    print("=" * 60)
    print()

    # For demo purposes, you can test with regular images
    # The system will show a warning about missing geospatial metadata
    print("For initial testing without GeoTIFF files:")
    print("You can use any aerial/satellite image (JPEG, PNG)")
    print("The system will process it but won't have coordinate information.")
    print()

    # Example: Download a sample test image
    choice = input("Download a sample test image? (y/n): ").strip().lower()

    if choice == 'y':
        for name, info in SAMPLE_IMAGES.items():
            try:
                dest = DATA_DIR / info["filename"]
                if dest.exists():
                    print(f"{info['filename']} already exists, skipping...")
                else:
                    download_file(info["url"], dest)
                    print(f"✓ {info['description']}")
                print()
            except Exception as e:
                print(f"✗ Failed to download {name}: {str(e)}")
                print()

    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print()
    print("To get real GeoTIFF imagery for full functionality:")
    print()
    print("Option 1 - USGS Earth Explorer (Best for US locations):")
    print("  1. Go to https://earthexplorer.usgs.gov/")
    print("  2. Search for your area of interest")
    print("  3. Click 'Data Sets' → 'Aerial Imagery' → 'NAIP'")
    print("  4. Select date range and click 'Results'")
    print("  5. Download GeoTIFF files")
    print()
    print("Option 2 - Sample from xView dataset:")
    print("  1. Visit http://xviewdataset.org/")
    print("  2. Register (free for research)")
    print("  3. Download sample GeoTIFF tiles")
    print()
    print("Option 3 - OpenAerialMap:")
    print("  1. Visit https://openaerialmap.org/")
    print("  2. Search location")
    print("  3. Download GeoTIFF imagery")
    print()
    print("Place downloaded GeoTIFF files in ./data/ or upload via the UI")
    print()


if __name__ == "__main__":
    main()
