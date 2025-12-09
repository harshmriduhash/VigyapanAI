from typing import Dict

class PromptGenerator:
    def generate_analysis_prompt(self, product_info: Dict[str, str]) -> str:
        """Generate analysis prompt for Gemini model with structured scoring format"""
        product_name = product_info.get("name", "the product")
        brand_name = product_info.get("brand", "the brand")
        target_audience = product_info.get("audience", "general audience")

        prompt = f"""Analyze these video frames for {product_name} by {brand_name}, targeting {target_audience}.

Please provide a detailed evaluation with numerical scores (0-100) in this exact format:

SCORES:
Visual Impact: [Score out of 100]
- Evaluate visual appeal and first impression
- Consider color scheme and composition

Creative Execution: [Score out of 100]
- Assess creative concept and storytelling
- Evaluate uniqueness and memorability

Audience Engagement: [Score out of 100]
- Analyze potential to capture {target_audience} attention
- Evaluate emotional connection and relevance

Production Quality: [Score out of 100]
- Assess technical execution
- Evaluate professional polish and finish

Brand Integration: [Score out of 100]
- Analyze how well {brand_name} is incorporated
- Evaluate brand message clarity

Tagline Effectiveness: [Score out of 100]
- Assess message impact and memorability
- Evaluate call-to-action strength

DETAILED ANALYSIS:
[Provide detailed analysis for each aspect above]

RECOMMENDATIONS:
1. [Specific improvement recommendation]
2. [Specific improvement recommendation]
3. [Specific improvement recommendation]
4. [Specific improvement recommendation]
5. [Specific improvement recommendation]

Please ensure all scores are provided as numerical values from 0-100."""

        return prompt

    def generate_improvement_prompt(self, scores: Dict[str, float]) -> str:
        """Generate improvement prompt based on scores with specific focus areas"""
        # Convert scores to percentages for readability
        score_percentages = {k: v * 100 for k, v in scores.items()}
        
        # Identify the three lowest scoring areas
        sorted_scores = sorted(score_percentages.items(), key=lambda x: x[1])
        lowest_scores = sorted_scores[:3]
        
        # Create focused improvement prompt
        prompt = f"""Based on the video advertisement analysis, provide specific, actionable recommendations 
for improvement, focusing on these key areas:

Current Scores:
{lowest_scores[0][0]}: {lowest_scores[0][1]:.1f}/100
{lowest_scores[1][0]}: {lowest_scores[1][1]:.1f}/100
{lowest_scores[2][0]}: {lowest_scores[2][1]:.1f}/100

Please provide:
1. Specific improvements for each low-scoring area
2. Actionable steps to implement changes
3. Examples of successful techniques
4. Potential impact of improvements
5. Priority order for implementing changes

Format your response as:
RECOMMENDATIONS:
1. [First specific recommendation]
2. [Second specific recommendation]
3. [Third specific recommendation]
4. [Fourth specific recommendation]
5. [Fifth specific recommendation]

Ensure recommendations are concrete, actionable, and directly address the lowest-scoring areas."""

        return prompt

    def generate_frame_analysis_prompt(self, frame_number: int, product_info: Dict[str, str]) -> str:
        """Generate prompt for analyzing individual frames"""
        product_name = product_info.get("name", "the product")
        brand_name = product_info.get("brand", "the brand")
        
        prompt = f"""Analyze this frame (#{frame_number}) from the {product_name} advertisement by {brand_name}.

Please evaluate:
1. Visual composition and framing
2. Color scheme and lighting
3. Product placement and visibility
4. Brand element integration
5. Message clarity and impact

Provide specific observations about what works well and what could be improved."""

        return prompt