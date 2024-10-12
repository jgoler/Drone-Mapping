#!/usr/bin/env python3
"""
Code for a full experiment pipeline
"""


from frame_extraction import extract_frames
from keyframe_selection import select_keyframes


def main():
    # Experiment parameters
    VIDEO_PATH = ""
    FRAME_FOLDER = ""
    KEYFRAME_FOLDER = ""
    PERCENTAGE = 0.1
    ALGORITHM = ""


    # extract frames from video to folder
    extract_frames(VIDEO_PATH, FRAME_FOLDER)

    # select keyframes
    select_keyframes(FRAME_FOLDER, KEYFRAME_FOLDER, PERCENTAGE, ALGORITHM)

if __name__ == "__main__":
    pass