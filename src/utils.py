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

format_dict = {
    "avi": {
        "codec": "DIVX",
        "extension": "avi"
    },
    "mp4": {
        "codec": "mp4v",
        "extension": "mp4"
    },
    "avi(raw)": {
        "codec": 0,
        "extension": "avi"
    }
}

def video_format_to_codec(video_format):
    return format_dict[video_format]["codec"] if video_format in format_dict else "DIVX"

def video_format_to_extension(video_format):
    return format_dict[video_format]["extension"] if video_format in format_dict else "avi"