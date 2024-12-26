from __future__ import annotations

from os import environ
from typing import Optional

from ..utils.config import get_env_var
from ..utils.io import load_yaml

YT_DOWNLOADS_PATH = environ["YT_DOWNLOADS_PATH"]

# Youtube DL opts
# https://github.com/yt-dlp/yt-dlp/tree/master?tab=readme-ov-file#download-options
YDL_OPTS_ALL = {
    "playliststart": 1,
    "playlistend": 52,
    "ignoreerrors": True,
    "writethumbnail": True,
    "writedescription": True,
    "writeinfojson": True,
    "outtmpl": (
        f"{YT_DOWNLOADS_PATH}/%(channel)s/Season %(upload_date>%y)s/%(title)s "
        "(S%(upload_date>%y)sE%(upload_date>%m%d)s).%(ext)s"
    ),
}

YDL_OPTS_DEFAULT = YDL_OPTS_ALL.copy()
YDL_OPTS_DEFAULT["format"] = "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4] / bv*+ba/b"

YDL_OPTS_BEST = YDL_OPTS_ALL.copy()
YDL_OPTS_BEST["format"] = "bestvideo+bestaudio/best"
YDL_OPTS_BEST["postprocessors"] = [
    {
        "key": "FFmpegVideoConvertor",
        "preferedformat": "mkv",
    }
]


def load_yt_subs_config(path: Optional[str] = None) -> list[dict]:
    """Load the YT subs yaml as a list of dicts.

    If path is None (default), will use YT_SUBS_PATH from enironment.

    """
    if path is None:
        path = get_env_var("YT_SUBS_PATH", "path")
    subs = []
    yt_subs = load_yaml(path)
    for parent, entry in yt_subs.items():
        for channel, options in entry.items():
            options["parent"] = parent
            options["channel"] = channel
            subs.append(options)
    return subs
