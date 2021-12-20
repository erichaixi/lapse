from .config_manager import ConfigManager
from .config import Config
from .time_lapse_creator import TimeLapseCreator
from .utils import get_photos_in_folder

import tkinter as tk
import tkinter.font
from tkinter import filedialog, messagebox
import os
import glob

FONT_SIZE = 14

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

        # Check video dimension
        try:
            res['output width'] = (int)(self.video_w_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video width must be an integer: "{self.video_w_entry.get().strip()}"')
            return False
        if res['output width'] <= 0:
            messagebox.showerror("Error", f"Video width must be a positive number")
            return False

        try:
            res['output height'] = (int)(self.video_h_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video height must be an integer: "{self.video_h_entry.get().strip()}"')
            return False
        if res['output height'] <= 0:
            messagebox.showerror("Error", f"Video height must be a positive number")
            return False

        return Config(res)

    def create_time_lapse_message(self, cfg):
        '''
        # Photos:
        Video Length (sec):
        FPS:
        Resolution:
        '''
        self.logger.debug(f"Create time lapse message using: {cfg}")

        message = "Create with the following settings?\n\n"

        num_photos = len(glob.glob(cfg['input folder'] + "/*"))
        message += f"# Photos: {num_photos}\n"

        message += f"Video Length (sec): {cfg['length']}\n"

        fps = round(num_photos / cfg['length'], 2)
        message += f"FPS: {fps}\n"

        message += f"Resolution: {cfg['output width']} x {cfg['output height']}"

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
            self.update_num_photo_counter(folder)
            self.input_dir_entry.config(text=folder)
            self.cfg['input folder'] = folder

            self.logger.debug(f"Set input folder={folder}")

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
            self.output_dir_entry.config(text=folder)

            self.cfg['output folder'] = folder

            self.logger.debug(f"Set output folder={folder}")

            if not self.cfg_manager.save(self.cfg):
                # display error notification
                pass

    def show_io_notification(self, message):
        self.io_notification_label.config(text=message)
        self.io_notification_label.pack()

    def hide_io_notification(self):
        self.io_notification_label.pack_forget()
        self.io_notification_label.config(text='')

    def update_num_photo_counter(self, folder=None):
        DEFAULT_STATEMENT = "# of images in input folder: "
        if folder:
            photos = get_photos_in_folder(folder)
            num_photos = len(photos)
            self.num_photos_counter_label.config(
                text=f"{DEFAULT_STATEMENT}{num_photos}"
            )
        else:
            self.num_photos_counter_label.config(
                text=f"{DEFAULT_STATEMENT}-"
            )

    def init_grid(self):
        self.root = tk.Tk()
        self.root.title("Time Lapse Creator")

        tk.font.nametofont("TkDefaultFont").configure(size=FONT_SIZE)
        tk.font.nametofont("TkTextFont").configure(size=FONT_SIZE)

        # Input/Output folders
        io_selection_frame = tk.LabelFrame(
            self.root,
            text="Input/Output Selection")
        self.init_input_output_folders(io_selection_frame)

        # Time Lapse options
        time_lapse_options_frame = tk.LabelFrame(
            self.root,
            text="Time Lapse Options")
        self.init_time_lapse_options(time_lapse_options_frame)

        # Create Time Lapse button
        self.button_run = tk.Button(self.root, text="Create Time Lapse", command=self.click_button_run)
        self.button_run.pack()

    def init_input_output_folders(self, container):
        ## Input folder
        frame_input_dir_label = tk.Frame(container)
        frame_input_dir_label.grid(row=0, column=0)
        input_dir_label = tk.Label(
            frame_input_dir_label,
            text="Input Folder:",
            anchor='w',
            width=13)
        input_dir_label.pack()

        frame_input_dir_entry = tk.Frame(container)
        frame_input_dir_entry.grid(row=0, column=1)
        self.input_dir_entry = tk.Label(
            frame_input_dir_entry,
            width=40,
            anchor='e',
            borderwidth=2,
            relief="groove")
        if 'input folder' in self.cfg:
            self.input_dir_entry.config(text=self.cfg['input folder'])
        self.input_dir_entry.pack()

        frame_input_dir_button = tk.Frame(container)
        frame_input_dir_button.grid(row=0, column=2)
        self.input_dir_button = tk.Button(frame_input_dir_button, text="Browse", command=self.clicked_input_dir_button)
        self.input_dir_button.pack()

        # Num photos counter
        frame_num_photos_counter_label = tk.Frame(container)
        frame_num_photos_counter_label.grid(row=1, column=1)
        self.num_photos_counter_label = tk.Label(
            frame_num_photos_counter_label,
            anchor='w',
            width=40
        )
        if 'input folder' in self.cfg:
            self.update_num_photo_counter(self.cfg['input folder'])
        else:
            self.update_num_photo_counter()
        self.num_photos_counter_label.pack()

        ## Output folder
        frame_output_dir_label = tk.Frame(container)
        frame_output_dir_label.grid(row=2, column=0)
        output_dir_label = tk.Label(
            frame_output_dir_label,
            text="Output Folder:",
            anchor='w',
            width=13)
        output_dir_label.pack()

        frame_output_dir_entry = tk.Frame(container)
        frame_output_dir_entry.grid(row=2, column=1)
        self.output_dir_entry = tk.Label(
            frame_output_dir_entry,
            width=40,
            anchor='e',
            borderwidth=2,
            relief="groove")
        if 'output folder' in self.cfg:
            self.output_dir_entry.config(text=self.cfg['output folder'])
        self.output_dir_entry.pack()

        frame_output_dir_button = tk.Frame(container)
        frame_output_dir_button.grid(row=2, column=2)
        self.output_dir_button = tk.Button(frame_output_dir_button, text="Browse", command=self.clicked_output_dir_button)
        self.output_dir_button.pack()

        # Notification row
        frame_io_notification_label = tk.Frame(container)
        frame_io_notification_label.grid(row=3, column=1)
        self.io_notification_label = tk.Label(frame_io_notification_label, anchor='w')

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

        frame_video_h_label = tk.Frame(container)
        frame_video_h_label.grid(row=2, column=0)
        video_h_label = tk.Label(
            frame_video_h_label,
            text="Video Height (px):",
            anchor='w')
        video_h_label.pack()

        frame_video_h_entry = tk.Frame(container)
        frame_video_h_entry.grid(row=2, column=1)
        self.video_h_entry = tk.Entry(frame_video_h_entry, width=5)
        self.video_h_entry.pack()

        container.pack(fill="both", expand="yes")

    def __init__(self, logger):
        self.logger = logger
        self.cfg_manager = ConfigManager(self.logger)
        self.cfg = self.cfg_manager.load()
        self.init_grid()
        self.root.mainloop()