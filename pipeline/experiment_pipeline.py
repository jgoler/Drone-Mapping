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
from utils import *


def main():
    # collect paths
    input_paths = read_input_paths()
    repo_path = input_paths["repo"]
    video_paths = input_paths["videos"]
    percentages = input_paths["percentages"]  # what percent of frames to select
    algorithms = ["n", "r"]
    
    # extract frames
    FRAMES_FOLDER = os.path.join(repo_path, "data", "frames")
    KF_FOLDER = os.path.join(repo_path, "data", "keyframes")
    for video_path in video_paths:
        if video_path == "":
            continue
        extract_frames(video_path, os.path.join(FRAMES_FOLDER, os.path.basename(video_path).split(".")[0]))
    
    # get frame folders for each video and select keyframes according to desired percentages and algorithms
    vid_frame_folders = get_immediate_subdirectories(FRAMES_FOLDER)
    out_folder_paths = []
    for vid_frame_folder in vid_frame_folders:
        for percent in percentages:
            for algorithm in algorithms:
                frame_folder_path = os.path.join(FRAMES_FOLDER, vid_frame_folder)
                out_folder_path = os.path.join(KF_FOLDER, os.path.basename(vid_frame_folder), f"{percent}p_{algorithm}")
                print("frame_folder_path: ", frame_folder_path)
                print("outpath: ", out_folder_path)
                fraction = percent/100
                kf_idxs = select_keyframes(frame_folder_path, out_folder_path, fraction, "n")
                out_folder_paths.append(out_folder_path)

    # export to txt
    export_to_txt(out_folder_paths, "kf_outfolders.txt")


if __name__ == "__main__":
    main()