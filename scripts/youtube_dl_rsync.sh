#!/bin/bash

rsync -rs --exclude '*.part' --exclude '*.mp4.ytdl' -e "ssh" $YT_DOWNLOADS_PATH $NAS_YT_PATH
