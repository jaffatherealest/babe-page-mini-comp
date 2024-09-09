import subprocess
import os
import tempfile

def compile_videos_ffmpeg(video_paths, output_path, target_fps=30):
    """
    Concatenates a list of videos using ffmpeg and saves the result to the output path.
    
    :param video_paths: List of video file paths to concatenate.
    :param output_path: Path where the final compiled video will be saved.
    :param target_fps: Target frame rate for the compiled video.
    """
    try:
        # Create a temporary file to store the list of video paths for ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as file_list:
            for vp in video_paths:
                file_list.write(f"file '{vp}'\n")  # Each video file needs to be listed with the format `file 'filename'`
            file_list_path = file_list.name  # Get the path to the temp file that contains the list of videos
        
        # Construct the ffmpeg command for concatenating videos
        ffmpeg_command = [
            'ffmpeg', '-y',  # Overwrite the output file if it exists
            '-f', 'concat', '-safe', '0',  # Concatenate videos listed in the file (no safety checks for file names)
            '-i', file_list_path,  # Input is the list of video files
            '-vf', f"fps={target_fps},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",  # Scale and crop to fit 1080x1920
            '-c:v', 'libx264',  # Encode with H.264 codec
            '-preset', 'fast',  # Use a fast preset for encoding
            '-crf', '22',  # Quality level (lower CRF = better quality, 22 is a good balance)
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            output_path  # Output file path
        ]
        
        # Run the ffmpeg command to compile the videos
        subprocess.run(ffmpeg_command, check=True)
        print(f"Compiled video saved to {output_path}")
        
        # Clean up the temporary file
        os.remove(file_list_path)
        
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"Error while compiling videos with ffmpeg: {e}")
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def save_video_locally(file_io, record_id):
    """
    Saves a file-like object (file_io) as a temporary video file using the record ID for naming.
    """
    try:
        # Save the file_io to a temporary directory with a unique name based on the record ID
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f"{record_id}.mp4")  # Assuming MP4 format
        with open(video_path, "wb") as video_file:
            file_content = file_io.read()
            video_file.write(file_content)  # Save the content of file_io to disk
        return video_path
    except Exception as e:
        print(f"Error while saving video locally: {e}")
        raise