from pathlib import Path
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent

def get_youtube_stream(url: str) -> str:
    ydl_opts = {"format": "best[ext=mp4]/best"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"]
    except Exception as e:
        print(f"[WARNING] YouTube stream failed: {e}. Falling back to webcam.")
        return 0  # fallback to webcam

YOUTUBE_URL = "https://youtu.be/iJZcjZD0fw0"
config = {
    "video_source": get_youtube_stream(YOUTUBE_URL),  # webcam → 0
    "model_path": str(BASE_DIR / "ai_module" / "yolov8n.pt"),
    "save_counts": BASE_DIR / "ai_module" / "vehicle_counts.jsonl",
    "plan_file": BASE_DIR / "ai_module" / "signal_plan.json",
    "confidence": 0.4,
    "img_size": 640,
    "dashboard": {"page_title": "Smart Traffic Dashboard", "layout": "wide"}
}
