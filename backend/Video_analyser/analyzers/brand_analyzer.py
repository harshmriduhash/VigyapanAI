import cv2
import numpy as np
from typing import Dict, Any
import ast  # Importing ast to safely evaluate the list string

class BrandAnalyzer:
    def analyze(self, frame: np.ndarray, product_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze brand presence and consistency in a given frame.
        
        Args:
            frame (np.ndarray): The video frame in BGR format.
            product_info (Dict[str, str]): Product information containing brand colors and other details.
        
        Returns:
            Dict[str, Any]: Analysis results including brand presence score, color compliance score, 
                            and overall brand score.
        """
        try:
            # Convert frame to different color spaces for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Detect potential brand elements
            brand_presence = self._detect_brand_elements(edges)
            
            # Parse and check color compliance
            brand_colors = self._parse_brand_colors(product_info.get('brand_colors', '[]'))
            color_compliance = self._check_color_compliance(
                frame, 
                brand_colors
            )
            
            # Compute overall brand score
            overall_score = (brand_presence + color_compliance) / 2
            
            return {
                "brand_presence": brand_presence,
                "color_compliance": color_compliance,
                "overall_brand_score": overall_score
            }
        except Exception as e:
            raise ValueError(f"Brand analysis failed: {e}")

    def _parse_brand_colors(self, brand_colors_str: str) -> list:
        """
        Parse the brand colors string into a list. If not provided, use general colors.
        
        Args:
            brand_colors_str (str): The brand colors string (e.g., '[#FFFFFF, #000000]').
        
        Returns:
            list: A list of brand colors as strings (e.g., ['#FFFFFF', '#000000']).
        """
        try:
            # Use ast.literal_eval to safely evaluate the string as a list
            brand_colors = ast.literal_eval(brand_colors_str)
            if not isinstance(brand_colors, list):
                raise ValueError("Brand colors should be a list.")
            
            # If the list is empty or None, use default colors
            if not brand_colors:
                return self._get_default_brand_colors()
            return brand_colors
        except (ValueError, SyntaxError):
            # Return default colors in case of an error or invalid format
            return self._get_default_brand_colors()

    def _get_default_brand_colors(self) -> list:
        """
        Returns default general brand colors if no brand colors are provided.
        
        Returns:
            list: A list of general colors as strings (e.g., ['#FFFFFF', '#000000']).
        """
        # Default general colors (white and black as neutral options)
        return ['#FFFFFF', '#000000']

    def _detect_brand_elements(self, edges: np.ndarray) -> float:
        """
        Detect potential brand elements using edge detection and contour analysis.
        
        Args:
            edges (np.ndarray): Edge-detected frame.
        
        Returns:
            float: A score representing the presence of brand elements.
        """
        # Find contours from the edge-detected frame
        contours, _ = cv2.findContours(
            edges, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # If no contours are found, return a default neutral score
        if not contours:
            return 0.5
        
        # Analyze contour characteristics
        scores = []
        total_area = edges.shape[0] * edges.shape[1]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < total_area * 0.01:  # Ignore small contours
                continue
            
            # Calculate contour complexity
            perimeter = cv2.arcLength(contour, True)
            complexity = (perimeter ** 2) / (4 * np.pi * area)  # Circularity measure
            scores.append(1 - min(complexity / 10, 1))  # Normalize complexity score
        
        # Return the average score of detected brand elements
        return np.mean(scores) if scores else 0.5

    def _check_color_compliance(self, frame: np.ndarray, brand_colors: list) -> float:
        """
        Check if the frame's dominant colors comply with brand colors.
        
        Args:
            frame (np.ndarray): The video frame in BGR format.
            brand_colors (list): List of brand colors in hex format (e.g., ['#FFFFFF', '#000000']).
        
        Returns:
            float: A score representing how compliant the frame's colors are with the brand colors.
        """
        if not brand_colors:
            # If no brand colors are provided, return a neutral score
            return 0.5
        
        # Convert frame colors to RGB format and flatten into a list of pixels
        frame_colors = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).reshape(-1, 3)
        
        # Convert brand colors from hex to RGB format
        brand_rgb = [
            [int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
            for color in brand_colors
        ]
        
        # Calculate color distances between frame pixels and each brand color
        compliance_scores = []
        for brand_color in brand_rgb:
            distances = np.linalg.norm(frame_colors - brand_color, axis=1)  # Euclidean distance
            compliance_scores.append(np.mean(distances))
        
        # Normalize the compliance score
        avg_distance = np.mean(compliance_scores)
        return 1 - min(avg_distance / 255, 1)  # Normalize and cap at 1.0
