import tempfile
import os
import time
from datetime import datetime
from typing import List

import httpx
import ffmpeg
import replicate
from rq.job import get_current_job

from auth import User
from config import get_settings
from queue import get_queue
from schemas import GenerateRequest
from storage import upload_file, presign_url


def enqueue_generate(request: GenerateRequest, user: User) -> str:
    q = get_queue()
    job = q.enqueue(run_generate_job, request.model_dump(), user.model_dump())
    return job.id


def run_generate_job(request_data: dict, user_data: dict) -> str:
    job = get_current_job()
    settings = get_settings()
    req = GenerateRequest(**request_data)
    user = User(**user_data)

    try:
        replicate_client = replicate.Client(api_token=settings.replicate_api_token)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        key = f"generated/{user.sub}/{timestamp}.mp4"

        with tempfile.TemporaryDirectory() as tmp:
            frame_paths = _generate_frames(req, replicate_client, tmp, settings.generation_scenes)
            audio_path = _generate_audio(req, replicate_client, tmp)
            video_path = _stitch_video(frame_paths, audio_path, tmp, settings.generation_fps, settings.generation_resolution)

            upload_file(video_path, key)
            url = presign_url(key)

        job.meta["result_url"] = url
        job.save_meta()
        return url
    except Exception as exc:
        if job:
            job.meta["error"] = str(exc)
            job.save_meta()
        raise


def _generate_frames(req: GenerateRequest, client: replicate.Client, tmp: str, scenes: int) -> List[str]:
    prompts: List[str] = []
    for scene in range(1, scenes + 1):
        prompts.append(
            f"Scene {scene}: {req.productName} - {req.tagline}. "
            f"CTA: {req.callToAction}. "
            f"Target audience: {req.targetAudience or 'general consumers'}. "
            f"Campaign goal: {req.campaignGoal or 'brand awareness'}. "
            "Cinematic lighting, commercial quality, 4k, product hero shot."
        )

    frame_paths: List[str] = []
    with httpx.Client() as client_http:
        for idx, prompt in enumerate(prompts):
            output = client.run(
                "stability-ai/stable-diffusion-xl-base-1.0",
                input={
                    "prompt": prompt,
                    "cfg_scale": 7,
                    "num_inference_steps": 30,
                },
            )
            # replicate returns list of URLs
            img_url = output[0] if isinstance(output, list) else output
            resp = client_http.get(img_url)
            resp.raise_for_status()
            frame_path = os.path.join(tmp, f"frame_{idx:02d}.png")
            with open(frame_path, "wb") as f:
                f.write(resp.content)
            frame_paths.append(frame_path)
    return frame_paths


def _generate_audio(req: GenerateRequest, client: replicate.Client, tmp: str) -> str:
    prompt = (
        f"Upbeat commercial background music for {req.productName}. "
        f"Tagline: {req.tagline}. Modern, inspiring, 15 seconds."
    )
    output = client.run(
        "facebook/musicgen-small",
        input={"prompt": prompt, "duration": min(req.duration, 15)},
    )
    audio_url = output[0] if isinstance(output, list) else output
    audio_path = os.path.join(tmp, "audio.wav")
    with httpx.Client() as client_http:
        resp = client_http.get(audio_url)
        resp.raise_for_status()
        with open(audio_path, "wb") as f:
            f.write(resp.content)
    return audio_path


def _stitch_video(frame_paths: List[str], audio_path: str, tmp: str, fps: int, resolution: str) -> str:
    list_file = os.path.join(tmp, "frames.txt")
    with open(list_file, "w") as f:
        for frame in frame_paths:
            f.write(f"file '{frame}'\n")
            # Repeat to stretch duration to match audio if needed
            f.write(f"file '{frame}'\n")

    video_out = os.path.join(tmp, "out.mp4")

    (
        ffmpeg
        .input(list_file, format="concat", safe=0, r=fps)
        .output(audio_path, video_out, vcodec="libx264", acodec="aac", pix_fmt="yuv420p", s=resolution, shortest=None)
        .overwrite_output()
        .run(quiet=True)
    )
    return video_out

