import assemblyai as aai
import sys
import pysrt
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

def create_subtitle(keyword):
    aai.settings.api_key = ""

    config = aai.TranscriptionConfig(language_code= "pt")

    transcript = aai.Transcriber(config=config).transcribe("output.wav")

    subtitles = transcript.export_subtitles_srt()

    f = open(keyword + "_subtitle.srt","a")
    f.write(subtitles)
    f.close()

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


def create_subtitle_clips(subtitles, videosize,fontsize=56, font='Arial', color='white', debug = False):
    subtitle_clips = []

    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time

        video_width, video_height = videosize
        
        text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color = 'Black', size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height* 4 / 5 

        text_position = (subtitle_x_position, subtitle_y_position)                    
        subtitle_clips.append(text_clip.set_position(text_position))

    return subtitle_clips

def subtitle_video(keyword):
    # Load video and SRT file
    video = VideoFileClip(keyword + ".mp4")
    create_subtitle(keyword)
    subtitles = pysrt.open(keyword + "_subtitle.srt",encoding='latin1')

    output_video_file = keyword+'_subtitled'+".mp4"

    # Create subtitle clips
    subtitle_clips = create_subtitle_clips(subtitles,video.size)

    # Add subtitles to the video
    final_video = CompositeVideoClip([video] + subtitle_clips)

    # Write output video file
    final_video.write_videofile(output_video_file)
