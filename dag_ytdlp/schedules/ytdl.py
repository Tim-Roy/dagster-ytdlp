from os import environ

from dagster import schedule

from ..jobs.ytdl import delete_ephemeral_yt_videos_job, refresh_yt_subscriptions

TZ = environ["TZ"]


# Daily @ 4:05am, 12:05pm, 6:05pm, 11:05pm
@schedule(cron_schedule="5 4,12,18,23 * * *", job=refresh_yt_subscriptions, execution_timezone=TZ)
def refresh_yt_subscriptions_schedule(_context):
    return {}


# Daily @ 2AM
@schedule(cron_schedule="10 2 * * *", job=delete_ephemeral_yt_videos_job, execution_timezone=TZ)
def delete_ephemeral_yt_videos_schedule(_context):
    return {}
