import os
import cv2
from skimage.metrics import structural_similarity as ssim

# Folder paths
folder1 = 'combined_video_frames/images'
folder2 = 'subset_combined_video_frames'

# Function to load images
def load_image(filepath):
    img = cv2.imread(filepath)
    if img is None:
        raise ValueError(f"Image at {filepath} could not be loaded.")
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Function to compare two images using SSIM
def compare_images(img1, img2):
    return ssim(img1, img2)

# Adjusted sorting function to handle filenames
images_folder1 = sorted(os.listdir(folder1), key=lambda x: int(x.split('_')[-1].split('.')[0]))
images_folder2 = sorted(os.listdir(folder2), key=lambda x: int(x.split('_')[-1].split('.')[0]))

# Dictionary to store the matching indices
matches = {}

# Loop over images in folder1 and compare with images in folder2
for img1_name in images_folder1:
    img1_path = os.path.join(folder1, img1_name)
    img1 = load_image(img1_path)


    for img2_name in images_folder2:
        img2_path = os.path.join(folder2, img2_name)
        img2 = load_image(img2_path)

        # Compare the images
        similarity = compare_images(img1, img2)

        if similarity > 0.99:  # Threshold for matching
            print(f"Image {img1_name} in folder1 matches with {img2_name} in folder2.")
            matches[img1_name] = img2_name
            
            break  # Stop after finding a match

    print(img1_name)

# Output the matching results
print("Matches found:", matches)


