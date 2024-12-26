# Dagster + YT-DLP

This is the source code for [YT-DLP](https://github.com/YT-DLP/YT-DLP) orchestration with Dagster. Requires Dagster to run. Optional scripts to sync with a NAS and delete older videos are also included.

This was a personal project that will not run without modifying source code or your local host. Below are suggested configurations.

# Disclaimer

This source code is provided "as is" without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the author be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

By using this source code, you agree that you are solely responsible for ensuring compliance with all applicable laws, regulations, and the terms and conditions of any platform or service, including YouTube or any other hosting services. The author assumes no responsibility for any misuse of the software or any consequences resulting from its use.

Users are strongly advised to familiarize themselves with and adhere to [YouTube’s Terms of Service](https://www.youtube.com/t/terms) and any other applicable policies of hosting services when using this source code.

## Set-up

1. Dagster must be configured to allow runs to be launched in new containers, follow the [tutorial](https://docs.dagster.io/deployment/guides/docker#launching-runs-in-containers) if needed.
1. 3 environent variables must be set both for this docker container AND the dagster container:
    1. YT_DOWNLOADS_PATH - the location where downloads are to be written. Update docker-compose for the host path as well.
    1. YT_SUBS_PATH - the path to the subscription config YAML. Update docker-compose for the host path as well.
    1. LOG_HOME, or remove logging if not interested.
    1. YT_NAS_PATH - needed for deleting videos tagged as ephemeral. Only needed for the `delete_ephemeral_yt_videos_job` job.
1. A back-end PostgreSQL database is used in this setup for maintaining a download history. To continue using this approach, the host, username, password, port and database must also be provided, see *./ytdl/config/database.py* for specifics. *./proc/dag_ytdlp.sql* contains the proper schema.
1. The scripts directory contains shell and systemd scripts for syncing data and cleaning the downloads directory.
1. The subscriptions YAML should follow the subscription_example.yaml format:
    - Must contain a URL
    - Optionally can contain the following 3 boolean options:
        - ephemeral (To be deleted after 90 days)
        - best_format (Override default and download best format available)
        - use_playlist_index (Use playlist index instead of MMDD for episode naming)
1. The Dagster service *workspace.yaml* must contain an entry for the corresponding code. For example, using the example DOCKERFILE with 4300, the following would need to be added:

```
load_from:
  - grpc_server:
      host: dagster_ytdlp
      port: 4300
      location_name: dagster_ytdlp_server
```

## Dagster Jobs

The following jobs are available when deployed:

#### refresh_yt_subscriptions

This is the main job that downloads new videos from the subscriptions list.

#### download_from_url

Manually download a single video from a URL.

#### backfill_yt_channel

Manually backfill a channel, allowing for a custom span of videos.

#### delete_ephemeral_yt_videos_job

Delete videos more than 90 days old from channels that are tagged as ephemeral.
