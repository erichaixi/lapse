from .utils import video_format_to_codec, video_format_to_extension

import cv2
import glob

class TimeLapseCreator:
    def __init__(self, logger, cfg, update_progress_bar):
        self.logger = logger
        self.cfg = cfg
        self.update_progress_bar = update_progress_bar

    def get_input_filenames(self):
        input_dir = f'{self.cfg["input folder"]}/*'
        filenames = glob.glob(input_dir)
        assert len(filenames) > 0, f"{input_dir} contains no files"
        self.logger.debug(filenames)
        
        return filenames

    def get_dimensions(self, filename):
        img = cv2.imread(filename)
        height, width, layers = img.shape

        x_factor = width / self.cfg['output width']
        y_factor = height / self.cfg['output height']

        if x_factor >= y_factor and x_factor > 1.0:
            height = round(height / x_factor)
            width  = round(width  / x_factor)
        elif y_factor >= x_factor and y_factor > 1.0:
            height = round(height / y_factor)
            width  = round(width  / y_factor)

        dimensions = (width,height)
        self.logger.debug(f"Dimensions: {dimensions}")
        return dimensions

    def run(self):
        # TODO: Progress Bar
        video_format = self.cfg["output format"]
        video_codec = video_format_to_codec(video_format)
        video_extension = video_format_to_extension(video_format)

        input_filenames = self.get_input_filenames()
        output_filename = f"{self.cfg['output folder']}/{self.cfg['output file']}.{video_extension}"

        dimensions = self.get_dimensions(input_filenames[0])

        self.logger.debug(f"Creating video writer, "\
                          f"output path={output_filename}, "\
                          f"codec={video_codec}, "\
                          f"fps={self.cfg['fps']}, "\
                          f"dimensions={dimensions}")

        self.logger.debug(f"Writing to {output_filename}, codec={video_codec}")

        video_fourcc = 0 if video_codec == 0 else cv2.VideoWriter_fourcc(*video_codec)
        output_video = cv2.VideoWriter(output_filename, 
                                       video_fourcc,
                                       self.cfg['fps'],
                                       dimensions)

        if not output_video.isOpened():
            print("Failed to open video writer")
            return False

        for idx, filename in enumerate(input_filenames):
            self.logger.debug(f"{idx+1} / {len(input_filenames)}")
            img = cv2.imread(filename)
            img = cv2.resize(img, dimensions)
            output_video.write(img)

            progress = (idx + 1) / len(input_filenames) * 100
            self.update_progress_bar(progress)

        output_video.release()
        return True