import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import yaml

logger = logging.getLogger("ytdl_logger")


def json_to_dict(path: str):
    with open(path, "r") as f:
        d = json.load(f)
    return d


def delete_legacy_files(ch_path: Path, ephemeral_days: int):
    """Scan the ch_path for subdir and remove all files from each subdir if older than ephemeral_days."""
    threshold_date = datetime.now() - timedelta(days=ephemeral_days)
    for child_dir in ch_path.iterdir():
        if child_dir.is_dir():
            for file_path in child_dir.iterdir():
                if file_path.is_file():
                    creation_time = file_path.stat().st_ctime
                    creation_date = datetime.fromtimestamp(creation_time)
                    if creation_date < threshold_date:
                        file_path.unlink()
                        logger.info(f"{str(file_path)} deleted from YT library")


class BlankLineDumper(yaml.Dumper):
    """Dump dict to YAML adding a blank line between each top-level item for readibilty."""

    def increase_indent(self, flow=False, indentless=False):
        return super(BlankLineDumper, self).increase_indent(flow, False)

    def write_line_break(self, data=None):
        if len(self.indents) == 1:
            super(BlankLineDumper, self).write_line_break()
        super(BlankLineDumper, self).write_line_break(data)


def load_yaml(path: str):
    """Load a yaml file.

    Will resolve to simplest representation, typically a dict.
    """
    try:
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"File {path} not found.")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")
        return None
