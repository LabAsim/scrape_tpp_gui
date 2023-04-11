"""
This module contains the class for the loading window when fetching news etc.
"""
import sys
import threading
import time
from tkinter import ttk
import tkinter as tk
import tktooltip
from scrape_tpp_gui.helper_functions import center
from scrape_tpp_gui.source.classes.generictoplevel import GenericToplevel
from typing import Callable, Union


def loading_tooltip(widget: tk.Tk | tk.Widget | tk.Toplevel | list[Union[tk.Tk | tk.Widget | tk.Toplevel]],
                    func: Callable, msg="Loading..", delay=0.001):
    """
    Loads a tooltip which follows the cursor, calls the function and then destroys the tooltip.

    :param widget: The widget to be followed by the Tooltip
    :param func: The function to be called
    :param msg: The message to be displayed in the tooltip
    :param event: The tkinter event (mouse clicks, buttons etc.)
    :param delay: The delay of the tooltip
    :return: None
    """
    if not isinstance(widget, list):
        tooltip = tktooltip.ToolTip(widget, msg=msg, delay=delay)
        func()
        tooltip.self_destroy_handler()
    else:
        tooltip = tktooltip.ToolTip(widget, msg=msg, delay=delay)
        for number, item in enumerate(widget):
            if number == 0:
                func()
        tooltip.self_destroy_handler()


if __name__ == "__main__":
    # An example for the tooltip
    root = tk.Tk()
    toplevel = tk.Toplevel(root)


    def fibonacci(numbers):
        number0 = 0
        number1 = 1
        count = 0
        while count < numbers:

            time.sleep(0.001)
            new_number = number0 + number1
            number0, number1 = number1, new_number
            count += 1


    center(root)
    thread = threading.Thread(target=lambda: loading_tooltip([root, toplevel], func=lambda: fibonacci(500)))
    thread.start()
    root.mainloop()
