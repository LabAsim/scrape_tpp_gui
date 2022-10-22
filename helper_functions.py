import argparse
import os.path
import pathlib
import random
import re
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from tkinter import messagebox

from misc import themes_paths

headers_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36,"
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30"]


def close_tkinter(root):
    if messagebox.askokcancel(title="Quit", message="Do you want to quit?"):
        root.destroy()
        print('close_tkinter(): Tkinter window is exiting')
        sys.exit()

def date_to_unix(date):
    """
    Converts and returns the date to unix timestamp
    :param date: Date in various forms
    :return: Unix timestamp
    See also:
        examples: https://www.devdungeon.com/content/working-dates-and-times-python-3
    Python docs:
        time: https://docs.python.org/3/library/time.html
        datetime: https://docs.python.org/3/library/datetime.html
    """
    # Make sure it's a string. Date is a tuple containing the date and an integer from sorting function (sortby())
    date = str(date[0])
    # If the date is in the form of "Πριν 6 ώρες/λεπτά"
    if re.match('[Ππ]ρ[ιίΙ]ν', date):
        print(f"date: {date}")
        # Remove 'Πριν/πριν'
        # See docs: https://docs.python.org/3/library/re.html#re.sub
        date = re.sub(pattern='[Ππ]ρ[ιίΙ]ν', repl="", string=date).lstrip(' ')
        if 'λεπτά' in date:  # "2 λεπτά"
            date_now = datetime.now()
            date = date.strip('Πριν').strip("λεπτά").strip()
            date = float(date)
            unix_date = date_now - timedelta(minutes=date)
            unix_date = time.mktime(unix_date.timetuple())
            return unix_date
        elif 'ώρ' in date:  # "2 ώρες / ώρα"
            date_now = datetime.now()
            date = date.strip('Πριν').strip("ώρα").strip("ώρες").strip()
            date = float(date)
            unix_date = date_now - timedelta(hours=date)
            unix_date = time.mktime(unix_date.timetuple())
            return unix_date
        elif 'δευ' in date:  # "39 δευτερόλεπτα"
            date_now = datetime.now()
            date = date.split(' ')
            date = float(date[0])
            unix_date = date_now - timedelta(seconds=date)
            unix_date = time.mktime(unix_date.timetuple())
            return unix_date
        else:  # '1 ημέρα'
            date_now = datetime.now()
            date = date.split(' ')
            date = float(date[0])
            unix_date = date_now - timedelta(days=date)
            unix_date = time.mktime(unix_date.timetuple())
            return unix_date
    else:  # Date is in the form of "19/10/22"
        date = date.split('/')
        year = int(date[-1])
        month = int(date[1])
        day = int(date[0])
        unix_date = datetime(year, month, day)
        unix_date = time.mktime(unix_date.timetuple())
        return unix_date


def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child)
            for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    # data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # Switch the heading, so it will be sorted  in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col,
                                                     int(not descending)))


def file_exists(dir_path, name) -> bool:
    """Returns true if the path exists"""
    path_to_name = pathlib.Path(os.path.join(dir_path, name))
    if path_to_name.exists():
        return True
    else:
        return False


def headers() -> dict[str, str]:
    """Picks and returns a random user agent from the list"""
    header = {'User-Agent': random.choice(headers_list)}
    print(f'Random header: {header}')
    return header


def callback(url):
    """Opens the url in the browser"""
    webbrowser.open_new_tab(url)


def center(window, parent_window=None):
    """
    https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
    :param window: The window to be centered
    :param parent_window: A toplevel or root
    """
    if not parent_window:
        window.update_idletasks()
        width = window.winfo_width()
        frm_width = window.winfo_rootx() - window.winfo_x()
        win_width = width + 2 * frm_width
        height = window.winfo_height()
        titlebar_height = window.winfo_rooty() - window.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = window.winfo_screenwidth() // 2 - win_width // 2
        y = window.winfo_screenheight() // 2 - win_height // 2
        window.geometry('+{}+{}'.format(x, y))
        window.deiconify()
        print(f"Window: {window} centered according to the width and the height of the screen")
    else:
        window.update_idletasks()
        width_parent = parent_window.winfo_width()
        height_parent = parent_window.winfo_height()
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
        x_dif = width_parent // 2 - size[0] // 2
        y_dif = height_parent // 2 - size[1] // 2
        window.geometry('+{}+{}'.format(parent_x + x_dif, parent_y + y_dif))
        print(f"Window: {window} centered according to the {parent_window} width and height")


def str2bool(v: bool | int | str) -> bool:
    """
    Convert a string to a boolean argument
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if isinstance(v, bool):
        return v
    elif isinstance(v, int):
        if v == 1:
            return True
        elif v == 0:
            return False
    elif v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean or equivalent value expected.')


def tkinter_theme_calling(root):
    """
    Registers the themes to tkinter instance
    :param root: tkinter.Tk()
    :return: None
    """
    # https://rdbende.github.io/tkinter-docs/tutorials/how-to-use-themes.html
    root.tk.call('source', themes_paths["azure"])  # https://github.com/rdbende/Azure-ttk-theme
    root.tk.call('source', themes_paths["plastik"])
    root.tk.call('source', themes_paths['radiance'])
    root.tk.call('source', themes_paths['aquativo'])
    root.tk.call('source', themes_paths['adapta'])
    root.tk.call('source', themes_paths['yaru'])
    root.tk.call('source', themes_paths['arc'])
    root.tk.call("set_theme", "dark")
