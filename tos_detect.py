import os
import io
import subprocess
import shutil  # Added for folder cleanup
import cv2 # not needed ?
import numpy as np
import pytesseract
from PIL import Image
import tempfile

# Modified frame extraction function to handle BytesIO
def extract_frames_from_video(video, project_folder='extracted_frames', frame_rate=1):
    frame_files = []
    
    # If video is a BytesIO object, write it to a temp file
    if isinstance(video, io.BytesIO):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video_file:
            tmp_video_file.write(video.getvalue())
            video_path = tmp_video_file.name
    else:
        video_path = video  # Assume it's a file path
    
    # Create the folder if it doesn't exist
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)
    
    try:
        # Define the output pattern for frames
        output_pattern = os.path.join(project_folder, 'frame_%04d.png')
        
        # FFmpeg command to extract frames
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'fps={frame_rate}',
            output_pattern
        ]
        
        # Run FFmpeg command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Log FFmpeg output (optional for debugging)
        print(f"FFmpeg stdout: {result.stdout.decode()}")
        print(f"FFmpeg stderr: {result.stderr.decode()}")
        
        # Collect the extracted frames
        frame_files = sorted([os.path.join(project_folder, f) for f in os.listdir(project_folder) if f.startswith('frame_') and f.endswith('.png')])
        print(f"Frames extracted to {project_folder}: {frame_files}")
        
        if not frame_files:
            raise Exception("No frames were extracted by FFmpeg")
    
    except Exception as e:
        print(f"Error during frame extraction: {e}")
    
    return project_folder  # Return project folder to pass along

def detect_text_in_frames_tesseract(project_folder):
    """
    Use Tesseract OCR to detect text in the extracted frames.
    Returns True if text is detected in any frame, otherwise False.
    """
    
    frame_files = [os.path.join(project_folder, f) for f in os.listdir(project_folder) if f.startswith('frame_') and f.endswith('.png')]
    
    for frame_file in frame_files:
        try:
            # Load the frame
            image = Image.open(frame_file)

            # Perform OCR
            text = pytesseract.image_to_string(image)

            if text:
                print(f"Text detected in {frame_file}: {text}")
                return True  # Text detected, skip video

        except Exception as e:
            print(f"Error processing frame {frame_file}: {e}")
            continue  # In case of error, just continue checking other frames

    return False  # No text detected in any frame

def cleanup_files(file_list):
    """
    Clean up temporary files.
    """
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)

# Function to clean up the project folder after processing
def cleanup_project_folder(project_folder='extracted_frames'):
    try:
        if os.path.exists(project_folder):
            shutil.rmtree(project_folder)
            print(f"Deleted folder: {project_folder}")
    except Exception as e:
        print(f"Error cleaning up folder {project_folder}: {e}")

############################################
if __name__ == "__main__":
    video_path = "/Users/jakejeffries/Downloads/bunny1.mp4"
    project_folder = extract_frames_from_video(video_path)
    # project_folder = "/Users/jakejeffries/Documents/Code/babe-page-4xdopeoverload/extracted_frames"
    if detect_text_in_frames_tesseract(project_folder):
        print("TOS detected!")
    else:
        print("No TOS detected")
############################################