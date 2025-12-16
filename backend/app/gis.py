"""GIS utilities for extracting metadata from geospatial imagery."""
import rasterio
from rasterio.transform import xy
from typing import Dict, Tuple, Optional
from pathlib import Path


class GISMetadataExtractor:
    """Extract geospatial metadata from imagery files."""

    @staticmethod
    def extract_metadata(filepath: str) -> Dict:
        """
        Extract comprehensive metadata from a GeoTIFF or similar geospatial image.

        Args:
            filepath: Path to the image file

        Returns:
            Dictionary containing geospatial and image metadata
        """
        try:
            with rasterio.open(filepath) as src:
                # Get bounding box
                bounds = src.bounds

                # Get transform and calculate resolution
                transform = src.transform
                resolution = abs(transform[0])  # Pixel width in CRS units

                # Extract all metadata
                metadata = {
                    "crs": src.crs.to_string() if src.crs else None,
                    "bounds": {
                        "minx": bounds.left,
                        "miny": bounds.bottom,
                        "maxx": bounds.right,
                        "maxy": bounds.top
                    },
                    "width": src.width,
                    "height": src.height,
                    "bands": src.count,
                    "resolution": resolution,
                    "transform": list(src.transform),
                    "dtype": str(src.dtypes[0]),
                    "nodata": src.nodata,
                    "tags": src.tags(),
                }

                # Add band-specific metadata
                metadata["band_descriptions"] = [
                    src.descriptions[i] if src.descriptions[i] else f"Band {i+1}"
                    for i in range(src.count)
                ]

                return metadata

        except Exception as e:
            raise ValueError(f"Failed to extract metadata: {str(e)}")

    @staticmethod
    def pixel_to_coords(
        filepath: str,
        pixel_x: float,
        pixel_y: float
    ) -> Tuple[float, float]:
        """
        Convert pixel coordinates to geographic coordinates (longitude, latitude).

        Args:
            filepath: Path to the image file
            pixel_x: X pixel coordinate
            pixel_y: Y pixel coordinate

        Returns:
            Tuple of (longitude, latitude)
        """
        try:
            with rasterio.open(filepath) as src:
                lon, lat = xy(src.transform, pixel_y, pixel_x)
                return (lon, lat)
        except Exception as e:
            raise ValueError(f"Failed to convert coordinates: {str(e)}")

    @staticmethod
    def get_center_coords(filepath: str) -> Tuple[float, float]:
        """
        Get the geographic coordinates of the image center.

        Args:
            filepath: Path to the image file

        Returns:
            Tuple of (longitude, latitude)
        """
        try:
            with rasterio.open(filepath) as src:
                center_x = src.width / 2
                center_y = src.height / 2
                lon, lat = xy(src.transform, center_y, center_x)
                return (lon, lat)
        except Exception as e:
            raise ValueError(f"Failed to get center coordinates: {str(e)}")

    @staticmethod
    def validate_geotiff(filepath: str) -> bool:
        """
        Validate that a file is a proper GeoTIFF with coordinate information.

        Args:
            filepath: Path to the image file

        Returns:
            True if valid, raises exception otherwise
        """
        try:
            with rasterio.open(filepath) as src:
                if src.crs is None:
                    raise ValueError("Image does not have a Coordinate Reference System (CRS)")
                if src.transform is None:
                    raise ValueError("Image does not have a geotransform")
                return True
        except rasterio.errors.RasterioIOError:
            raise ValueError("File is not a valid raster image")
