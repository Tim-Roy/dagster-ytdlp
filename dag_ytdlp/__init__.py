from dagster import Definitions

from .jobs import ytdl as ytdl_jobs
from .schedules import ytdl as ytdl_schedules
from .utils.logging import setup_logging
from .youtube.ytdl import YT_Channel

setup_logging()

__all__ = ["YT_Channel"]


jobs = [
    ytdl_jobs.refresh_yt_subscriptions,
    ytdl_jobs.download_from_url,
    ytdl_jobs.backfill_yt_channel,
    ytdl_jobs.delete_ephemeral_yt_videos_job,
]

schedules = [ytdl_schedules.refresh_yt_subscriptions_schedule, ytdl_schedules.delete_ephemeral_yt_videos_schedule]

defs = Definitions(
    jobs=jobs,
    schedules=schedules,
)
