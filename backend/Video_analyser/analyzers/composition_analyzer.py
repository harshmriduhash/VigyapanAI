import cv2
import numpy as np
from typing import Dict, Any

class CompositionAnalyzer:
    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame composition using rule of thirds and balance"""
        try:
            height, width = frame.shape[:2]
            third_h, third_w = height // 3, width // 3
            
            # Divide frame into 9 regions
            regions = []
            for i in range(3):
                for j in range(3):
                    region = frame[
                        i*third_h:(i+1)*third_h, 
                        j*third_w:(j+1)*third_w
                    ]
                    regions.append(np.mean(region))
            
            # Calculate balance scores
            balance = self._calculate_balance(regions)
            thirds = self._calculate_thirds_alignment(regions)
            
            return {
                "balance_score": balance,
                "thirds_alignment": thirds,
                "overall_composition": (balance + thirds) / 2
            }
        except Exception as e:
            raise ValueError(f"Composition analysis failed: {e}")

    def _calculate_balance(self, regions: list) -> float:
        """Calculate visual balance score"""
        left = np.mean(regions[::3])
        right = np.mean(regions[2::3])
        top = np.mean(regions[:3])
        bottom = np.mean(regions[6:])
        
        horizontal_balance = 1 - min(abs(left - right) / 255, 1)
        vertical_balance = 1 - min(abs(top - bottom) / 255, 1)
        
        return (horizontal_balance + vertical_balance) / 2

    def _calculate_thirds_alignment(self, regions: list) -> float:
        """Calculate alignment with rule of thirds"""
        # Power points are intersections of third lines
        power_points = [regions[0], regions[2], regions[6], regions[8]]
        return np.mean(power_points) / 255