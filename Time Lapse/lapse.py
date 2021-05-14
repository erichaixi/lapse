import cv2
from datetime import datetime
import glob
import json
import logging
import logging.handlers
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(
    "logs/log", maxBytes=(1048576*5), backupCount=0
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class Config:
    slots = [
        'input folder',
        'output folder',
        'length',

        'output file',
        'output height',
        'output width',
    ]

    def __init__(self, args):
        self.d = {}

        for key in args:
            self.d[key] = args[key]
                
        currDatetime = datetime.now()
        dt_string = currDatetime.strftime("%d-%m-%Y %H-%M-%S")
        self.d['output file'] = dt_string

        self.d['output height'] = 1080
        self.d['output width'] = 1920

        # Confirm all slots are filled
        for slot in self.slots:
            assert slot in self.d

        logger.debug(f"Config: {self.d}")

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, val):
        self.d[key] = val

class TimeLapse:
    def __init__(self, config):
        self.config = config

    def get_input_filenames(self):
        input_dir = f'{self.config["input folder"]}/*'
        filenames = glob.glob(input_dir)
        assert len(filenames) > 0, f"{input_dir} contains no files"
        logger.debug(filenames)
        
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
        logger.debug(f"Dimensions: {dimensions}")
        return dimensions

    def run(self):
        input_filenames = self.get_input_filenames()
        output_filename = f"{self.config['output folder']}/{self.config['output file']}.avi"

        skip_interval = self.config['length'] / (len(input_filenames) - 1)
        fps = 1.0 / skip_interval
        logger.debug(f"Skip interval: {skip_interval}. Fps: {fps}")

        dimensions = self.get_dimensions(input_filenames[0])

        output_video = cv2.VideoWriter(output_filename, 
                                       cv2.VideoWriter_fourcc(*'DIVX'),
                                       fps,
                                       dimensions)

        for idx, filename in enumerate(input_filenames):
            logger.debug(f"{idx+1} / {len(input_filenames)}")
            img = cv2.imread(filename)
            img = cv2.resize(img, dimensions)
            output_video.write(img)

        output_video.release()

