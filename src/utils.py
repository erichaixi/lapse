import glob
import imghdr

def get_photos_in_folder(folder):
    filenames = glob.glob(f"{folder}/*")
    
    res = []
    for filename in filenames:
        try:
            if imghdr.what(filename):
                res.append(filename)
        except:
            continue

    return res

format_to_codec_dict = {
    "avi": "DIVX",
    "mp4": "mp4v"
}

def video_format_to_codec(video_format):
    return format_to_codec_dict[video_format] if video_format in format_to_codec_dict else "DIVX"