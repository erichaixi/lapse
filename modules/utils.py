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