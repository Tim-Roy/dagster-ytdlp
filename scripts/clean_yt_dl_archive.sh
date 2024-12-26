#!/bin/bash

# Delete videos older than 3 days
find $YT_DOWNLOADS_PATH -mindepth 1 -mtime +3 -delete
