import google.generativeai as genai
from typing import Dict, List, Any
import numpy as np
from PIL import Image
import re
import cv2
import logging
from .prompt_generator import PromptGenerator

class GeminiHandler:
    def __init__(self, api_key: str):
        """Initialize Gemini handler with API key"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.prompt_generator = PromptGenerator()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            raise ValueError(f"Gemini initialization failed: {e}")

    def _parse_response(self, response_text: str) -> Dict[str, float]:
        """Parse numerical scores from Gemini response"""
        try:
            # Extract scores using regex patterns
            patterns = {
                "visual_impact": r"Visual\s+Impact:?\s*(\d+\.?\d*)",
                "creative_execution": r"Creative\s+Execution:?\s*(\d+\.?\d*)",
                "audience_engagement": r"Audience\s+Engagement:?\s*(\d+\.?\d*)",
                "production_quality": r"Production\s+Quality:?\s*(\d+\.?\d*)",
                "brand_integration": r"Brand\s+Integration:?\s*(\d+\.?\d*)",
                "tagline_effectiveness": r"Tagline\s+Effectiveness:?\s*(\d+\.?\d*)"
            }
            
            scores = {}
            for category, pattern in patterns.items():
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    # Convert score to float and normalize to 0-1 range
                    score = float(matches[0])
                    scores[category] = min(100, max(0, score)) / 100
                else:
                    self.logger.warning(f"No score found for {category}")
                    raise ValueError(f"Missing score for {category}")
            
            # Validate that we have all required scores
            if len(scores) != len(patterns):
                raise ValueError("Not all required scores were found in the response")
            
            return scores

        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            raise

    def _extract_recommendations(self, response_text: str) -> List[str]:
        """Extract recommendations from Gemini response"""
        try:
            recommendations = []
            
            # Look for recommendations section
            sections = re.split(
                r"recommendations:|improvements:|suggestions:",
                response_text,
                flags=re.IGNORECASE
            )
            
            if len(sections) > 1:
                # Get the recommendations section
                rec_text = sections[1]
                
                # Split by bullet points or numbers
                rec_items = re.split(r'\n\s*[-•\d]+\.?\s*', rec_text)
                
                # Clean and filter recommendations
                recommendations = [
                    rec.strip() for rec in rec_items
                    if rec.strip() and len(rec.strip()) > 10
                ]
                
                # Validate recommendations
                if not recommendations:
                    raise ValueError("No valid recommendations found in response")
                
                return recommendations[:5]  # Return top 5 recommendations
            else:
                raise ValueError("No recommendations section found in response")

        except Exception as e:
            self.logger.error(f"Error extracting recommendations: {e}")
            raise

    def analyze_frames(self, frames: List[np.ndarray], product_info: Dict[str, str]) -> Dict[str, Any]:
        """Analyze frames using Gemini AI"""
        try:
            # Convert frames to PIL Images
            pil_images = []
            for frame in frames[::3]:  # Sample every third frame
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_images.append(Image.fromarray(rgb_frame))

            # Generate initial analysis prompt
            prompt = self.prompt_generator.generate_analysis_prompt(product_info)
            
            # Get response from Gemini
            response = self.model.generate_content([prompt, *pil_images])
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini")

            # Parse scores and validate
            scores = self._parse_response(response.text)
            recommendations = self._extract_recommendations(response.text)

            # Calculate score breakdown
            score_breakdown = self._calculate_score_breakdown(scores)

            # Get detailed recommendations
            improvement_prompt = self.prompt_generator.generate_improvement_prompt(scores)
            improvement_response = self.model.generate_content(improvement_prompt)
            
            if not improvement_response or not improvement_response.text:
                raise ValueError("Empty improvement response from Gemini")
                
            detailed_recommendations = self._extract_recommendations(improvement_response.text)

            return {
                "scores": scores,
                "score_calculation": score_breakdown,
                "general_recommendations": recommendations,
                "detailed_recommendations": detailed_recommendations
            }

        except Exception as e:
            self.logger.error(f"Gemini analysis error: {e}")
            raise

    def _calculate_score_breakdown(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate detailed score breakdown with weights"""
        weights = {
            "visual_impact": 0.25,
            "creative_execution": 0.20,
            "audience_engagement": 0.20,
            "production_quality": 0.15,
            "brand_integration": 0.10,
            "tagline_effectiveness": 0.10
        }
        
        weighted_scores = {}
        total_score = 0
        
        for category, score in scores.items():
            weight = weights.get(category, 0)
            weighted_score = score * weight * 100  # Convert to percentage
            weighted_scores[category] = {
                "raw_score": score * 100,
                "weight": weight * 100,
                "weighted_score": weighted_score
            }
            total_score += weighted_score
            
        return {
            "weighted_scores": weighted_scores,
            "total_ai_score": total_score,
            "weights_explanation": weights,
            "calculation_breakdown": f"Total AI Score: {total_score:.1f}% (sum of all weighted category scores)"
        }