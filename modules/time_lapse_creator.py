import cv2
import glob

class TimeLapseCreator:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def get_input_filenames(self):
        input_dir = f'{self.config["input folder"]}/*'
        filenames = glob.glob(input_dir)
        assert len(filenames) > 0, f"{input_dir} contains no files"
        self.logger.debug(filenames)
        
        return filenames

    def get_dimensions(self, filename):
        img = cv2.imread(filename)
        height, width, layers = img.shape

        x_factor = width / self.config['output width']
        y_factor = height / self.config['output height']

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
        input_filenames = self.get_input_filenames()
        output_filename = f"{self.config['output folder']}/{self.config['output file']}.avi"

        skip_interval = self.config['length'] / (len(input_filenames) - 1)
        fps = 1.0 / skip_interval
        self.logger.debug(f"Skip interval: {skip_interval}. Fps: {fps}")

        dimensions = self.get_dimensions(input_filenames[0])

        output_video = cv2.VideoWriter(output_filename, 
                                       cv2.VideoWriter_fourcc(*'DIVX'),
                                       fps,
                                       dimensions)

        for idx, filename in enumerate(input_filenames):
            self.logger.debug(f"{idx+1} / {len(input_filenames)}")
            img = cv2.imread(filename)
            img = cv2.resize(img, dimensions)
            output_video.write(img)

        output_video.release()