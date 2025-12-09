# utils/validators.py
from pathlib import Path
from typing import Dict, Any
import logging

class VideoValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.mp4', '.avi', '.mov']

    def validate(self, video_path: str) -> bool:
        """Validate video file existence and format"""
        try:
            path = Path(video_path)
            if not path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not path.suffix.lower() in self.supported_formats:
                raise ValueError(f"Unsupported video format: {path.suffix}")
            return True
        except Exception as e:
            self.logger.error(f"Video validation error: {e}")
            raise

class ProductInfoValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_fields = ['product_name', 'tagline', 'brand_colors']

    def validate(self, product_info: Dict[str, str]) -> bool:
        """Validate product information completeness"""
        try:
            missing_fields = [
                field for field in self.required_fields 
                if field not in product_info
            ]
            
            # Handle missing brand_colors by setting a default value
            if 'brand_colors' not in product_info:
                product_info['brand_colors'] = '["#FFFFFF", "#000000"]'  # Default colors
            
            # Check for any missing fields after handling 'brand_colors'
            if missing_fields:
                missing_fields.remove('brand_colors')  # Remove brand_colors from missing fields list
            if missing_fields:
                raise ValueError(f"Missing required product information: {missing_fields}")
            
            return True
        except Exception as e:
            self.logger.error(f"Product info validation error: {e}")
            raise
