import subprocess
import json
import sys
import os
from pathlib import Path

def extract_video_info(url_or_id: str, output_dir: str = "knowledge/extracted"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # yt-dlp でメタデータと字幕（日本語・英語）を取得
    cmd = [
        r"C:\Users\kiyot\AppData\Local\Programs\Python\Python310\Scripts\yt-dlp.exe",
        "--dump-json",
        "--write-auto-sub",
        "--sub-lang", "ja,en",
        "--skip-download",
        "--output", f"{output_dir}/%(id)s",
        url_or_id
    ]
    
    print(f"Extracting metadata from: {url_or_id}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0:
        print("Error running yt-dlp:", result.stderr)
        return None
    
    try:
        data = json.loads(result.stdout)
        info = {
            "id": data.get("id"),
            "title": data.get("title"),
            "uploader": data.get("uploader"),
            "duration": data.get("duration"),
            "description": data.get("description"),
            "webpage_url": data.get("webpage_url"),
            "chapters": data.get("chapters", [])
        }
        json_path = Path(output_dir) / f"{info['id']}_meta.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"Saved metadata to {json_path}")
        return info
    except Exception as e:
        print("Failed to parse json:", e)
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_video_info(sys.argv[1])
    else:
        print("Usage: python youtube_extractor.py <youtube_url>")
