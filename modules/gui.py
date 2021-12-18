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

    def click_button_input_folder(self):
        self.logger.debug("Click self.button_input_folder")

        if 'input folder' in self.cfg:
            folder = filedialog.askdirectory(initialdir=self.cfg['input folder'])
        else:
            folder = filedialog.askdirectory()
        
        self.logger.debug("Selected input folder: \"{folder}\"")
        if folder:
            self.entry_input_folder.delete(0, tk.END)
            self.entry_input_folder.insert(0, folder)
            self.cfg['input folder'] = folder

            self.logger.debug("Set input folder")

            if not self.cfg_manager.save(self.cfg):
                # display error notification
                pass

    def click_button_output_folder(self):
        self.logger.debug("Click self.button_output_folder")
        
        if 'output folder' in self.cfg:
            folder = filedialog.askdirectory(initialdir=self.cfg['output folder'])
        else:
            folder = filedialog.askdirectory()

        self.logger.debug("Selected output folder: \"{folder}\"")
        if folder:
            self.entry_output_folder.delete(0, tk.END)
            self.entry_output_folder.insert(0, folder)
            self.cfg['output folder'] = folder

            self.logger.debug("Set output folder")

            if not self.cfg_manager.save(self.cfg):
                # display error notification
                pass

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

    

    def __init__(self, logger):
        self.logger = logger
        self.cfg_manager = ConfigManager(self.logger)
        self.cfg = self.cfg_manager.load()
        self.init_grid()