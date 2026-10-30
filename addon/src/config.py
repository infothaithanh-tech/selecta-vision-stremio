SERIES_TEMPLATES = {
    "dbz": {
        "ids": ["tt0121220", "tt0214341"],
        "name": "Dragon Ball Z",
    },
    "db": {
        "ids": ["tt0088509", "tt0280249"],
        "name": "Dragon Ball",
    },
}

ADDON_ID = "selectavision.stremio"
ADDON_VERSION = "1.0.0"
ADDON_NAME = "SelectaVision"
ADDON_DESCRIPTION = "Dragon Ball em HD - Dual Áudio (PT-BR/JP)"

VIDEO_SIZE_APPROX = 6400000000
STREAM_FPS = "23.976"
STREAM_RESOLUTION = "1080p"

# --- Phụ đề (Vietsub) ---
# URL gốc của GitHub Pages, dùng để tạo link tới file .srt.
# Trong GitHub Actions tự suy ra từ GITHUB_REPOSITORY (fork chạy được ngay);
# chạy trên máy thì đặt biến môi trường PAGES_BASE_URL nếu cần.
import os as _os

_repo = _os.environ.get("GITHUB_REPOSITORY", "edersonff/selecta-vision-stremio")
_owner, _name = _repo.split("/", 1)
PAGES_BASE_URL = _os.environ.get(
    "PAGES_BASE_URL", f"https://{_owner.lower()}.github.io/{_name}"
).rstrip("/")

SUBTITLE_LANG = "vie"  # mã ISO 639-2 mà Stremio dùng cho tiếng Việt
SUBTITLE_LABEL = "Tiếng Việt"
# Chỉ series nào có thư mục subs/<key>/ep_NNN.srt mới được gắn sub
SERIES_WITH_SUBS = {"dbz"}
