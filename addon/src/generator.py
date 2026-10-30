import json
import os
import shutil
from typing import Dict, List

from config import (
    ADDON_ID,
    ADDON_VERSION,
    ADDON_NAME,
    ADDON_DESCRIPTION,
    SERIES_TEMPLATES,
    VIDEO_SIZE_APPROX,
    STREAM_FPS,
    STREAM_RESOLUTION,
    PAGES_BASE_URL,
    SUBTITLE_LANG,
    SERIES_WITH_SUBS,
)
from scraper import Episode

SUBS_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subs")


SEASON_MAPS = {
    "tt0121220": [
        (1, 39), (40, 74), (75, 107), (108, 139),
        (140, 165), (166, 194), (195, 219), (220, 253), (254, 291),
    ],
    "tt0214341": [
        (1, 39), (40, 74), (75, 107), (108, 139),
        (140, 165), (166, 194), (195, 219), (220, 253), (254, 291),
    ],
    "tt0088509": [
        (1, 13), (14, 28), (29, 68), (69, 101), (102, 132), (133, 153),
    ],
    "tt0280249": [
        (1, 28), (29, 53), (54, 101), (102, 122), (123, 153),
    ],
}

DEFAULT_SEASONS = [(1, 999)]


def get_season(episode_number: int, imdb_id: str = "tt0121220") -> int:
    for season, (start, end) in enumerate(SEASON_MAPS.get(imdb_id, DEFAULT_SEASONS), 1):
        if start <= episode_number <= end:
            return season
    return 1


def get_season_episode(episode_number: int, imdb_id: str = "tt0121220") -> int:
    for season, (start, end) in enumerate(SEASON_MAPS.get(imdb_id, DEFAULT_SEASONS), 1):
        if start <= episode_number <= end:
            return episode_number - start + 1
    return episode_number


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_manifest() -> dict:
    return {
        "id": ADDON_ID,
        "version": ADDON_VERSION,
        "name": ADDON_NAME,
        "description": ADDON_DESCRIPTION,
        "logo": "https://static.vakinha.com.br/uploads/vakinha/image/566433/mtv.png?ims=700x410",
        "background": "https://static.vakinha.com.br/uploads/vakinha/image/566433/mtv.png?ims=700x410",
        "contactEmail": "ederr@ederr.com",
        "resources": ["stream"],
        "types": ["series"],
        "catalogs": [],
        "idPrefixes": ["tt"],
        "behaviorHints": {
            "adult": False,
            "p2p": False,
            "configurable": False,
            "configurationRequired": False,
        },
    }


def build_subtitles(episode: Episode, series_key: str) -> list:
    """Trả về danh sách phụ đề cho tập (rỗng nếu chưa có file .srt)."""
    if series_key not in SERIES_WITH_SUBS:
        return []
    name = f"ep_{episode.number:03d}.srt"
    if not os.path.isfile(os.path.join(SUBS_SRC_DIR, series_key, name)):
        return []
    return [
        {
            "id": f"{series_key}-{SUBTITLE_LANG}-{episode.number:03d}",
            "url": f"{PAGES_BASE_URL}/subs/{series_key}/{name}",
            "lang": SUBTITLE_LANG,
        }
    ]


def copy_subtitles(output_dir: str) -> int:
    """Chép subs/ vào dist/subs/ để GitHub Pages phục vụ."""
    if not os.path.isdir(SUBS_SRC_DIR):
        return 0
    dest = os.path.join(output_dir, "subs")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(SUBS_SRC_DIR, dest)
    return sum(len(f) for _, _, f in os.walk(dest))


def build_stream(episode: Episode, series_key: str) -> dict:
    template = SERIES_TEMPLATES[series_key]
    subtitles = build_subtitles(episode, series_key)
    return {
        "streams": [
            {
                "url": episode.direct_url,
                "name": ADDON_NAME,
                "title": f"{template['name']} Ep.{episode.number:02d} · {STREAM_RESOLUTION} · NTSC {STREAM_FPS}fps · ~6GB",
                "behaviorHints": {
                    "notWebReady": False,
                    "bingeGroup": f"selectavision-{series_key}",
                    "filename": f"{template['name']}.{episode.number:02d}.SelectaVision.{STREAM_RESOLUTION}.mkv",
                    "videoSize": VIDEO_SIZE_APPROX,
                },
                **({"subtitles": subtitles} if subtitles else {}),
            }
        ]
    }


def generate_addon_files(
    episodes_by_series: Dict[str, List[Episode]], output_dir: str = "dist"
) -> None:
    import glob as globmod
    stream_dir = f"{output_dir}/stream/series"
    for old in globmod.glob(f"{stream_dir}/*.json"):
        os.remove(old)
    ensure_dir(output_dir)
    ensure_dir(stream_dir)

    write_json(f"{output_dir}/manifest.json", build_manifest())
    print(f"Copied {copy_subtitles(output_dir)} subtitle files")

    total_files = 0
    for series_key, episodes in episodes_by_series.items():
        if not episodes:
            continue

        template = SERIES_TEMPLATES[series_key]

        for episode in episodes:
            stream_data = build_stream(episode, series_key)
            for series_id in template["ids"]:
                season = get_season(episode.number, series_id)
                season_ep = get_season_episode(episode.number, series_id)
                stream_id = f"{series_id}:{season}:{season_ep}"
                write_json(
                    f"{output_dir}/stream/series/{stream_id}.json",
                    stream_data,
                )
                total_files += 1

    print(f"Generated addon files in {output_dir}/")
    for key, eps in episodes_by_series.items():
        ids_count = len(SERIES_TEMPLATES[key]["ids"])
        print(
            f"  {SERIES_TEMPLATES[key]['name']}: {len(eps)} episodes x {ids_count} IDs = {len(eps) * ids_count} files"
        )
    print(f"Total stream files: {total_files}")
