"""Object detection using YOLOv8."""
from ultralytics import YOLO
from typing import List, Dict, Tuple
from pathlib import Path
import numpy as np
from PIL import Image


class ObjectDetector:
    """YOLOv8-based object detector for satellite imagery."""

    def __init__(self, model_name: str = "yolov8n.pt"):
        """
        Initialize the object detector.

        Args:
            model_name: Name of the YOLOv8 model to use (yolov8n, yolov8s, yolov8m, etc.)
        """
        self.model = YOLO(model_name)

    def detect_objects(
        self,
        image_path: str,
        confidence_threshold: float = 0.25,
        target_classes: List[str] = None
    ) -> List[Dict]:
        """
        Detect objects in an image.

        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence score for detections
            target_classes: List of class names to detect (None = all classes)

        Returns:
            List of detection dictionaries with class, confidence, and bbox info
        """
        results = self.model(image_path, conf=confidence_threshold, verbose=False)

        detections = []
        for result in results:
            boxes = result.boxes

            for i in range(len(boxes)):
                box = boxes[i]
                class_id = int(box.cls[0])
                class_name = result.names[class_id]

                # Filter by target classes if specified
                if target_classes and class_name not in target_classes:
                    continue

                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                detection = {
                    "class_name": class_name,
                    "confidence": float(box.conf[0]),
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2)
                    },
                    "center": {
                        "x": int((x1 + x2) / 2),
                        "y": int((y1 + y2) / 2)
                    }
                }
                detections.append(detection)

        return detections

    def count_objects(
        self,
        image_path: str,
        target_class: str,
        confidence_threshold: float = 0.25
    ) -> Tuple[int, List[Dict]]:
        """
        Count specific objects in an image.

        Args:
            image_path: Path to the image file
            target_class: Class name to count (e.g., "car", "truck", "person")
            confidence_threshold: Minimum confidence score

        Returns:
            Tuple of (count, list of detections)
        """
        detections = self.detect_objects(
            image_path,
            confidence_threshold=confidence_threshold,
            target_classes=[target_class]
        )
        return len(detections), detections

    def get_vehicle_count(
        self,
        image_path: str,
        confidence_threshold: float = 0.25
    ) -> Dict:
        """
        Count all types of vehicles in an image.

        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence score

        Returns:
            Dictionary with counts for each vehicle type
        """
        vehicle_classes = ["car", "truck", "bus", "motorcycle", "bicycle"]

        detections = self.detect_objects(
            image_path,
            confidence_threshold=confidence_threshold,
            target_classes=vehicle_classes
        )

        # Count by class
        counts = {cls: 0 for cls in vehicle_classes}
        for detection in detections:
            counts[detection["class_name"]] += 1

        return {
            "total_vehicles": len(detections),
            "counts_by_type": counts,
            "detections": detections
        }

    @staticmethod
    def get_supported_classes() -> List[str]:
        """
        Get list of classes that YOLO can detect.

        Returns:
            List of class names
        """
        # COCO dataset classes (YOLOv8 default)
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
            'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',
            'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
            'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
