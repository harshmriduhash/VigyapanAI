import cv2
import numpy as np
from typing import Dict, Any

class ProductAnalyzer:
    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze product focus and prominence"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect edges for product boundaries
            edges = cv2.Canny(blurred, 50, 150)
            
            # Analyze focus metrics
            focus_metrics = self._analyze_focus(gray)
            
            # Analyze product prominence
            prominence = self._analyze_prominence(edges)
            
            return {
                "focus_quality": focus_metrics["focus_score"],
                "product_prominence": prominence,
                "clarity": focus_metrics["clarity"],
                "overall_product_score": (
                    focus_metrics["focus_score"] + 
                    prominence + 
                    focus_metrics["clarity"]
                ) / 3
            }
        except Exception as e:
            raise ValueError(f"Product analysis failed: {e}")

    def _analyze_focus(self, gray_frame: np.ndarray) -> Dict[str, float]:
        """Analyze focus quality using Laplacian variance"""
        laplacian = cv2.Laplacian(gray_frame, cv2.CV_64F)
        focus_score = np.var(laplacian) / 10000  # Normalize
        
        # Calculate local contrast
        local_contrast = cv2.equalizeHist(gray_frame)
        clarity = np.std(local_contrast) / 128  # Normalize
        
        return {
            "focus_score": min(focus_score, 1.0),
            "clarity": min(clarity, 1.0)
        }

    def _analyze_prominence(self, edges: np.ndarray) -> float:
        """Analyze product prominence using edge density"""
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_pixels = np.count_nonzero(edges)
        
        # Calculate edge density
        edge_density = edge_pixels / total_pixels
        
        # Normalize score
        return min(edge_density * 10, 1.0)