"""
This module contains the class for the loading window when fetching news etc.
"""
import threading
import time
from tkinter import ttk
import tkinter as tk
import tktooltip
from scrape_tpp_gui.helper_functions import center
from scrape_tpp_gui.source.classes.generictoplevel import GenericToplevel
from typing import Callable


def tooltip_handler_thread(widget: tk.Tk | tk.Widget | tk.Toplevel, func: Callable, msg="Loading..", event=None):
    """
    Starts a separate thread for the tooltip to appear and the func to be called. This is implemented so as the main gui
    not to be frozen during the execution of the func (for example during search the keyword in the database).
    :param widget: The widget to be followed by the Tooltip
    :param func: The function to be called
    :param msg: The message to be displayed in the tooltip
    :param event: The tk event
    :return: None
    """
    search_thread = threading.Thread(target=lambda: loading_tooltip(widget=widget, func=func, msg=msg))
    search_thread.start()


def loading_tooltip(widget: tk.Tk | tk.Widget | tk.Toplevel, func: Callable, msg="Loading..", event=None):
    """
    Loads a tooltip which follows the cursor, calls the function and then destroys the tooltip.
    :param widget: The widget to be followed by the Tooltip
    :param func: The function to be called
    :param msg: The message to be displayed in the tooltip
    :return: None
    """
    tooltip = tktooltip.ToolTip(widget, msg=msg, delay=0.001)
    func()
    #widget.after(10, func)
    widget.bind("<Enter>", "")
    widget.bind("<Leave>", "")
    widget.bind("<Motion>", "")
    widget.bind("<ButtonPress>", "")
    tooltip.destroy()


class GenericLoadingWindow(GenericToplevel):
    """
    A loading window used when there is going to be delay in the application.
    """
    x = 200
    y = 80

    def __init__(self, controller, root):
        super().__init__(controller=controller, root=root)
        self.root = root
        self.toplevel.withdraw()
        self.toplevel.overrideredirect(True)
        self.toplevel.geometry(f'{GenericLoadingWindow.x}x{GenericLoadingWindow.y}')
        self.toplevel.resizable(width=False, height=False)
        self.big_frame = ttk.Frame(self.toplevel)
        self.big_frame.pack(expand=True, fill='both')
        self.init_UI()
        # self.toplevel.update()
        center(self.toplevel, root)
        self.bring_focus_back()
        self.loading_tooltip(func=self.wait)

    def init_UI(self):
        """
        Creates the User Interface
        """

        self.askquit_topframe = ttk.Frame(self.big_frame)
        self.askquit_topframe.pack(side='top', expand=True)
        self.valueLabel = ttk.Label(self.askquit_topframe, text="Loading..")
        self.valueLabel.pack(expand=True)
        self.progressbar = ttk.Progressbar(self.toplevel, orient='horizontal', mode='indeterminate')
        self.progressbar.pack(side='top', pady=(10, 5))
        self.value_label = ttk.Label(self.toplevel)
        self.value_label.pack(side='bottom', expand=True)

    def loading_tooltip(self, func):
        loading_tooltip = tktooltip.ToolTip(self.root, msg='loading...', delay=0)
        func()
        self.root.bind("<Enter>", "")
        self.root.bind("<Leave>", "")
        self.root.bind("<Motion>", "")
        self.root.bind("<ButtonPress>", "")
        # print(self.root.bindtags)
        loading_tooltip.destroy()

    # @tooltip_loading_wrapper
    def wait(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    GenericLoadingWindow(controller=None, root=root)
    root.mainloop()
