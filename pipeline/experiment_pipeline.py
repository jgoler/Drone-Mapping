#!/usr/bin/env python3
"""
Python code for keyframe extraction

Extracts frames from a video file and saves them as image files in a specified folder.
Selects keyframes from the extracted frames based on a specified percentage and a specified algorithm.

Runs using system python3 by default
Run with own python interpreter if needed

Algorithms:
n - evenly spaced frames
r - randomly selected frames
"""

import os
from frame_extraction import extract_frames
from keyframe_selection import select_keyframes
from utils import get_config, get_immediate_subdirectories, export_to_txt


def main():
    # collect paths
    config = get_config()
    repo_path = config["repo"]
    video_paths = config["videos"]
    percentages = config["percentages"]  # what percent of frames to select
    algorithms = config["algorithms"]

    # extract frames and select keyframes
    FRAMES_FOLDER = os.path.join(repo_path, "data", "frames")
    KF_FOLDER = os.path.join(repo_path, "data", "keyframes")
    for video_path in video_paths:
        if video_path == "":
            continue
        extract_frames(
            video_path, os.path.join(FRAMES_FOLDER, os.path.basename(video_path).split(".")[0])
        )

    # get frame folders for each video and select keyframes according to desired percentages and algorithms
    vid_frame_folders = get_immediate_subdirectories(FRAMES_FOLDER)
    kf_folder_paths = []
    processed_folder_paths = []  # output folders for Colmap (ns-process) processing
    for vid_frame_folder in vid_frame_folders:
        for percent in percentages:
            for algorithm in algorithms:
                frame_folder_path = os.path.join(FRAMES_FOLDER, vid_frame_folder)
                video_name = os.path.basename(vid_frame_folder)
                kf_folder_path = os.path.join(KF_FOLDER, video_name, f"{percent}p_{algorithm}")
                processed_folder_path = os.path.join(
                    repo_path, "data", "processed", video_name, f"{percent}p_{algorithm}"
                )
                # check if keyframes already selected (i.e. kf folder already exists)
                if os.path.exists(kf_folder_path):
                    print(f"Keyframes already exist in '{kf_folder_path}'")
                else:
                    # if not, run keyframe selection algorithm
                    fraction = percent / 100
                    kf_idxs = select_keyframes(
                        frame_folder_path, kf_folder_path, fraction, algorithm
                    )
                    print(f"Successfully added keyframes to '{kf_folder_path}'")
                kf_folder_paths.append(kf_folder_path)
                processed_folder_paths.append(processed_folder_path)

    # export to txt
    export_to_txt(kf_folder_paths, "kf_folders.txt")
    export_to_txt(processed_folder_paths, "processed_folders.txt")


if __name__ == "__main__":
    main()
