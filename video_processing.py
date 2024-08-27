# what funcitons should be put into this file: mirror, upscale, compile 


def compile_videos(video_paths, output_path):
    clips = [VideoFileClip(vp) for vp in video_paths]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path)
