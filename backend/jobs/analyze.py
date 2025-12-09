import tempfile
import os
from datetime import datetime
from typing import List

import cv2
import httpx
import google.generativeai as genai
from PIL import Image
from rq.job import get_current_job

from auth import User
from config import get_settings
from queue import get_queue
from schemas import AnalyzeRequest
from storage import upload_file, presign_url


def enqueue_analyze(request: AnalyzeRequest, user: User) -> str:
    q = get_queue()
    job = q.enqueue(run_analyze_job, request.model_dump(), user.model_dump())
    return job.id


def run_analyze_job(request_data: dict, user_data: dict) -> str:
    job = get_current_job()
    settings = get_settings()
    req = AnalyzeRequest(**request_data)
    user = User(**user_data)
    genai.configure(api_key=settings.google_api_key)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            video_path = os.path.join(tmp, "video.mp4")
            _download_file(req.videoUrl, video_path)
            frames = _sample_frames(video_path, max_frames=6)
            report_text = _analyze_with_gemini(frames, req)

            report_path = os.path.join(tmp, "report.txt")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_text)

            key = f"reports/{user.sub}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
            upload_file(report_path, key)
            url = presign_url(key)

        job.meta["result_url"] = url
        job.save_meta()
        return url
    except Exception as exc:
        if job:
            job.meta["error"] = str(exc)
            job.save_meta()
        raise


def _download_file(url: str, dest: str) -> None:
    with httpx.Client() as client:
        resp = client.get(url)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(resp.content)


def _sample_frames(video_path: str, max_frames: int = 6) -> List[Image.Image]:
    cap = cv2.VideoCapture(video_path)
    frames: List[Image.Image] = []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    step = max(1, total // max_frames)
    idx = 0
    while len(frames) < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(frame_rgb))
        idx += step
    cap.release()
    return frames


def _analyze_with_gemini(frames: List[Image.Image], req: AnalyzeRequest) -> str:
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = (
        f"Analyze this advertisement video for {req.productName} by {req.brandName}.\n"
        f"Tagline: {req.tagline}.\n"
        f"Color palette: {req.colorPalette or 'not provided'}.\n"
        "Provide scores (0-100) for visual impact, creative execution, audience engagement, "
        "production quality, brand integration, tagline effectiveness. Then list 5 actionable recommendations.\n"
        "Return concise markdown text."
    )
    resp = model.generate_content([prompt, *frames])
    if not resp or not resp.text:
        raise ValueError("Empty response from Gemini")
    return resp.text

