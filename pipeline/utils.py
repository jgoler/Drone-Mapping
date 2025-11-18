"""
Utility functions
"""

import os
import yaml
import argparse


def safe_open(path, error_msg=None):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        if error_msg is not None:
            raise ValueError(f"File cannot be opened: {path}\nError message: {error_msg}")
        else:
            raise Warning(f"File cannot be opened: {path}")
        return ""


def read_input_paths():
    """
    Reads input paths from input_paths/repo.txt and input_paths/video_paths.txt
    *** Not using this function anymore ***
    """

    ret = dict()
    REPO_PATH = safe_open(
        "input_paths/repo.txt",
        error_msg="Repo path not found. Set repo path in input_paths/repo.txt",
    )
    REPO_PATH = REPO_PATH.strip()
    if not os.path.exists(REPO_PATH):
        raise ValueError("'{REPO_PATH}' is not a valid path. Set repo path in input_paths/repo.txt")
    ret["repo"] = REPO_PATH

    VIDEO_PATHS = safe_open("input_paths/videos.txt")
    VIDEO_PATHS = VIDEO_PATHS.strip().split("\n")
    ret["videos"] = VIDEO_PATHS

    PERCENTAGES = safe_open("input_paths/percentages.txt")
    PERCENTAGES = PERCENTAGES.strip().split("\n")
    PERCENTAGES = [float(x) for x in PERCENTAGES]
    ret["percentages"] = PERCENTAGES

    return ret


def get_config():
    """
    Load config.yaml, which contains all the relevant file paths
    """
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config


def get_immediate_subdirectories(path):
    """Returns a list of immediate subdirectories in the given path."""

    subdirectories = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            subdirectories.append(entry)
    return subdirectories


def export_to_txt(array, path):
    with open(path, "w") as f:
        for item in array:
            f.write("%s\n" % item)


def find_dataparser_transforms_file(search_dir):
    """Find the dataparser_transforms.json file in the given model directory and experiment name."""

    # Find the latest config file
    dataparser_files = []
    if not os.path.exists(search_dir):
        return ""

    for root, dirs, files in os.walk(search_dir):
        if "dataparser_transforms.json" in files:
            dataparser_files.append(os.path.join(root, "dataparser_transforms.json"))

    if not dataparser_files:
        return ""

    # Use folder name to get the latest one
    latest_file = max(dataparser_files, key=lambda x: os.path.basename(x))

    return latest_file
