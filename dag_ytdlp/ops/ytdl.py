import logging
from pathlib import Path
from typing import Dict, List, Optional

from dagster import DynamicOut, DynamicOutput, op

from ..config.ytdl import load_yt_subs_config
from ..utils.config import get_env_var
from ..utils.io import delete_legacy_files
from ..youtube.ytdl import YT_Channel

LOGGER = logging.getLogger("ytdl_logger")


@op(out=DynamicOut())
def get_yt_channels(path: Optional[str] = None) -> List[Dict]:
    """Load YT subscription config as dict.

    Args:
    ----
        path (str, optional): Path to config location for YT channels.
        If None (default), will use YT_FULL_PATH from environment.

    Returns dict of YT channel title and YT channel url with additional optional args.

    """
    yt_chan_list = load_yt_subs_config(path)
    for yt_channel in yt_chan_list:
        yield DynamicOutput(
            yt_channel,
            mapping_key=f'{yt_channel["channel"]}'.replace(" ", "_")
            .replace("-", "_DASH_")
            .replace(".", "_DOT_")
            .replace("'", ""),
        )


@op
def download_new_yt_episodes(yt_channel: dict):
    """Download all new videos for a given channel config dict."""
    url = yt_channel["url"]
    channel = yt_channel["channel"]
    parent = yt_channel["parent"]
    order_seq = yt_channel.get("order_seq", False)
    best_format = yt_channel.get("best_format", False)
    ytdl = YT_Channel(url, channel, parent, order_seq, best_format)
    ytdl.fetch_entries()
    ytdl.download_new_videos()


@op(config_schema=dict)
def download_yt_from_url(context):
    url = context.op_config.get("url", "")
    channel = "MISC"
    if not context.op_config.get("use_MISC_channel", True):
        channel = context.op_config.get("use_MISC_channel", "MISC")
    if url == "":
        LOGGER.error("No url entered.")
    else:
        ytdl = YT_Channel(url, channel)
        ytdl.download_from_url()


@op(config_schema=dict)
def backfill_yt_channel_if_valid(context):
    channel = context.op_config.get("channel", "")
    max_videos = context.op_config.get("max_videos", 100)
    yt_chan_list = load_yt_subs_config()
    url = None
    for yt_channel in yt_chan_list:
        if channel == yt_channel["channel"]:
            url = yt_channel["url"]
            parent = yt_channel["parent"]
            order_seq = yt_channel.get("order_seq", False)
            best_format = yt_channel.get("best_format", False)
    if url is None:
        LOGGER.error(f"Bad configuration for {channel}.")
    else:
        ytdl = YT_Channel(url, channel, parent, order_seq, best_format)
        ytdl.set_max_videos(max_videos)
        ytdl.fetch_entries()
        ytdl.download_new_videos()


@op(config_schema=dict)
def delete_ephemeral_yt_videos_op(context):
    ephmeral_days = context.op_config.get("ephmeral_days", 365)
    yt_chan_list = load_yt_subs_config()
    YT_NAS_PATH = get_env_var("YT_NAS_PATH", "YT_NAS_PATH")
    for yt_channel in yt_chan_list:
        if yt_channel.get("ephemeral", False):
            ch_path = Path(YT_NAS_PATH, yt_channel["parent"], yt_channel["channel"])
            if ch_path.exists() and ch_path.is_dir():
                delete_legacy_files(ch_path, ephmeral_days)


if __name__ == "__main__":
    delete_ephemeral_yt_videos_op()
