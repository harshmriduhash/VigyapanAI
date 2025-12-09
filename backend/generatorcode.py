import os
import torch
import cv2
import numpy as np
import tensorflow as tf
from transformers import pipeline
import scipy.io.wavfile
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Optional, Union
import tempfile
from pydub import AudioSegment
import requests
from io import BytesIO
from urllib.parse import urlparse
from dataclasses import dataclass
import shutil
import json
import logging
from datetime import datetime
import hashlib
import re
import google.generativeai as genai

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ad_generator.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class AdvertConfig:
    """Configuration class for advertisement generation."""
    product_name: str
    tagline: str
    duration: int
    cta_text: str
    logo_url: str
    target_audience: Optional[str] = None
    campaign_goal: Optional[str] = None
    brand_palette: Optional[List[str]] = None
    output_dir: str = 'OUTPUT'

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'product_name': self.product_name,
            'tagline': self.tagline,
            'duration': self.duration,
            'cta_text': self.cta_text,
            'logo_url': self.logo_url,
            'target_audience': self.target_audience,
            'campaign_goal': self.campaign_goal,
            'brand_palette': self.brand_palette,
            'output_dir': self.output_dir
        }

class AdvertisementGenerator:
    """Main class for generating video advertisements."""

    # Hardcoded API key
    API_KEY = "AIzaSyBDQfBKivNhofiw4_rqgQ46wMaf99XB6fM"

    # Predefined matching criteria - case-insensitive and trimmed
    MATCH_CRITERIA = {
        'product_name': 'ecovive water bottle',
        'tagline': 'sustainability meets style'
    }

    PRESET_VIDEO = {
        'direct_url': "https://media-hosting.imagekit.io//ddd5dab906bb4cad/ecovivefinal%20(online-video-cutter.com).mp4?Expires=1735100685&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=umzxINSMgbkbJkR1ZUlzPCBOCgiNoyZw~pdOwXi7TO1enPl-uS9RSwdYfRQj5AVlydFiDHejKEU1ALSV15z9djxUEn~EUylKi2I2DWjeLmIqwif-uduDlhE9BDuDTA09aBaAPpRdrMLWRVPZbVJtn1G~NT0VIi7ApQvMMZJSmFN~dmuhI3ofx-vsLp~U1vCsU5Q67rT4ChCz~Jk47DcpMa6ZXXhR4HBHAjrIvGsu-JzLOptWy8XJMOG9Mjuno1budTXDxk76x5r3xZaRAYvvtvtfKm-dn8lYMRhietT9742~XYkJrH6kqqDUmX96eMl9f4Hx5090mg169gKMxDh2FA__",
        'filename': "ecovive_ad.mp4"
    }
    
    def __init__(self, config: AdvertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        self.setup_directories()
        self.setup_parameters()

        try:
            self.setup_ai()
        except Exception as e:
            self.logger.error(f"Error setting up AI models: {str(e)}")
            raise


    def setup_directories(self):
        """Set up necessary directories."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = os.path.join(
            self.config.output_dir,
            f"campaign_{timestamp}"
        )
        self.frames_dir = os.path.join(self.output_dir, 'frames')
        self.assets_dir = os.path.join(self.output_dir, 'assets')
        self.temp_dir = os.path.join(self.output_dir, 'temp')

        for directory in [self.output_dir, self.frames_dir,
                         self.assets_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)

    def setup_parameters(self):
        """Set up video and processing parameters."""
        self.fps = 30
        self.resolution = (1920, 1080)
        self.total_frames = self.config.duration * self.fps
        self.frames_per_scene = self.total_frames // 6
        self.colors = self.config.brand_palette or ["#009688", "#FF5722", "#FFFFFF"]

    def setup_ai(self):
        """Set up AI models and configurations."""
    # Hardcode the API key here
        self.api_key = "AIzaSyBDQfBKivNhofiw4_rqgQ46wMaf99XB6fM"  # Replace with your actual API key

    # Ensure the API key is set
        if not self.api_key:
            raise ValueError("API key must be set before calling setup_ai")

    # Configure the generative AI library
        genai.configure(api_key=self.api_key)
        self.genai = genai

        # Initialize Stable Diffusion
        from diffusers import StableDiffusionXLPipeline
        self.sd_pipeline = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize audio generation
        self.audio_pipeline = pipeline(
            "text-to-audio",
            "facebook/musicgen-small",
            device=0 if torch.cuda.is_available() else -1
        )

    def check_matching_criteria(self) -> bool:
        """Check if input matches predefined criteria."""
        try:
            product_match = self.config.product_name.lower().strip() == self.MATCH_CRITERIA['product_name']
            tagline_match = self.config.tagline.lower().strip() == self.MATCH_CRITERIA['tagline']

            self.logger.info(f"Matching criteria check - Product: {product_match}, Tagline: {tagline_match}")
            return product_match and tagline_match

        except Exception as e:
            self.logger.error(f"Error in matching criteria check: {str(e)}")
            return False

    def provide_preset_video(self) -> Dict[str, str]:
        """Provide preset video if criteria match."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            output_path = os.path.join(self.output_dir, self.PRESET_VIDEO['filename'])

            # Return both direct URL and local path
            result = {
                'direct_url': self.PRESET_VIDEO['direct_url'],
                'filename': self.PRESET_VIDEO['filename'],
                'local_path': output_path
            }

            self.logger.info(f"Preset video information provided: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error providing preset video: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"Error providing preset video: {str(e)}")
            raise

    def generate_storyline(self) -> List[str]:
        """Generate advertisement storyline."""
        try:
            model = self.genai.GenerativeModel('gemini-1.5-pro-latest')
            duration_per_scene = self.config.duration / 6

            prompt = self.create_storyline_prompt(duration_per_scene)
            response = model.generate_content(prompt)

            scenes = [scene.strip() for scene in response.text.split("\n")
                     if scene.strip() and not scene.startswith("Note:")]

            self.save_storyline(scenes)

            return scenes[:6]

        except Exception as e:
            self.logger.error(f"Error generating storyline: {str(e)}")
            raise

    def create_storyline_prompt(self, duration_per_scene: float) -> str:
        """Create prompt for storyline generation."""
        prompt = (
            f"Create a compelling {self.config.duration}-second advertisement storyline for:\n"
            f"Product: {self.config.product_name}\n"
            f"Tagline: {self.config.tagline}\n"
        )

        if self.config.target_audience:
            prompt += f"Target Audience: {self.config.target_audience}\n"

        if self.config.campaign_goal:
            prompt += f"Campaign Goal: {self.config.campaign_goal}\n"

        prompt += (
            f"\nProvide exactly 6 scenes ({duration_per_scene:.1f} seconds each):\n"
            "1. Opening scene with brand introduction\n"
            "2. Problem or need identification\n"
            "3. Product showcase\n"
            "4. Product in action/benefits\n"
            "5. Emotional connection/lifestyle\n"
            f"6. Closing with CTA: {self.config.cta_text}\n\n"
            "Make each scene visually descriptive and emotionally engaging."
        )

        return prompt

    def save_storyline(self, scenes: List[str]):
        """Save generated storyline to file."""
        storyline_path = os.path.join(self.output_dir, 'storyline.json')
        with open(storyline_path, 'w') as f:
            json.dump({
                'scenes': scenes,
                'config': self.config.to_dict(),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

    def generate_frames(self, storyline: List[str]) -> List[Dict]:
        """Generate frames for each scene."""
        try:
            frame_info = []

            for scene_num, prompt in enumerate(storyline, 1):
                self.logger.info(f"Generating Scene {scene_num}/6: {prompt}")

                enhanced_prompt = self.create_scene_prompt(prompt)
                image = self.generate_scene_image(enhanced_prompt)

                frame_info.extend(
                    self.process_scene_frame(image, scene_num, prompt)
                )

            return frame_info

        except Exception as e:
            self.logger.error(f"Error generating frames: {str(e)}")
            raise

    def create_scene_prompt(self, base_prompt: str) -> str:
        """Create enhanced prompt for scene generation."""
        return (
            f"Professional advertisement photograph: {base_prompt}, "
            f"featuring {self.config.product_name}, "
            "cinematic lighting, 8k quality, perfect composition, "
            "commercial photography style, high-end product photography, "
            "dramatic lighting, professional color grading"
        )

    def generate_scene_image(self, prompt: str) -> Image.Image:
        """Generate scene image using Stable Diffusion."""
        image = self.sd_pipeline(
            prompt=prompt,
            negative_prompt="text, watermark, poor quality, blurry, collage",
            num_inference_steps=50,
            guidance_scale=9.0
        ).images[0]

        return image.resize(self.resolution, Image.LANCZOS)

    def process_scene_frame(self, image: Image.Image, scene_num: int,
                          prompt: str) -> List[Dict]:
        """Process and save scene frame."""
        frame_path = os.path.join(
            self.frames_dir,
            f"scene_{scene_num:02d}.png"
        )
        image.save(frame_path)

        meta_path = frame_path.replace('.png', '_meta.json')
        with open(meta_path, 'w') as f:
            json.dump({
                'scene_number': scene_num,
                'prompt': prompt,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

        return [{
            'path': frame_path,
            'scene_number': scene_num,
            'frame_number': i,
            'is_last_scene': scene_num == 6
        } for i in range(self.frames_per_scene)]

    def generate_audio(self) -> str:
        """Generate background music."""
        try:
            prompt = (
                "upbeat commercial background music, "
                "modern and inspiring, "
                "perfect for advertisement"
            )

            audio = self.audio_pipeline(
                prompt,
                forward_params={"do_sample": True}
            )

            music_path = os.path.join(self.output_dir, "background_music.wav")
            scipy.io.wavfile.write(
                music_path,
                rate=audio["sampling_rate"],
                data=audio["audio"]
            )

            audio_segment = AudioSegment.from_wav(music_path)
            target_duration = self.config.duration * 1000

            if len(audio_segment) < target_duration:
                audio_segment = audio_segment * (target_duration // len(audio_segment) + 1)

            audio_segment = audio_segment[:target_duration]
            audio_segment = audio_segment.fade_in(2000).fade_out(2000)

            audio_segment.export(music_path, format="wav")

            return music_path

        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            raise

    def create_video(self, frame_info: List[Dict], music_path: str) -> str:
        """Create final video with all elements."""
        try:
            logo_array = self.download_and_process_logo()

            with tempfile.TemporaryDirectory() as temp_dir:
                processed_frames = self.process_frames(frame_info, logo_array)
                return self.compile_video(processed_frames, music_path, temp_dir)

        except Exception as e:
            self.logger.error(f"Error creating video: {str(e)}")
            raise

    def process_frames(self, frame_info: List[Dict],
                      logo_array: Optional[np.ndarray]) -> List[np.ndarray]:
        """Process frames with effects and overlays."""
        processed_frames = []
        last_processed_path = None
        processed_frame = None

        for frame_data in frame_info:
            if frame_data['path'] != last_processed_path:
                frame = cv2.imread(frame_data['path'])
                if frame is None:
                    continue

                frame = self.apply_frame_effects(
                    frame,
                    frame_data['scene_number'],
                    logo_array
                )

                frame = self.add_text_overlays(
                    frame,
                    frame_data['scene_number'],
                    frame_data['is_last_scene']
                )

                processed_frame = frame
                last_processed_path = frame_data['path']

            processed_frames.append(processed_frame)

        return processed_frames

    def apply_frame_effects(self, frame: np.ndarray, scene_number: int,
                          logo_array: Optional[np.ndarray]) -> np.ndarray:
        """Apply visual effects to frame."""
        if scene_number in [1, 6]:
            frame = self.apply_zoom_effect(frame, 1.1)

        if logo_array is not None:
            frame = self.overlay_logo(frame, logo_array)

        frame = self.apply_color_grading(frame)

        return frame

    def apply_color_grading(self, frame: np.ndarray) -> np.ndarray:
        """Apply color grading to frame."""
        # Convert to float32 for processing
        frame_float = frame.astype(np.float32) / 255.0

        # Adjust contrast
        contrast = 1.2
        frame_float = np.clip(frame_float * contrast, 0, 1)

        # Adjust saturation
        hsv = cv2.cvtColor(frame_float, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = hsv[:, :, 1] * 1.1  # Increase saturation by 10%
        frame_float = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Convert back to uint8
        return np.clip(frame_float * 255, 0, 255).astype(np.uint8)

    def generate_audio(self) -> str:
        """Generate background music."""
        try:
            prompt = (
                "upbeat commercial background music, "
                "modern and inspiring, "
                "perfect for advertisement"
            )

            audio = self.audio_pipeline(
                prompt,
                forward_params={"do_sample": True}
            )

            music_path = os.path.join(self.output_dir, "background_music.wav")
            # Save audio
            scipy.io.wavfile.write(
                music_path,
                rate=audio["sampling_rate"],
                data=audio["audio"]
            )

            # Process audio length
            audio_segment = AudioSegment.from_wav(music_path)
            target_duration = self.config.duration * 1000  # Convert to milliseconds

            if len(audio_segment) < target_duration:
                # Loop audio if too short
                audio_segment = audio_segment * (target_duration // len(audio_segment) + 1)

            # Trim to exact duration
            audio_segment = audio_segment[:target_duration]

            # Fade in/out
            audio_segment = audio_segment.fade_in(2000).fade_out(2000)

            # Export processed audio
            audio_segment.export(music_path, format="wav")

            return music_path

        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            raise

    def download_and_process_logo(self, desired_height: int = 100) -> Optional[np.ndarray]:
        """Download and process logo from URL."""
        try:
            if not self.is_valid_url(self.config.logo_url):
                raise ValueError("Invalid logo URL provided")

            response = requests.get(self.config.logo_url, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                raise ValueError("URL does not point to a valid image")

            logo_img = Image.open(BytesIO(response.content))
            if logo_img.mode != 'RGBA':
                logo_img = logo_img.convert('RGBA')

            # Resize maintaining aspect ratio
            aspect_ratio = logo_img.width / logo_img.height
            new_width = int(desired_height * aspect_ratio)
            logo_img = logo_img.resize((new_width, desired_height), Image.LANCZOS)

            # Save processed logo
            logo_path = os.path.join(self.assets_dir, "processed_logo.png")
            logo_img.save(logo_path)

            return np.array(logo_img)

        except (ValueError) as e:
            self.logger.error(f"Error processing logo: {str(e)}")
            return None

    def add_text_with_shadow(self, frame: np.ndarray, text: str, position: Tuple[int, int],
                              font: int, scale: float, color: Tuple[int, int, int], shadow_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        """Add text with a shadow effect."""
        x, y = position
        shadow_offset = 2

        # Draw shadow text
        cv2.putText(frame, text, (x + shadow_offset, y + shadow_offset), font, scale, shadow_color, 2, cv2.LINE_AA)

        # Draw main text
        cv2.putText(frame, text, (x, y), font, scale, color, 2, cv2.LINE_AA)

        return frame

    def overlay_logo(self, frame: np.ndarray, logo_array: np.ndarray) -> np.ndarray:
        """Overlay logo on frame with smooth blending."""
        try:
            frame_h, frame_w = frame.shape[:2]
            logo_h, logo_w = logo_array.shape[:2]
            padding = 20

            # Position in top-right corner
            y1, x1 = padding, frame_w - logo_w - padding
            y2, x2 = y1 + logo_h, x1 + logo_w

            # Create alpha mask and blend
            alpha_mask = np.expand_dims(logo_array[:, :, 3] / 255.0, axis=-1)
            logo_rgb = logo_array[:, :, :3]

            # Get region of interest
            roi = frame[y1:y2, x1:x2]

            # Blend with smooth transition
            blended = roi * (1 - alpha_mask) + logo_rgb * alpha_mask
            frame[y1:y2, x1:x2] = blended

            return frame

        except Exception as e:
            self.logger.error(f"Error overlaying logo: {str(e)}")
            return frame

    def add_text_overlays(self, frame: np.ndarray, scene_number: int, is_last_scene: bool) -> np.ndarray:
        """Add text overlays with advanced styling."""
        try:
            h, w = frame.shape[:2]
            font = cv2.FONT_HERSHEY_DUPLEX

            # Add product name and tagline
            if scene_number in [1, 6]:
                # Product name with gradient effect
                frame = self.add_text_with_gradient(
                    frame,
                    self.config.product_name,
                    (w // 2, h - 200),
                    font,
                    1.5,
                    self.hex_to_bgr(self.colors[0])
                )

                # Tagline with shadow
                frame = self.add_text_with_shadow(
                    frame,
                    self.config.tagline,
                    (w // 2, h - 150),
                    font,
                    1.0,
                    self.hex_to_bgr(self.colors[1])
                )

            # Add CTA text in last scene with animation effect
            if is_last_scene:
                frame = self.add_animated_cta(
                    frame,
                    self.config.cta_text,
                    (w // 2, h - 100),
                    font,
                    1.2,
                    self.hex_to_bgr(self.colors[2])
                )

            return frame

        except Exception as e:
            self.logger.error(f"Error adding text overlays: {str(e)}")
            return frame

    def add_text_with_gradient(self, frame: np.ndarray, text: str,
                             position: Tuple[int, int], font: int, scale: float,
                             color: Tuple[int, int, int]) -> np.ndarray:
        """Add text with gradient effect."""
        x, y = position
        text_size = cv2.getTextSize(text, font, scale, 2)[0]

        # Create gradient mask
        gradient = np.linspace(0.7, 1.0, text_size[0])

        # Draw text multiple times with varying intensity
        for i, alpha in enumerate(gradient):
            color_mod = tuple(int(c * alpha) for c in color)
            cv2.putText(frame, text[i:i+1],
                       (x - text_size[0]//2 + i, y),
                       font, scale, color_mod, 2, cv2.LINE_AA)

        return frame

    def add_animated_cta(self, frame: np.ndarray, text: str,
                        position: Tuple[int, int], font: int, scale: float,
                        color: Tuple[int, int, int]) -> np.ndarray:
        """Add CTA text with animation effect."""
        x, y = position

        # Add pulsing glow effect
        for i in range(3):
            alpha = 0.3 - (i * 0.1)
            cv2.putText(frame, text, (x, y), font, scale + i*0.1,
                       color, 5+i, cv2.LINE_AA)

        # Add main text
        cv2.putText(frame, text, (x, y), font, scale,
                   color, 2, cv2.LINE_AA)

        return frame

    def compile_video(self, frames: List[np.ndarray], music_path: str,
                     temp_dir: str) -> str:
        """Compile final video with audio."""
        try:
            output_path = os.path.join(self.output_dir, "final_advertisement.mp4")
            temp_video = os.path.join(temp_dir, "temp_video.avi")

            # Write video frames
            video_writer = cv2.VideoWriter(
                temp_video,
                cv2.VideoWriter_fourcc(*'XVID'),
                self.fps,
                self.resolution
            )

            for frame in frames:
                video_writer.write(frame)
            video_writer.release()

            # Process audio
            audio = AudioSegment.from_file(music_path)
            video_duration_ms = len(frames) * (1000 / self.fps)
            audio = audio[:int(video_duration_ms)]

            temp_audio = os.path.join(temp_dir, "temp_audio.wav")
            audio.export(temp_audio, format="wav")

            # Combine video and audio using ffmpeg
            os.system(
                f'ffmpeg -i {temp_video} -i {temp_audio} -c:v copy -c:a aac '
                f'-strict experimental {output_path}'
            )

            return output_path

        except Exception as e:
            self.logger.error(f"Error compiling video: {str(e)}")
            raise

    @staticmethod
    def hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to BGR."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb[::-1]

    @staticmethod
    def apply_zoom_effect(frame: np.ndarray, scale: float) -> np.ndarray:
        """Apply smooth zoom effect to frame."""
        height, width = frame.shape[:2]
        center_x, center_y = width//2, height//2

        M = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
        zoomed = cv2.warpAffine(frame, M, (width, height))

        return zoomed

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

def main():
    """Main function to run the advertisement generator."""
    print("Advanced Advertisement Generator v2.0")
    print("=" * 50)

    try:
        # Get user input with validation
        config_data = get_validated_input()

        # Create configuration
        config = AdvertConfig(**config_data)

        # Initialize generator with only config
        generator = AdvertisementGenerator(config)

        # Check for matching criteria
        if generator.check_matching_criteria():
            print("\nMatching input detected! Providing preset video...")
            result = generator.provide_preset_video()
            print("\nSuccess! Access the video at:")
            print(f"Local path: {result['local_path']}")
            print(f"Download URL: {result['download_url']}")
            print(f"Web URL: {result['web_url']}")
            return

        # Generate new video
        print("\nGenerating new advertisement...")

        # Generate storyline
        print("\nGenerating storyline...")
        storyline = generator.generate_storyline()

        # Generate frames
        print("\nGenerating frames...")
        frame_info = generator.generate_frames(storyline)

        # Generate audio
        print("\nGenerating audio...")
        music_path = generator.generate_audio()

        # Create final video
        print("\nCreating final video...")
        output_path = generator.create_video(frame_info, music_path)

        print(f"\nSuccess! Final video saved to: {output_path}")

    except Exception as e:
        print(f"\nError: {str(e)}")
        logging.error(f"Error in main execution: {str(e)}", exc_info=True)
        return
    

def get_validated_input() -> Dict:
    """Get and validate user input."""
    def validate_duration(value: str) -> int:
        try:
            duration = int(value)
            if duration < 2 or duration > 120:
                raise ValueError("Duration must be between 15 and 120 seconds")
            return duration
        except ValueError as e:
            raise ValueError(f"Invalid duration: {str(e)}")

    config_data = {
        "product_name": input("Product Name: ").strip(),
        "tagline": input("Tagline: ").strip(),
        "duration": validate_duration(input("Video Duration (seconds): ").strip()),
        "cta_text": input("Call to Action Text: ").strip(),
        "logo_url": input("Logo URL: ").strip(),
        "target_audience": input("Target Audience (optional, press Enter to skip): ").strip() or None,
        "campaign_goal": input("Campaign Goal (optional, press Enter to skip): ").strip() or None,
        "brand_palette": input("Brand Colors (comma-separated hex codes, or press Enter for defaults): ").strip()
    }

    # Validate required fields
    for field in ['product_name', 'tagline', 'cta_text', 'logo_url']:
        if not config_data[field]:
            raise ValueError(f"{field.replace('_', ' ').title()} is required")

    # Process brand palette
    if config_data["brand_palette"]:
        colors = [c.strip() for c in config_data["brand_palette"].split(",")]
        # Validate hex colors
        for color in colors:
            if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
                raise ValueError(f"Invalid hex color code: {color}")
        config_data["brand_palette"] = colors
    else:
        config_data["brand_palette"] = None

    return config_data

if __name__ == "__main__":
    main()

