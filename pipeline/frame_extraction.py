#!/usr/bin/env python3
"""
Extracts frames from a video file and saves them as image files in a specified folder.
"""


import cv2
import os


def extract_frames(video_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not video.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    frame_count = 0

    while True:
        # Read the next frame from the video
        ret, frame = video.read()

        # If we reached the end of the video, break out of the loop
        if not ret:
            break

        # Save the current frame as an image file
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    # Release the video capture object
    video.release()
    print(f"Extracted {frame_count} frames to {output_folder}")


if __name__ == "__main__":
    # Example usage
    video_path = '20p.mp4'
    output_folder = 'image_frames'
    extract_frames(video_path, output_folder)