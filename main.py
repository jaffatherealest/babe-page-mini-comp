# Importing functions from other modules
from gdrive import (
    authenticate_drive_api,
    download_file_from_url,
    upload_file_to_drive
)

from airtable import (
    AirtableClient
)

from tos_detect import (
    cleanup_files,
    detect_text_in_frames_tesseract,
    extract_frames_from_video,
    cleanup_project_folder
)

from video_processing import (
    compile_videos_ffmpeg,  # Changed to use the ffmpeg version
    save_video_locally
)

from config import (
    AIRTABLE_API_KEY,
    videos_table,
    tiktok_videos_view,
    bp_source_scraper_base_id
)

import tempfile
import os

def main():
    drive_service = authenticate_drive_api()

    bp_scraper_client = AirtableClient(base_id=bp_source_scraper_base_id, api_key=AIRTABLE_API_KEY)

    tiktok_records = bp_scraper_client.fetch_records(videos_table, tiktok_videos_view)

    non_tos_videos = []  # This will hold tuples of (video_path, record_id) for non-TOS videos

    for record in tiktok_records:
        download_url = record['fields'].get('DOWNLOAD URL')
        file_path = f"{record['id']}.mp4"  # Save video using record ID as the filename
        
        if not download_url:
            print(f"No download URL for record {record['id']}")
            continue

        try:
            print(f"Processing record: {record['id']}")

            # Try downloading the video
            video_data = download_file_from_url(download_url)
            print(f"Downloaded video from {download_url}, video_data type: {type(video_data)}")

            # Save video to disk
            file_path = save_video_locally(video_data, record['id'])  # Correctly save the video and return the path

            print(f"Video saved to {file_path}")

            # Extract frames from the video
            project_folder = extract_frames_from_video(file_path)
            print(f"Extracted frames from {file_path}")

            # Check for TOS violations
            if detect_text_in_frames_tesseract(project_folder):
                cleanup_project_folder(project_folder)  # Cleanup frames if TOS violation is detected
                bp_scraper_client.update_record(videos_table, record['id'], {"TOS DETECTED": True})
                print(f"TOS violation detected for {record['id']}")
                
                try:
                    # Check if the file exists and delete io
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Deleted video file: {file_path}")
                    else:
                        print(f"File not found for deletion: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
                
                continue  # Skip to the next record

            # Add non-TOS video to the list
            non_tos_videos.append({
                'record_id': record['id'],
                'file_path': file_path
            })

            # Print non-TOS videos list for debugging
            print(f"Non-TOS videos list: {non_tos_videos}")
            print(f"Length of non_tos_videos: {len(non_tos_videos)}")

            # Compile videos when we have 3 non-TOS videos
            if len(non_tos_videos) == 3:
                video_paths = [v['file_path'] for v in non_tos_videos]  # Extract file paths
                record_ids = [v['record_id'] for v in non_tos_videos]   # Extract record IDs

                output_filename = f"minicomp_{'_'.join(record_ids)}.mp4"
                output_path = os.path.join(project_folder, output_filename)

                # Check if all file paths exist
                if all(os.path.exists(path) for path in video_paths):
                    try:
                        # Compile the videos into one using ffmpeg
                        print(f"Compiling videos: {video_paths} into {output_path}")
                        compile_videos_ffmpeg(video_paths, output_path)  # Updated to use ffmpeg-based compile
                        print(f"Compilation complete. Output video saved at {output_path}")
                    except Exception as e:
                        print(f"Error during video compilation: {e}")
                        non_tos_videos.clear()
                        break  # Stop after the error

                    try:
                        # Upload the compiled video to Google Drive
                        print(f"Uploading compiled video {output_filename} to Google Drive")
                        new_google_drive_link = upload_file_to_drive(drive_service, output_path, output_filename)
                        
                        if new_google_drive_link:
                            print(f"Upload successful. Google Drive link: {new_google_drive_link}")
                            for record_id in record_ids:
                                bp_scraper_client.update_record(videos_table, record_id, {
                                    "BABE PAGE TEMPLATE USED": True
                                })
                            print(f"Records updated for: {record_ids}")
                            cleanup_project_folder(project_folder)
                            print(f"Project folder cleaned up: {project_folder}")
                        else:
                            print(f"Failed to upload compiled video to Google Drive: {output_filename}")
                    except Exception as e:
                        print(f"Error during upload to Google Drive: {e}")
                        non_tos_videos.clear()
                        break  # Stop after the error
                else:
                    print(f"One or more files do not exist in {video_paths}")

                # Clear the non-TOS videos list after processing
                non_tos_videos.clear()

                break  # Stop after creating one mini compilation video

        except Exception as e:
            print(f"Failed to process record ID: {record['id']} - Error: {e}")
            non_tos_videos.clear()  # Clear non-TOS list to prevent future issues
            break  # Stop processing after an error occurs to prevent further issues
    

if __name__ == "__main__":
    main()