from __future__ import annotations

import datetime as dt
import logging
import re
from typing import Iterable, TypeVar

import sqlalchemy as db
from yt_dlp import YoutubeDL

from ..config.database import DATABASE_URL
from ..config.ytdl import YDL_OPTS_BEST, YDL_OPTS_DEFAULT

T = TypeVar("T")


def take(amount: int, iterable: Iterable[T], reverse: bool = False) -> Iterable[T]:
    """Create iterable capped at amount.

    To flip order of iterable, set reverse = True
    """
    if reverse:
        iterable = iter(reversed([x for x in iterable]))
    for _, elem in zip(range(amount), iterable):
        yield elem


def check_url_is_playlist(url: str):
    """True if string follows YouTube's playlist syntax."""
    return bool(re.search(r"\/playlist\?", url))


class YT_Channel:
    """Core class for managing downloading of videos from a specified channel or playlist."""

    def __init__(
        self, url: str, channel: str = None, parent: str = None, order_seq: bool = False, best_format: bool = False
    ):
        """Initialize a new instance of the class.

        Args:
        ----
            url (str):
                The URL to be used for the instance. Can be a channel or a playlist
            channel (str, optional):
                The channel name to be used. Defaults to None.
                If provided will override the channel name provided from youtube's meatadata.
            parent (str, optional):
                The parent identifier. Defaults to None.
                If provided, will insert the channel under the given parent folder.
            order_seq (bool, optional):
                Flag to indicate if order sequence should be used. Defaults to False.
                If True, will overrride the default behavior of using the MMDD as the episode number and replace with
                the playlist sequence item. Also will override Season number from YYYY to just "1".
            best_format (bool, optional):
                Flag to indicate if the best format should be used. Defaults to False.
                When True, will override the ydl_opts format. This can eat up a lot more space.

        """
        # There is a bug with ytdl where the original copy of ytdl_opts gets overwritten when intializing a new instance
        # Hence for some wonky work-arounds
        self.url = url
        self.channel = channel
        self.parent = parent
        self.order_seq = order_seq
        self.ydl_opts = YDL_OPTS_DEFAULT
        if best_format:
            self.ydl_opts = YDL_OPTS_BEST
        self.outtmpl_default_bug = False
        if isinstance(
            self.ydl_opts["outtmpl"], str
        ):  # weird bug? where sometimes the outtmpl is a dict with item = "default"
            outtmpl = self.ydl_opts["outtmpl"]
        else:
            outtmpl = self.ydl_opts["outtmpl"]["default"]
            self.outtmpl_default_bug = True
        if parent is not None:
            outtmpl = outtmpl.replace("%(channel)s", f"{parent}/%(channel)s")
        if channel is not None:
            outtmpl = outtmpl.replace("%(channel)s", f"{channel}")
        if self.order_seq:
            outtmpl = outtmpl.replace("Season %(upload_date>%y)s", "Season 1")
            outtmpl = outtmpl.replace("S%(upload_date>%y)s", "S1")
        if self.outtmpl_default_bug:
            self.ydl_opts["outtmpl"]["default"] = outtmpl
        else:
            self.ydl_opts["outtmpl"] = outtmpl
        self.outtmpl = outtmpl
        self.logging = logging.getLogger("ytdl_logger")

    def fetch_entries(self):
        """Populate URLs of videos for the channel."""
        if self.order_seq:
            # Arbitrary high number
            max_hist = 1000
        else:
            max_hist = self.ydl_opts["playlistend"]
        with YoutubeDL(self.ydl_opts) as ydl:
            yt_info = ydl.extract_info(self.url, download=False, process=False)
        if yt_info is None:
            self.logging.warning(f"{self.channel} returned empty. Check {self.url}.")
            self.video_urls = []
            return None
        result = []
        entries = yt_info.get("entries", [])
        # convert generator to list and remove private videos
        entries = [entry for entry in list(entries) if not self._remove_video(entry)]
        if entries is None or len(entries) == 0:
            self.logging.warning(f"{self.channel} returned no valid video URLs. Check {self.url}.")
            return None
        first_date = self.get_video_upload_date(entries[0].get("url"))
        last_date = self.get_video_upload_date(entries[-1].get("url"))
        playlist_count = yt_info.get("playlist_count", None)
        if playlist_count is not None:
            max_hist = min(max_hist, playlist_count)
        # For some (but not all) playlists, the oldest video is the first url
        reverse_entries = (last_date > first_date) and not (self.order_seq)
        for i, entry in enumerate(take(max_hist, iter(entries), reverse_entries)):
            if entry.get("url") is None:
                logging.warning("Ignoring malformed url entry from %s", entry.get("url"))
            else:
                entry["playlist_index"] = i + 1
                result.append(entry)
        self.video_metadata = result
        self.video_urls = [(result[i]["url"], result[i]["playlist_index"]) for i in range(len(result))]

    def get_video_upload_date(self, url: str) -> int:
        dt = YoutubeDL(self.ydl_opts).extract_info(url, download=False, process=False)["upload_date"]
        return dt

    @staticmethod
    def get_hist_dl_urls() -> list[str]:
        """Query DB and return list of URLs previously downloaded."""
        engine = db.create_engine(DATABASE_URL)
        connection = engine.connect()
        table = db.Table("downloads", db.MetaData(), autoload_with=engine, schema="ytdl")
        query = db.select(table.columns.url)
        rslt = connection.execute(query).fetchall()
        url_hist = [x[0] for x in rslt]
        return url_hist

    @staticmethod
    def update_db_with_video_url(url: str, channel: str):
        """Update history with video URL and channel."""
        now = dt.datetime.now()
        engine = db.create_engine(DATABASE_URL)
        table = db.Table("downloads", db.MetaData(), autoload_with=engine, schema="ytdl")
        insert_stmt = db.insert(table).values(url=url, channel=channel, download_date=now)
        with engine.connect() as conn:
            conn.execute(insert_stmt)
            conn.commit()

    def use_index_for_episode(self, ydl_opts: dict, idx: int) -> dict:
        """Update format for epsides in YT config dict to use playlist index."""
        outtmpl = self.outtmpl
        outtmpl = outtmpl.replace("E%(upload_date>%m%d)s", f"E{idx}")
        # hack due to bug (see class initialization)
        if isinstance(self.ydl_opts["outtmpl"], str):
            ydl_opts["outtmpl"] = outtmpl
        else:
            ydl_opts["outtmpl"]["default"] = outtmpl
        return ydl_opts

    def download_video(self, url: str, playlist_idx: int, update_db=True):
        """Download a single video.

        Args:
        ----
        url (str): URL of video
        playlist_idx (int): Index of playlist. Only used if self.order_seq = True.
        update_db (bool): Add entry to database after successful download. Defaults to True

        """
        ydl_opts = self.ydl_opts.copy()
        if self.channel is None:
            channel = ""
        else:
            channel = self.channel
        if self.order_seq:
            ydl_opts = self.use_index_for_episode(ydl_opts, playlist_idx)

        with YoutubeDL(ydl_opts) as ydl:
            dl_fail = ydl.download([url])
        if update_db and not dl_fail:
            self.update_db_with_video_url(url, channel)
            logging.info(f"{url} for channel {channel} successfully downloaded")
        elif dl_fail:
            logging.warning(f"{url} for channel {channel} download failed")
        else:
            logging.info(f"{url} for channel {channel} successfully downloaded")

    def download_new_videos(self):
        """Initiate downloading of videos for channel.

        Will only download videos if not present in history.
        """
        url_hist = self.get_hist_dl_urls()
        video_urls = [(url, idx) for (url, idx) in self.video_urls if url not in url_hist]

        if len(video_urls) > 0:
            for url, idx in video_urls:
                self.download_video(url, idx)
            logging.info(f"Completed attempted downloads for {self.channel}")
        else:
            logging.info(f"No new videos to download for {self.channel}")

    def download_from_url(self):
        """Download a single video given a provided URL if not in database."""
        self.video_urls = [(self.url, 0)]
        self.download_new_videos()

    def set_max_videos(self, max_videos: int = 100):
        """Override default options for max videos to add download queue."""
        self.ydl_opts["playlistend"] = max_videos

    @staticmethod
    def _remove_video(entry):
        """Return True if entry should be removed from download list.

        Reasons for removal:
            - Private video
            - Live feed
        """
        remove = False
        if entry.get("title", "") == "[Private video]":
            remove = True
        elif entry.get("live_status", None) is not None:
            remove = True
        return remove
