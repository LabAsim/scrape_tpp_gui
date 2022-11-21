"""
A toplevel asking the user to update the application
"""
import os.path
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
import psutil

parent_folder = os.path.dirname(__file__)
parent_of_parent_folder = os.path.dirname(parent_folder)
sys.path.append(parent_of_parent_folder)
from helper_functions import center
from classes.ShowInfo import ShowInfo
from PIL import Image, ImageTk
import PIL.Image
#from misc import dir_path


class AskUpdate(tk.Toplevel):
    """
    A toplevel window for updating the application.
    """
    x = 290
    y = 110

    def __init__(self, controller, root):
        super().__init__()
        self.geometry(f'{AskUpdate.x}x{AskUpdate.y}')  # Here, self is tkinter.Toplevel
        self.controller = controller
        self.root = root
        self.grab_set()
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.initUI()
        self.setActive()
        dir_path = os.path.dirname(os.path.realpath(__file__))  # The relative is like this: ./classes
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            dir_path = os.path.dirname(os.path.realpath(sys.executable))
            print("Exe:", dir_path)
        elif __file__:
            dir_path = os.path.dirname(__file__)
            print(f'Script: {dir_path}')
        self.dir_path = dir_path  # The directory containing the executable. See above for the real folder.
        print(self.dir_path)
        center(self)  # Center according to the screen's x,y, not self.root's.

    def initUI(self):
        """
        Constructs the window.
        """
        self.title("Update")
        askquit_topframe = ttk.Frame(self.big_frame)
        askquit_topframe.pack(side='top', expand=True)
        valuelabel = ttk.Label(askquit_topframe, text="A new update was found."
                                                      "\nDo you want to download the update?")
        valuelabel.pack(side='right', expand=True)
        image = Image.open(os.path.join(parent_of_parent_folder, "images/questionmark.png"))
        image = image.resize(
            (int(self.winfo_width() * 25), int(self.winfo_height() * 25)), PIL.Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(askquit_topframe, image=image)
        image_label.pack(side='left', expand=True, padx=10, pady=10)
        image_label.image = image
        buttons_frame = ttk.Frame(self.big_frame)
        buttons_frame.pack(side='bottom', expand=True)
        ok_button = ttk.Button(buttons_frame, text="Ok", command=self.download_and_quit)
        ok_button.pack(side='left', expand=True, pady=10, padx=10)
        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side='right', expand=True, pady=10, padx=10)

    def download_and_quit(self):
        """
        Downloads the update to the same folder as the running executable.
        :return: None
        """
        current_pid = os.getpid()
        current_process = psutil.Process(current_pid)
        children_of_current = current_process.children(recursive=True)
        children_of_current.append(current_process)
        current_own_process = {child.name(): child.pid for child in children_of_current}
        print(f'tk.TK() processes: {current_own_process}')

        # Open updater.exe
        parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # It's a temp dir.
        bat_file = os.path.join(parent_dir, 'source\\updater\\start_updater.bat')
        path_to_the_exe = os.path.join(parent_dir, 'source\\updater\\updater.exe')
        str_dump = f'''
                        \nstart "" "{path_to_the_exe}" --path {self.dir_path} --parentpid {current_pid}
                        \nexit
                    '''
        with open(bat_file, 'w+') as file:
            file.write(str_dump)
            print(f"file is written: {bat_file}")

        # Multiprocessing Process does not survive sys.exit() from main Process. It needs subprocess Popen
        # See: https://stackoverflow.com/questions/21665341/python-multiprocessing-and-independence-of-children-processes
        try:
            subprocess.Popen(bat_file)
            print(f"Updating process started from {path_to_the_exe}")
        except Exception as err:
            print(err)
            time.sleep(2)
        else:  # Destroy AskUpdate toplevel
            self.toplevel_quit()
        '''if self.controller:
            self.controller.exit_the_program()
        else:
            self.toplevel_quit()'''

    def toplevel_quit(self, widget=None):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            if widget is tk.Tk:
                print(f'AskQuit>toplevel_quit: Root is now exiting')
                sys.exit()
            else:
                self.destroy()
                widget.destroy()
                print(f'AskQuit>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'AskQuit>toplevel_quit: {self} is now destroyed')

    def setActive(self):
        """
        https://stackoverflow.com/questions/15944533/how-to-keep-the-window-focus-on-new-toplevel-window-in-tkinter
        """
        self.big_frame.lift()
        self.big_frame.focus_force()
        self.big_frame.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    AskUpdate(controller=None, root=root)
    root.mainloop()
