from .config_manager import ConfigManager
from .config import Config
from .time_lapse_creator import TimeLapseCreator

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import glob

class GUI:
    def validate_fields(self):
        res = {}

        # Check input folder
        res['input folder'] = self.input_dir_entry.get().strip()
        if not os.path.exists(res['input folder']):
            messagebox.showerror("Error", f'Input folder does not exist: "{res["input folder"]}"')
            return False
        elif not glob.glob(res['input folder'] + "/*"):
            messagebox.showerror("Error", f'Input folder is empty: "{res["input folder"]}"')
            return False

        # Check output folder
        res['output folder'] = self.output_dir_entry.get().strip()
        if not os.path.exists(res['output folder']):
            messagebox.showerror("Error", f'Output folder does not exist: "{res["output folder"]}"')
            return False

        # Check video length
        try:
            res['length'] = (float)(self.video_length_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video length must be a number: "{self.video_length_entry.get().strip()}"')
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
        self.logger.debug("Click self.button_run")
        
        cfg = self.validate_fields()
        if not cfg:
            return

        message = self.create_time_lapse_message(cfg)
        rc = messagebox.askyesno("Create Time Lapse", message)
        if rc == tk.YES:
            lapse = TimeLapseCreator(self.logger, cfg)
            lapse.run()
            self.logger.debug("Created time lapse")
            messagebox.showinfo("Finished", "Time lapse created.")
        else:
            self.logger.debug("User chose not to create time lapse")

    def clicked_input_dir_button(self):
        self.logger.debug("Click self.input_dir_button")

        if 'input folder' in self.cfg:
            folder = filedialog.askdirectory(initialdir=self.cfg['input folder'])
        else:
            folder = filedialog.askdirectory()
        
        self.logger.debug("Selected input folder: \"{folder}\"")
        if folder:
            self.input_dir_entry.delete(0, tk.END)
            self.input_dir_entry.insert(0, folder)
            self.cfg['input folder'] = folder

            self.logger.debug("Set input folder")

            if not self.cfg_manager.save(self.cfg):
                # display error notification
                pass

    def clicked_output_dir_button(self):
        self.logger.debug("Click self.output_dir_button")
        
        if 'output folder' in self.cfg:
            folder = filedialog.askdirectory(initialdir=self.cfg['output folder'])
        else:
            folder = filedialog.askdirectory()

        self.logger.debug("Selected output folder: \"{folder}\"")
        if folder:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, folder)
            self.cfg['output folder'] = folder

            self.logger.debug("Set output folder")

            if not self.cfg_manager.save(self.cfg):
                # display error notification
                pass

    def init_grid(self):
        self.root = tk.Tk()
        self.root.title("Time Lapse Creator")

        # Input/Output folders
        top_frame = tk.Frame(self.root)
        self.init_input_output_folders(top_frame)

        # Time Lapse options
        time_lapse_options_frame = tk.LabelFrame(
            self.root,
            text="Time Lapse Options")
        self.init_time_lapse_options(time_lapse_options_frame)

        # Create Time Lapse button
        self.button_run = tk.Button(self.root, text="Create Time Lapse", command=self.click_button_run)
        self.button_run.pack()

        self.root.mainloop()

    def init_input_output_folders(self, container):
        ## Input folder
        frame_input_dir_label = tk.Frame(container)
        frame_input_dir_label.grid(row=0, column=0)
        input_dir_label = tk.Label(frame_input_dir_label, text="Input Folder:", anchor='w')
        input_dir_label.pack()

        frame_input_dir_entry = tk.Frame(container)
        frame_input_dir_entry.grid(row=0, column=1)
        self.input_dir_entry = tk.Entry(frame_input_dir_entry, width=40)
        if 'input folder' in self.cfg:
            self.input_dir_entry.insert(0, self.cfg['input folder'])
        self.input_dir_entry.pack()

        frame_input_dir_button = tk.Frame(container)
        frame_input_dir_button.grid(row=0, column=2)
        self.input_dir_button = tk.Button(frame_input_dir_button, text="Browse", command=self.clicked_input_dir_button)
        self.input_dir_button.pack()

        ## Output folder
        frame_output_dir_label = tk.Frame(container)
        frame_output_dir_label.grid(row=1, column=0)
        output_dir_label = tk.Label(frame_output_dir_label, text="Output Folder:", anchor='w')
        output_dir_label.pack()

        frame_output_dir_entry = tk.Frame(container)
        frame_output_dir_entry.grid(row=1, column=1)
        self.output_dir_entry = tk.Entry(frame_output_dir_entry, width=40)
        if 'output folder' in self.cfg:
            self.output_dir_entry.insert(0, self.cfg['output folder'])
        self.output_dir_entry.pack()

        frame_output_dir_button = tk.Frame(container)
        frame_output_dir_button.grid(row=1, column=2)
        self.output_dir_button = tk.Button(frame_output_dir_button, text="Browse", command=self.clicked_output_dir_button)
        self.output_dir_button.pack()

        container.pack()

    def init_time_lapse_options(self, container):
        # Video duration
        frame_video_length_label = tk.Frame(container)
        frame_video_length_label.grid(row=0, column=0)
        video_length_label = tk.Label(
            frame_video_length_label,
            text="Video Length (sec):",
            anchor='w')
        video_length_label.pack()

        frame_video_length_entry = tk.Frame(container)
        frame_video_length_entry.grid(row=0, column=1)
        self.video_length_entry = tk.Entry(frame_video_length_entry, width=5)
        self.video_length_entry.pack()

        # TODO: FPS

        # Dimensions
        frame_video_w_label = tk.Frame(container)
        frame_video_w_label.grid(row=1, column=0)
        video_w_label = tk.Label(
            frame_video_w_label,
            text="Video Width (px):",
            anchor='w')
        video_w_label.pack()

        frame_video_w_entry = tk.Frame(container)
        frame_video_w_entry.grid(row=1, column=1)
        self.video_w_entry = tk.Entry(frame_video_w_entry, width=5)
        self.video_w_entry.pack()

        container.pack(fill="both", expand="yes")

    def __init__(self, logger):
        self.logger = logger
        self.cfg_manager = ConfigManager(self.logger)
        self.cfg = self.cfg_manager.load()
        self.init_grid()