from .config_manager import ConfigManager
from .config import Config
from .time_lapse_creator import TimeLapseCreator
from .utils import get_photos_in_folder

from PIL import Image, ImageTk, ImageOps
import tkinter as tk
import tkinter.font
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import glob

FONT_SIZE = 14

class GUI:
    def validate_fields(self):
        # Check input folder
        self.cfg['input folder'] = self.input_dir_entry['text'].strip()
        if not os.path.exists(self.cfg['input folder']):
            messagebox.showerror("Error", f'Input folder does not exist: "{self.cfg["input folder"]}"')
            return False
        elif not glob.glob(self.cfg['input folder'] + "/*"):
            messagebox.showerror("Error", f'Input folder is empty: "{self.cfg["input folder"]}"')
            return False

        # Check output folder
        self.cfg['output folder'] = self.output_dir_entry['text'].strip()
        if not os.path.exists(self.cfg['output folder']):
            messagebox.showerror("Error", f'Output folder does not exist: "{self.cfg["output folder"]}"')
            return False

        # Check video length
        try:
            self.cfg['length'] = (float)(self.video_length_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video length must be a number: "{self.video_length_entry.get().strip()}"')
            return False
        if self.cfg['length'] <= 0:
            messagebox.showerror("Error", f'Video length must be a positive number: "{self.cfg["length"]}"')
            return False

        # Check video dimension
        try:
            self.cfg['output width'] = (int)(self.video_w_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video width must be a positive number')
            return False
        if self.cfg['output width'] <= 0:
            messagebox.showerror("Error", f"Video width must be a positive number")
            return False

        try:
            self.cfg['output height'] = (int)(self.video_h_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", f'Video height must be an integer: "{self.video_h_entry.get().strip()}"')
            return False
        if self.cfg['output height'] <= 0:
            messagebox.showerror("Error", f"Video height must be a positive number")
            return False

        return True

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

    def update_progress_bar(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def click_button_run(self):
        self.logger.debug("Click self.button_run")

        if not self.validate_fields():
            return

        if not self.cfg_manager.save(self.cfg):
            # display error notification
            pass

        message = self.create_time_lapse_message(self.cfg)
        rc = messagebox.askyesno("Create Time Lapse", message)
        if rc == tk.YES:
            lapse = TimeLapseCreator(self.logger, self.cfg, self.update_progress_bar)
            lapse.run()
            self.logger.debug("Created time lapse")
            messagebox.showinfo("Finished", "Time lapse created.")
            os.startfile(self.cfg['output folder'])
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

    def show_io_notification(self, message):
        self.io_notification_label.config(text=message)
        self.io_notification_label.pack()

    def hide_io_notification(self):
        self.io_notification_label.pack_forget()
        self.io_notification_label.config(text='')

    def update_num_photo_counter(self, folder=None):
        if folder:
            photos = get_photos_in_folder(folder)
            num_photos = len(photos)
            self.num_photos_counter_label.config(
                text=f"{num_photos} images"
            )

            self.update_photo_preview(folder)
        else:
            self.num_photos_counter_label.config(
                text=f"0 images"
            )

    def update_photo_preview(self, folder=None):
        self.photo_preview_container.delete(1.0, 'end')
        self.photo_preview_container.images.clear()

        if folder:
            photo_paths = get_photos_in_folder(folder)

            if not photo_paths:
                return

            if self.selected_sort_method.get() == "Creation Time":
                photo_paths = sorted(photo_paths, key=os.path.getctime)
            else:
                photo_paths = sorted(photo_paths)

            for idx, image_file_path in enumerate(photo_paths):
                img = Image.open(image_file_path)

                if idx == 0:
                    video_width, video_height = img.size

                img = ImageOps.fit(img, (128, 128), method = Image.ANTIALIAS,
                   bleed = 0.0, centering =(0.5, 0.5))
                img = ImageTk.PhotoImage(img)

                # self.photo_preview_container.insert('insert', image_file_path+'\n')
                self.photo_preview_container.image_create('insert', padx=5, pady=5, image=img)
                self.photo_preview_container.images.append(img)  # Keep a reference.
                # self.photo_preview_container.insert('insert', '\n')
            
            if self.cfg['use_loaded_photo_size']:
                self.update_video_resolution(video_width, video_height)

    def update_video_resolution(self, width, height):
        self.video_w_entry.delete(0, 'end')
        self.video_w_entry.insert(0, width)
        self.video_h_entry.delete(0, 'end')
        self.video_h_entry.insert(0, height)

        self.cfg['output width'] = width
        self.cfg['output height'] = height

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
        self.input_dir_button = tk.Button(
            frame_input_dir_button,
            text="Browse",
            command=self.clicked_input_dir_button,
            bg='#75FF5A'
        )
        self.input_dir_button.pack()

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
        self.output_dir_button = tk.Button(
            frame_output_dir_button,
            text="Browse",
            command=self.clicked_output_dir_button,
            bg='#75FF5A'
        )
        self.output_dir_button.pack()

        # Notification row
        frame_io_notification_label = tk.Frame(container)
        frame_io_notification_label.grid(row=3, column=1)
        self.io_notification_label = tk.Label(frame_io_notification_label, anchor='w')

        container.pack()

    def is_float_callback(self, P):
        try:
            if P == '' or P == '.':
                return True

            float(P)
            return True
        except:
            return False

    def is_int_callback(self, P):

        return P == '' or str.isnumeric(P)

    def init_time_lapse_options(self, container):
        ROWS = [
            'length',
            'width',
            'height'
        ]

        vcmd_is_float = container.register(self.is_float_callback)
        vcmd_is_int = container.register(self.is_int_callback)

        # Video duration
        frame_video_length_label = tk.Frame(container)
        frame_video_length_label.grid(
            row=ROWS.index('length'),
            column=0,
            sticky='w'
        )
        video_length_label = tk.Label(
            frame_video_length_label,
            text="Video Length (sec):",)
        video_length_label.pack()

        frame_video_length_entry = tk.Frame(container)
        frame_video_length_entry.grid(row=0, column=1)
        self.video_length_entry = tk.Entry(
            frame_video_length_entry,
            width=5,
            validate='key',
            validatecommand = (vcmd_is_float, '%P')
        )
        self.video_length_entry.pack()

        # Dimensions
        frame_video_w_label = tk.Frame(container)
        frame_video_w_label.grid(
            row=ROWS.index('width'),
            column=0,
            sticky='w'
        )
        video_w_label = tk.Label(
            frame_video_w_label,
            text="Video Width (px):",
        )
        video_w_label.pack()

        frame_video_w_entry = tk.Frame(container)
        frame_video_w_entry.grid(row=1, column=1)
        self.video_w_entry = tk.Entry(
            frame_video_w_entry,
            width=5,
            validate='key',
            validatecommand = (vcmd_is_int, '%P')
        )
        self.video_w_entry.insert(0, self.cfg['output width'])
        self.video_w_entry.pack()

        frame_video_h_label = tk.Frame(container)
        frame_video_h_label.grid(
            row=ROWS.index('height'),
            column=0,
            sticky='w'
        )
        video_h_label = tk.Label(
            frame_video_h_label,
            text="Video Height (px):",
        )
        video_h_label.pack()

        frame_video_h_entry = tk.Frame(container)
        frame_video_h_entry.grid(row=2, column=1)
        self.video_h_entry = tk.Entry(
            frame_video_h_entry,
            width=5,
            validate='key',
            validatecommand = (vcmd_is_int, '%P')
        )
        self.video_h_entry.insert(0, self.cfg['output height'])
        self.video_h_entry.pack()

        container.pack(fill="both", expand="yes")

    def init_photo_preview(self, container):
        frame_photo_preview_container = tk.Frame(container)
        frame_photo_preview_container.grid(row=0, column=0)
        self.photo_preview_container = tk.scrolledtext.ScrolledText(
            frame_photo_preview_container,
            width=52
        )
        self.photo_preview_container.pack(side='top', fill='both')
        self.photo_preview_container.images = []

        # Num photos counter
        frame_num_photos_counter_label = tk.Frame(container)
        frame_num_photos_counter_label.grid(row=1, column=0, sticky='w')
        self.num_photos_counter_label = tk.Label(
            frame_num_photos_counter_label,
            anchor='w',
            width=30
        )

        self.update_num_photo_counter()
        self.num_photos_counter_label.pack(fill='x', expand='yes')

        # Sort method
        SORT_METHODS = [
            "Name",
            "Creation Time"
        ]

        frame_sort_method_dropdown = tk.Frame(container)
        frame_sort_method_dropdown.grid(row=2, column=0, sticky='w')
        self.sort_method_dropdown = tk.OptionMenu(
            frame_sort_method_dropdown,
            self.selected_sort_method,
            *SORT_METHODS,
            command=self.sort_method_changed
        )
        self.sort_method_dropdown.pack(side='right')

        label_sort_method_dropdown = tk.Label(
            frame_sort_method_dropdown,
            text="Sort by:"
        )
        label_sort_method_dropdown.pack(side='left')

    def sort_method_changed(self, choice):
        if 'input folder' in self.cfg:
            self.update_photo_preview(self.cfg['input folder'])

    def init_grid(self):
        self.root = tk.Tk()
        self.root.title("Time Lapse Creator")

        self.selected_sort_method = tk.StringVar()
        self.selected_sort_method.set("Name")

        tk.font.nametofont("TkDefaultFont").configure(size=FONT_SIZE)
        tk.font.nametofont("TkTextFont").configure(size=FONT_SIZE)

        left_root_frame = tk.Frame(self.root)
        left_root_frame.pack(side='left')
        # left_root_frame.grid(row=0, column=0, sticky='nw')
        right_root_frame = tk.Frame(self.root)
        right_root_frame.pack(side='right')
        # right_root_frame.grid(row=0, column=1)


        # Create photo preview
        self.init_photo_preview(right_root_frame)

        # Input/Output folders
        io_selection_frame = tk.LabelFrame(
            left_root_frame,
            text="Input/Output Selection")
        self.init_input_output_folders(io_selection_frame)

        # Time Lapse options
        time_lapse_options_frame = tk.LabelFrame(
            left_root_frame,
            text="Time Lapse Options")
        self.init_time_lapse_options(time_lapse_options_frame)

        # Space above create time lapse button
        dummy_label = tk.Label(left_root_frame, height=6)
        dummy_label.pack()

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            left_root_frame,
            orient='horizontal',
            length=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x')

        # Create Time Lapse button
        self.button_run = tk.Button(
            left_root_frame,
            text="Create Time Lapse",
            command=self.click_button_run,
            bg='#75FF5A'
        )
        self.button_run.pack(expand='yes', fill='y')

        if 'input folder' in self.cfg:
            self.update_num_photo_counter(self.cfg['input folder'])

    def __init__(self, logger):
        self.logger = logger
        self.cfg_manager = ConfigManager(self.logger)
        self.cfg = self.cfg_manager.load()
        self.init_grid()
        self.root.mainloop()