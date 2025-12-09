# video_analyzer/pipeline.py
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime

from .utils.validators import VideoValidator, ProductInfoValidator
from .utils.logger import setup_logger
from .analyzers.color_analyzer import ColorAnalyzer
from .analyzers.composition_analyzer import CompositionAnalyzer
from .analyzers.brand_analyzer import BrandAnalyzer
from .analyzers.product_analyzer import ProductAnalyzer
from .ai_integration.gemini_handler import GeminiHandler
from .config.scoring_criteria import SCORING_CRITERIA

class VideoAnalyzerPipeline:
    def __init__(self, api_key: str):
        """Initialize the video analyzer pipeline"""
        self.logger = setup_logger()
        self.validators = {
            'video': VideoValidator(),
            'product_info': ProductInfoValidator()
        }
        self.analyzers = {
            'color': ColorAnalyzer(),
            'composition': CompositionAnalyzer(),
            'brand': BrandAnalyzer(),
            'product': ProductAnalyzer()
        }
        self.ai_handler = GeminiHandler(api_key)
        self.scoring_criteria = SCORING_CRITERIA

    def analyze_video(self, 
                     video_path: str, 
                     product_info: Dict[str, str], 
                     sample_rate: int = 30,
                     output_dir: str = "analysis_results") -> Tuple[Dict[str, Any], str]:
        """
        Main method to analyze a video file and generate formatted report
        """
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Validation step
            self.logger.info("Validating inputs...")
            self.validators['video'].validate(video_path)
            self.validators['product_info'].validate(product_info)
            
            # Extract frames
            self.logger.info("Extracting frames...")
            frames = self._extract_frames(video_path, sample_rate)
            if not frames:
                raise ValueError("No frames could be extracted from video")
            
            # Technical analysis
            self.logger.info("Performing technical analysis...")
            technical_results = self._perform_technical_analysis(frames, product_info)
            
            # AI analysis
            self.logger.info("Performing AI analysis...")
            ai_results = self.ai_handler.analyze_frames(frames, product_info)
            
            # Combine results
            self.logger.info("Aggregating results...")
            final_results = self._aggregate_results(technical_results, ai_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(final_results)
            
            # Prepare final analysis results
            analysis_results = {
                "analysis_results": final_results,
                "recommendations": recommendations,
                "scores": self._calculate_final_scores(final_results),
                "metadata": {
                    "frames_analyzed": len(frames),
                    "sample_rate": sample_rate,
                    "filename": Path(video_path).name,
                    "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            # Generate and save formatted report
            report_path = self._save_analysis_report(analysis_results, video_path, output_dir, product_info)
            
            # Save raw results as JSON
            json_path = Path(output_dir) / f"raw_analysis_{Path(video_path).stem}.json"
            with open(json_path, 'w') as f:
                json.dump(analysis_results, f, indent=4, default=str)
            
            self.logger.info(f"Analysis complete. Report saved to {report_path}")
            return analysis_results, report_path
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {e}")
            raise

    def _extract_frames(self, video_path: str, sample_rate: int) -> List[np.ndarray]:
        """Extract frames from video at given sample rate"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % sample_rate == 0:
                frames.append(frame)
            frame_count += 1
            
        cap.release()
        return frames

    def _perform_technical_analysis(self, 
                                  frames: List[np.ndarray], 
                                  product_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Perform technical analysis on extracted frames"""
        frame_results = []
        
        for frame in frames:
            frame_analysis = {
                'color': self.analyzers['color'].analyze(frame),
                'composition': self.analyzers['composition'].analyze(frame),
                'brand': self.analyzers['brand'].analyze(frame, product_info),
                'product': self.analyzers['product'].analyze(frame)
            }
            frame_results.append(frame_analysis)
            
        return frame_results

    def _aggregate_results(self, 
                          technical_results: List[Dict[str, Any]], 
                          ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate technical and AI analysis results"""
        # Calculate averages for technical metrics
        aggregated_technical = {}
        for metric in ['color', 'composition', 'brand', 'product']:
            metric_values = [frame[metric] for frame in technical_results]
            aggregated_technical[metric] = {
                key: float(np.mean([frame[key] for frame in metric_values]))
                for key in metric_values[0].keys()
            }
        technical_score = self._calculate_technical_score(aggregated_technical)
        ai_score = float(np.mean(list(ai_results["scores"].values())))

        return {
        "technical_metrics": aggregated_technical,
        "ai_metrics": ai_results["scores"],
        "technical_score": technical_score,
        "ai_score": ai_score
        }

    def _calculate_technical_score(self, 
                                 technical_metrics: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall technical score"""
        weights = {
        'color': {
            'color_harmony': 0.15,
            'avg_saturation': 0.10,
            'avg_brightness': 0.10
        },
        'composition': {
            'balance_score': 0.10,
            'thirds_alignment': 0.10,
            'overall_composition': 0.10
        },
        'brand': {
            'brand_presence': 0.15,
            'color_compliance': 0.10
        },
        'product': {
            'focus_quality': 0.05,
            'product_prominence': 0.10,
            'clarity': 0.05
        }
        }
        total_score = 0.0
        total_weight = 0.0
    
        for category, metrics in weights.items():
            if category in technical_metrics:
                for metric, weight in metrics.items():
                    if metric in technical_metrics[category]:
                        value = technical_metrics[category][metric]
                    # Ensure the value is between 0 and 1
                        normalized_value = min(max(float(value), 0.0), 1.0)
                        total_score += normalized_value * weight
                        total_weight += weight
                
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.5  # Default score if no valid metrics
        
        return final_score

    def _calculate_final_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate final weighted scores with detailed breakdown"""
        technical_weight = 0.30
        ai_weight = 0.70
    
    # Ensure technical score is between 0 and 1
        technical_score = min(max(float(results["technical_score"]), 0.0), 1.0)
    
    # Ensure AI score is between 0 and 1
        ai_score = min(max(float(results["ai_score"]), 0.0), 1.0)
    
        # Calculate final weighted score (will be between 0 and 1)
        final_score = (technical_score * technical_weight + ai_score * ai_weight)
    
    # Convert scores to 0-100 scale for reporting
        technical_score_100 = technical_score * 100
        ai_score_100 = ai_score * 100
        final_score_100 = final_score * 100
    
    # Create detailed score breakdown
        score_breakdown = {
        "technical_score": {
            "raw_score": technical_score_100,
            "weight": technical_weight * 100,
            "weighted_contribution": technical_score * technical_weight * 100
        },
        "ai_score": {
            "raw_score": ai_score_100,
            "weight": ai_weight * 100,
            "weighted_contribution": ai_score * ai_weight * 100
        },
        "calculation_explanation": (
            f"Final Score: ({technical_score_100:.1f} × {technical_weight:.1f}) + "
            f"({ai_score_100:.1f} × {ai_weight:.1f}) = {final_score_100:.1f}"
        )
    }
    
        return {
        "technical_score": float(technical_score),
        "ai_score": float(ai_score),
        "overall_score": float(final_score),
        "score_breakdown": score_breakdown,
        "detailed_scores": {
            **results["technical_metrics"],
            "ai_evaluation": results["ai_metrics"]
        }
    }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate final recommendations based on analysis results"""
        recommendations = []
        tech_metrics = results["technical_metrics"]
        
        # Color recommendations
        if tech_metrics["color"]["color_harmony"] < 0.7:
            recommendations.append(
                "Improve color harmony by using more complementary colors"
            )
        
        # Composition recommendations    
        if tech_metrics["composition"]["balance_score"] < 0.6:
            recommendations.append(
                "Enhance visual balance by redistributing elements"
            )
            
        if tech_metrics["composition"]["thirds_alignment"] < 0.5:
            recommendations.append(
                "Better utilize the rule of thirds for key elements"
            )
            
        # Brand recommendations
        if tech_metrics["brand"]["color_compliance"] < 0.7:
            recommendations.append(
                "Increase adherence to brand color guidelines"
            )
            
        if tech_metrics["brand"]["brand_presence"] < 0.6:
            recommendations.append(
                "Strengthen brand visibility in the video"
            )
            
        # Product recommendations
        if tech_metrics["product"]["product_prominence"] < 0.6:
            recommendations.append(
                "Improve product visibility and prominence"
            )
            
        if tech_metrics["product"]["clarity"] < 0.6:
            recommendations.append(
                "Enhance product clarity and focus"
            )
        
        # Add AI-generated recommendations if available
        if "ai_metrics" in results and hasattr(results["ai_metrics"], "recommendations"):
            recommendations.extend(results["ai_metrics"]["recommendations"][:3])
        
        # Remove duplicates and limit to top 5
        return list(set(recommendations))[:5]

    def _save_analysis_report(self, 
                            analysis_results: Dict[str, Any], 
                            video_path: str,
                            output_dir: str,
                            product_info: Dict[str, str]) -> str:
        """Generate and save formatted analysis report with score calculations"""
        scores = analysis_results['scores']
        metrics = analysis_results['analysis_results']
        
        # Calculate overall score out of 100
        overall_score = min(round(scores['overall_score'] * 100), 100)
        
        report = f"""Video Advertisement Analysis Report
===========================================================================

Product: {product_info.get('name', Path(video_path).stem)}
Brand: {product_info.get('brand', 'Not specified')}
Analysis Date: {analysis_results['metadata']['analysis_date']}

Overall Score: {overall_score}/100

Score Calculation:
-----------------
Technical Score: {scores['score_breakdown']['technical_score']['raw_score']:.1f}
- Weight: {scores['score_breakdown']['technical_score']['weight']}%
- Weighted Contribution: {scores['score_breakdown']['technical_score']['weighted_contribution']:.1f}

AI Score: {scores['score_breakdown']['ai_score']['raw_score']:.1f}
- Weight: {scores['score_breakdown']['ai_score']['weight']}%
- Weighted Contribution: {scores['score_breakdown']['ai_score']['weighted_contribution']:.1f}

Final Score Calculation:
{scores['score_breakdown']['calculation_explanation']}
------------------------

Visual Impact:
Score: {int(metrics['ai_metrics']['visual_impact'] * 30)}/30
- Visual clarity and composition alignment
- Color harmony and balance
- Overall visual appeal

Creative Execution:
Score: {int(metrics['ai_metrics']['creative_execution'] * 25)}/25
- Innovation in presentation
- Storytelling effectiveness
- Brand integration quality

Audience Engagement:
Score: {int(metrics['ai_metrics']['audience_engagement'] * 25)}/25
- Target audience alignment
- Message clarity
- Call-to-action effectiveness

Production Quality:
Score: {int(metrics['ai_metrics']['production_quality'] * 20)}/20
- Technical excellence
- Smooth transitions
- Professional polish

Technical Metrics:
-----------------
Color Analysis:
- Color Harmony: {metrics['technical_metrics']['color']['color_harmony']:.2f}
- Color Saturation: {metrics['technical_metrics']['color']['avg_saturation']:.2f}
- Brightness Level: {metrics['technical_metrics']['color']['avg_brightness']:.2f}

Composition Analysis:
- Balance Score: {metrics['technical_metrics']['composition']['balance_score']:.2f}
- Rule of Thirds: {metrics['technical_metrics']['composition']['thirds_alignment']:.2f}
- Overall Composition: {metrics['technical_metrics']['composition']['overall_composition']:.2f}

Brand & Product Presence:
- Brand Visibility: {metrics['technical_metrics']['brand']['brand_presence']:.2f}
- Product Focus: {metrics['technical_metrics']['product']['focus_quality']:.2f}
- Visual Clarity: {metrics['technical_metrics']['product']['clarity']:.2f}

Key Insights:
------------
{self._format_key_insights(metrics['technical_metrics'])}

Recommendations:
---------------
{self._format_recommendations(analysis_results['recommendations'])}

Technical Specifications:
-----------------------
- Frames Analyzed: {analysis_results['metadata']['frames_analyzed']}
- Sample Rate: {analysis_results['metadata']['sample_rate']} fps
- Filename: {analysis_results['metadata']['filename']}

Note: Scores are normalized on a scale of 0-100. 
Raw analysis data saved in JSON format for further processing.
"""
        
        # Save report
        report_path = Path(output_dir) / f"analysis_report_{Path(video_path).stem}.txt"
        with open(report_path, "w") as f:
            f.write(report)
        
        # Print to console
        print("\n" + "="*50)
        print("Analysis Complete!")
        print("="*50)
        print(report)
        print(f"\nDetailed report saved to: {report_path}")
        
        return str(report_path)

    def _format_key_insights(self, metrics: Dict[str, Dict[str, float]]) -> str:
        """Format key insights based on technical metrics"""
        insights = []
        
        # Color insights
        if metrics['color']['color_harmony'] > 0.7:
            insights.append("Strong color harmony enhances visual appeal")
        elif metrics['color']['color_harmony'] < 0.4:
            insights.append("Color harmony needs improvement")
            
        # Composition insights
        if metrics['composition']['balance_score'] > 0.8:
            insights.append("Excellent visual balance and composition")
        elif metrics['composition']['balance_score'] < 0.4:
            insights.append("Visual balance needs improvement")
        
        # Brand insights
        if metrics['brand']['brand_presence'] > 0.7:
            insights.append("Strong brand presence throughout")
        elif metrics['brand']['brand_presence'] < 0.4:
            insights.append("Brand presence needs strengthening")
        
        # Product insights
        if metrics['product']['clarity'] > 0.7:
            insights.append("Clear and effective product presentation")
        elif metrics['product']['clarity'] < 0.4:
            insights.append("Product presentation needs improvement")
            
        if not insights:
            insights.append("No significant strengths or weaknesses identified")
            
        return "\n".join(f"- {insight}" for insight in insights)

    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations with proper bullet points"""
        return "\n".join(f"- {rec}" for rec in recommendations)