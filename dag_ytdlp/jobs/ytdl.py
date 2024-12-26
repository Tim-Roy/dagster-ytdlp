from dagster import job

from ..ops.ytdl import (
    backfill_yt_channel_if_valid,
    delete_ephemeral_yt_videos_op,
    download_new_yt_episodes,
    download_yt_from_url,
    get_yt_channels,
)


@job
def refresh_yt_subscriptions():
    yt_channels = get_yt_channels()
    yt_channels.map(download_new_yt_episodes).collect()


INSTRUCTIONS = "1. Copy & Paste URL below."
INSTRUCTIONS += "\n2. To choose a separate folder from _MISC_, set to false."
INSTRUCTIONS += "\n3. To override default channel name, enter channel name (after step 2)."

yt_url_config = {
    "ops": {
        "download_yt_from_url": {
            "config": {
                "_instructions": INSTRUCTIONS,
                "url": "",
                "use_MISC_channel": True,
                "channel": "",
                "parent": "shared",
            }
        }
    }
}


@job(config=yt_url_config)
def download_from_url():
    download_yt_from_url()


yt_backfill_config = {"ops": {"backfill_yt_channel_if_valid": {"config": {"channel": "", "max_videos": 100}}}}


@job(config=yt_backfill_config)
def backfill_yt_channel():
    backfill_yt_channel_if_valid()


delete_ephemeral_yt_videos_job_config = {"ops": {"delete_ephemeral_yt_videos_op": {"config": {"ephmeral_days": 60}}}}


@job(config=delete_ephemeral_yt_videos_job_config)
def delete_ephemeral_yt_videos_job():
    delete_ephemeral_yt_videos_op()


if __name__ == "__main__":
    refresh_yt_subscriptions.execute_in_process()
