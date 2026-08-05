import os
import json
import time
from pathlib import Path

import requests

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "gist-downloader",
}

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def load_gists():
    raw = os.environ.get("GISTS", "").strip()
    if not raw:
        raise ValueError("环境变量 GISTS 为空")
    return json.loads(raw)

def get_gist_meta(gist_url):
    gist_id = gist_url.rstrip("/").split("/")[-1].split("#")[0]
    api_url = f"https://api.github.com/gists/{gist_id}"
    r = requests.get(api_url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def download_and_overwrite(item):
    gist_url = item["gist_url"]
    file_name = item["file_name"]
    save_as = item.get("save_as", file_name)

    meta = get_gist_meta(gist_url)
    file_info = meta["files"].get(file_name)
    if not file_info:
        print(f"未找到文件: {file_name}")
        return

    raw_url = file_info["raw_url"]
    r = requests.get(raw_url, timeout=30)
    r.raise_for_status()

    out_path = RESULTS_DIR / save_as
    out_path.write_text(r.text, encoding="utf-8")

    print(f"已覆盖写入: {out_path}")

def main():
    gists = load_gists()

    for i, item in enumerate(gists):
        try:
            download_and_overwrite(item)
        except Exception as e:
            print(f"下载失败: {item.get('gist_url')} -> {e}")

        if i < len(gists) - 1:
            time.sleep(5)

if __name__ == "__main__":
    main()
