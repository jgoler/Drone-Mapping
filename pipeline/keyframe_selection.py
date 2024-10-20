#!/usr/bin/env python3
"""
Code for selecting keyframes from a video
"""


import os
import numpy as np


def select_keyframes(input_folder, output_folder, percentage, algorithm=""):
    # get list of all frames in order
    frames = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".jpg") or f.endswith(".png")]
    try:
        frames.sort(key=lambda f: int(os.path.basename(f).split("_")[1].split(".")[0]))
    except:
        print("Frames not numbered, sorting by filename")
        frames.sort(key=lambda f: os.path.basename(f).split(".")[0])

    # run frame selection algorithm
    num_frames = int(len(frames) * percentage)
    if algorithm == "n":
        # select evenly spaced frames
        frame_indices = np.linspace(0, len(frames) - 1, num_frames, dtype=int)
    else:
        # select a random fraction of frames, but keep them in their original order
        frame_indices = np.random.choice(len(frames), size=num_frames, replace=False)
        frame_indices.sort()
    selected_frames = [frames[i] for i in frame_indices]

    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # copy the selected frames to the output folder
    for i, frame in enumerate(selected_frames):
        filename = os.path.basename(frame)
        output_filename = os.path.join(output_folder, filename)
        os.system(f"cp {frame} {output_filename}")
    
    # return the indices of the selected frames for the future when we analyze different algorithms
    return frame_indices