class GUI:
    path_cfg = "settings.cfg"

    def save_cfg(self):
        with open(self.path_cfg, 'w') as f:
            json.dump(self.cfg, f)

    def validate_fields(self):
        res = {}

        # Check input folder
        res['input folder'] = self.entry_input_folder.get().strip()
        if not os.path.exists(res['input folder']):
            messagebox.showerror("Error", f'Input folder does not exist: "{res["input folder"]}"')
            return False
        elif not glob.glob(res['input folder'] + "/*"):
            messagebox.showerror("Error", f'Input folder is empty: "{res["input folder"]}"')
            return False

        # Check output folder
        res['output folder'] = self.entry_output_folder.get().strip()
        if not os.path.exists(res['output folder']):
            messagebox.showerror("Error", f'Output folder does not exist: "{res["output folder"]}"')
            return False

        # Check video length
        try:
            res['length'] = (float)(self.entry_video_length.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video length must be a number: "{self.entry_video_length.get().strip()}"')
            return False
        if res['length'] <= 0:
            messagebox.showerror("Error", f'Video length must be a positive number: "{res["length"]}"')
            return False

        return Config(res)

    def create_time_lapse_message(self, cfg):
        '''
        # Photos:
        Video Length (sec):
        FPS:
        Resolution:
        '''
        message = "Create with the following settings?\n\n"

        num_photos = len(glob.glob(cfg['input folder'] + "/*"))
        message += f"# Photos: {num_photos}\n"

        message += f"Video Length (sec): {cfg['length']}\n"

        fps = round(num_photos / cfg['length'], 2)
        message += f"FPS: {fps}\n"

        message += "Resolution: 1920 x 1080"

        return message

    def click_button_run(self):
        logger.debug("Click self.button_run")
        
        cfg = self.validate_fields()
        if not cfg:
            return

        message = self.create_time_lapse_message(cfg)
        rc = messagebox.askyesno("Create Time Lapse", message)
        if rc == tk.YES:
            lapse = TimeLapse(cfg)
            lapse.run()
            logger.debug("Created time lapse")
            messagebox.showinfo("Finished", "Time lapse created.")
        else:
            logger.debug("User chose not to create time lapse")

    def click_button_input_folder(self):
        logger.debug("Click self.button_input_folder")

        if 'input folder' in self.cfg:
            folder = filedialog.askdirectory(initialdir=self.cfg['input folder'])
        else:
            folder = filedialog.askdirectory()
        
        logger.debug("Selected input folder: \"{folder}\"")
        if folder:
            self.entry_input_folder.delete(0, tk.END)
            self.entry_input_folder.insert(0, folder)
            self.cfg['input folder'] = folder

            logger.debug("Set input folder")
            self.save_cfg()

    def click_button_output_folder(self):
        logger.debug("Click self.button_output_folder")
        
        if 'output folder' in self.cfg:
            folder = filedialog.askdirectory(initialdir=self.cfg['output folder'])
        else:
            folder = filedialog.askdirectory()

        logger.debug("Selected output folder: \"{folder}\"")
        if folder:
            self.entry_output_folder.delete(0, tk.END)
            self.entry_output_folder.insert(0, folder)
            self.cfg['output folder'] = folder

            logger.debug("Set output folder")
            self.save_cfg()

    def init_grid(self):
        self.root = tk.Tk()
        self.root.title("Time Lapse Creator")

        # Top Frame
        self.topframe = tk.Frame(self.root)

        ## Input folder
        self.frame_0_0 = tk.Frame(self.topframe)
        self.frame_0_0.grid(row=0, column=0)
        self.label_0_0 = tk.Label(self.frame_0_0, text="Input Folder:", anchor='w')
        self.label_0_0.pack()

        self.frame_0_1 = tk.Frame(self.topframe)
        self.frame_0_1.grid(row=0, column=1)
        self.entry_input_folder = tk.Entry(self.frame_0_1, width=40)
        if 'input folder' in self.cfg:
            self.entry_input_folder.insert(0, self.cfg['input folder'])
        self.entry_input_folder.pack()

        self.frame_0_2 = tk.Frame(self.topframe)
        self.frame_0_2.grid(row=0, column=2)
        self.button_input_folder = tk.Button(self.frame_0_2, text="Browse", command=self.click_button_input_folder)
        self.button_input_folder.pack()

        ## Output folder
        self.frame_1_0 = tk.Frame(self.topframe)
        self.frame_1_0.grid(row=1, column=0)
        self.label_1_0 = tk.Label(self.frame_1_0, text="Output Folder:", anchor='w')
        self.label_1_0.pack()

        self.frame_1_1 = tk.Frame(self.topframe)
        self.frame_1_1.grid(row=1, column=1)
        self.entry_output_folder = tk.Entry(self.frame_1_1, width=40)
        if 'output folder' in self.cfg:
            self.entry_output_folder.insert(0, self.cfg['output folder'])
        self.entry_output_folder.pack()

        self.frame_1_2 = tk.Frame(self.topframe)
        self.frame_1_2.grid(row=1, column=2)
        self.button_output_folder = tk.Button(self.frame_1_2, text="Browse", command=self.click_button_output_folder)
        self.button_output_folder.pack()

        self.topframe.pack()



        # Bot Frame
        self.botframe = tk.Frame(self.root)

        ## Video length
        self.frame_3_0 = tk.Frame(self.botframe)
        self.frame_3_0.grid(row=0, column=0)
        self.label_3_0 = tk.Label(self.frame_3_0, text="Video Length (sec):", anchor='w')
        self.label_3_0.pack()

        self.frame_3_1 = tk.Frame(self.botframe)
        self.frame_3_1.grid(row=0, column=1)
        self.entry_video_length = tk.Entry(self.frame_3_1, width=5)
        self.entry_video_length.pack()

        self.botframe.pack()

        # Run self.button
        self.button_run = tk.Button(self.root, text="Create Time Lapse", command=self.click_button_run)
        self.button_run.pack()

        self.root.mainloop()

    def init_cfg(self):
        if os.path.exists(self.path_cfg):
            with open(self.path_cfg) as f:
                self.cfg = json.load(f)
                logger.debug(f"Loaded config: {self.cfg}")
        else:
            self.cfg = {}
            logger.debug(f"No existing config")

    def __init__(self):
        self.init_cfg()
        self.init_grid()

gui = GUI()