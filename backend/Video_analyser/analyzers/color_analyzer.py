import cv2
import numpy as np
from typing import Dict, Any
from sklearn.cluster import KMeans
import colorsys

class ColorAnalyzer:
    def __init__(self):
        self.n_colors = 5

    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze color palette and harmony of a frame"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pixels = rgb_frame.reshape(-1, 3)
            
            kmeans = KMeans(n_clusters=self.n_colors, random_state=42)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_
            
            # Convert to HSV for harmony analysis
            hsv_colors = []
            for color in colors:
                hsv = colorsys.rgb_to_hsv(
                    color[0]/255, color[1]/255, color[2]/255
                )
                hsv_colors.append(hsv)
            
            harmony_score = self._calculate_harmony(hsv_colors)
            
            return {
                "dominant_colors": colors.tolist(),
                "color_harmony": harmony_score,
                "avg_saturation": np.mean([c[1] for c in hsv_colors]),
                "avg_brightness": np.mean([c[2] for c in hsv_colors])
            }
        except Exception as e:
            raise ValueError(f"Color analysis failed: {e}")

    def _calculate_harmony(self, hsv_colors: list) -> float:
        """Calculate color harmony score"""
        if not hsv_colors:
            return 0.5

        harmony_scores = []
        
        # Check complementary colors
        for i, color1 in enumerate(hsv_colors):
            for j, color2 in enumerate(hsv_colors[i+1:]):
                # Calculate hue difference
                hue_diff = abs(color1[0] - color2[0])
                if hue_diff > 0.5:
                    hue_diff = 1 - hue_diff
                    
                # Score based on complementary relationship
                harmony_scores.append(1 - (2 * hue_diff))

        return np.mean(harmony_scores) if harmony_scores else 0.5