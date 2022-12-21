"""
Contains the classes for the user-application interaction regarding webdriver (chromedriver) and Chrome.
"""
import ctypes
import os
import pathlib
import subprocess
import sys
import time
import tkinter as tk
import webbrowser
from tkinter import ttk
import PIL
import requests
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zipfile import ZipFile

from scrape_tpp_gui.helper_functions import str2bool, tkinter_theme_calling, center

# import scrape_tpp_gui.helper_functions.center
parent_folder = os.path.dirname(__file__)
parent_of_parent_folder = os.path.dirname(parent_folder)
sys.path.append(parent_of_parent_folder)
sys.path.append(parent_folder)

from classes.search_software import InstalledSoftware
import xml.etree.ElementTree as ET


class WarningDoesNotExists(tk.Toplevel):
    """
    Warn
    """
    url_chrome = 'https://www.google.com/chrome/'
    url_chromedriver = 'https://sites.google.com/chromium.org/driver/'
    path_to_desktop = os.path.join(pathlib.Path.home(), 'Desktop')

    def __init__(self, root, controller, info, program: str, x=270, y=125):
        super().__init__()
        self.geometry(f'{x}x{y}')  # Here, self is tkinter.Toplevel
        # Set a fixed size
        self.minsize(width=x, height=y)
        self.maxsize(width=x, height=y)
        # Disable maximize / minimize button
        self.resizable(width=False, height=False)
        self.controller = controller
        self.root = root
        self.info = info
        # Currently, self.program can be: 'chrome', 'chromedriver', 'other'.
        self.program = program.lower()  # To assure it is not case-sensitive.
        self.x = x
        self.y = y
        self.installed_software = None
        self.path_to_home = pathlib.Path.home()
        self.path_to_desktop = os.path.join(self.path_to_home, 'Desktop')
        self.big_frame = ttk.Frame(self)
        self.big_frame.pack(expand=True, fill='both')
        self.initUI()
        self.setActive()
        self.grab_set()
        center(self, self.root)
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

    def initUI(self):
        """
        Constructs the window.
        """
        self.title("Warning")
        _topframe = ttk.Frame(self.big_frame)
        _topframe.pack(side='top', expand=True)
        valuelabel = ttk.Label(_topframe, text=f"{self.info}")
        valuelabel.pack(side='right', expand=True)
        if self.program == 'other':
            image = Image.open(os.path.join(parent_of_parent_folder, "images/warning/warning_sign1.png"))
        else:
            image = Image.open(os.path.join(parent_of_parent_folder, "images/warning/warning_sign.png"))
        image = image.resize(
            (int(self.winfo_width() * 60), int(self.winfo_height() * 60)), PIL.Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(_topframe, image=image)
        image_label.pack(side='left', expand=True, padx=10, pady=1)
        image_label.image = image
        buttons_frame = ttk.Frame(self.big_frame)
        buttons_frame.pack(side='bottom', expand=True)
        # Scrape with beautifulsoup for chromedriver.
        # Chrome needs Javascript for rendering the download button in the official site, thus it can not be automated.
        if self.program == 'chromedriver':
            cancel_button = ttk.Button(buttons_frame, text=f"Cancel", command=self.toplevel_quit)
            cancel_button.pack(side='bottom', expand=True, pady=10, padx=10, )
            open_button = ttk.Button(buttons_frame, text=f"Open {self.program.capitalize()} site",
                                     command=self.open_browser)
            open_button.pack(side='left', expand=True, pady=10, padx=10, )
            download_button = ttk.Button(buttons_frame, text=f"Download Chromedriver",
                                         command=self.check_chrome_version_and_download_chromedriver_and_add_it_to_path)
            download_button.pack(side='right', expand=True, pady=10, padx=10, )
        elif self.program == 'chrome':  # "Chrome"
            open_button = ttk.Button(buttons_frame, text=f"Download {self.program.capitalize()}",
                                     command=self.open_browser)
            open_button.pack(side='left', expand=True, pady=10, padx=10, )
            cancel_button = ttk.Button(buttons_frame, text=f"Cancel", command=self.toplevel_quit)
            cancel_button.pack(side='right', expand=True, pady=10, padx=10, )
        else:
            cancel_button = ttk.Button(buttons_frame, text=f"Cancel", command=self.toplevel_quit)
            cancel_button.pack(side='right', expand=True, pady=10, padx=10, )

    def open_browser(self):
        """Opens the url in the browser"""
        if self.program.lower() == 'chrome':
            webbrowser.open_new_tab(WarningDoesNotExists.url_chrome)
        elif self.program.lower() in "chromedriver.exe":
            webbrowser.open_new_tab(WarningDoesNotExists.url_chromedriver)
        self.toplevel_quit()

    def check_chrome_version_and_download_chromedriver_and_add_it_to_path(self):
        """
        Checks current version of Chrome, downloads a compatible chromedriver, unzips the file and
        adds the folder to windows' PATH.
        """
        the_version_of_chromedriver_to_download = self.check_chrome_version()
        self.download_compatible_chromedriver(version=the_version_of_chromedriver_to_download)
        self.locate_unzip_and_add_chromedriver_to_path()

    def check_chrome_version(self):
        """
        Chrome version
        See also: https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml
        """
        self.installed_software = InstalledSoftware(f'chrome')
        current_chrome_version = self.installed_software.installed_programs[0]['version']
        print(f"Current Chrome version: {current_chrome_version}")
        # Check if there is an identical version for Chromedriver
        try:
            response = requests.get(self.url_target_version(current_chrome_version), timeout=4)
            print(f"respone code {response.status_code}")
            if response.status_code in (400, 401, 402, 403, 404):
                # Check Google API
                google_api_respone = requests.get('https://chromedriver.storage.googleapis.com/', timeout=4)
                text = google_api_respone.text
                xml_file = os.path.join(pathlib.Path.home(), 'response.xml')
                current_chrome_version_first_numbers = current_chrome_version.split('.')[0]
                with open(xml_file, 'w+') as file:
                    file.write(text)
                ET.register_namespace('', 'http://doc.s3.amazonaws.com/2006-03-01')
                tree = ET.parse(xml_file, parser=ET.XMLParser(encoding='UTF-8'))
                _root = tree.getroot()
                for child in _root:
                    if child.tag == '{http://doc.s3.amazonaws.com/2006-03-01}Contents':
                        for child_child in child:
                            if child_child.tag == '{http://doc.s3.amazonaws.com/2006-03-01}Key' \
                                    and current_chrome_version_first_numbers in child_child.text:
                                # print(child_child.tag, child_child.text)
                                if '.' in child_child.text:  # To avoid other formats i.e 'LATEST_RELEASE_107'
                                    # Format: 107.0.5304.62
                                    chromedriver_version = child_child.text.split('.')[0]
                                    if chromedriver_version == current_chrome_version_first_numbers:
                                        print(f"Chromedriver version: {chromedriver_version} from {child_child.text}")
                                        # Example: Split '107.0.5304.18/chromedriver_win32.zip' and
                                        # return the first part
                                        return child_child.text.split('/')[0]
        except Exception as err:
            print(f"{err}")
            raise

    def download_compatible_chromedriver(self, version):
        """
        Downloads the given `version` of Chromedriver.
        :param version: The version of chromedriver to download
        """

        url_to_download_chromedriver = self.url_target_version(version)
        print(url_to_download_chromedriver)
        response = requests.get(url_to_download_chromedriver)
        chromedriver_path = os.path.join(pathlib.Path.home(), 'Desktop\\Chromedriver.zip')
        with open(chromedriver_path, 'wb+') as file:
            file.write(response.content)
            print(f"Chromedriver saved to {chromedriver_path}")

    def locate_unzip_and_add_chromedriver_to_path(self):
        """
        It creates a folder in Home if it does not exist, unzips there the chromedriver and
        then adds the folder to PATH.
        :return:
        """
        path_to_zip = os.path.join(pathlib.Path.home(), 'Desktop\\chromedriver.zip')
        path_to_unzip = os.path.join(pathlib.Path.home(), 'webdriver')
        try:
            os.mkdir(path_to_unzip)
            print(f"A folder created: {path_to_unzip}")
        except OSError:  # The folder exists.
            print(f"THe folder exists")
        # Unzip the file
        try:
            zip_file = ZipFile(path_to_zip)
            zip_file.extractall(path=path_to_unzip)
            zip_file.close()
        except Exception as err:
            print(err)
        finally:
            os.remove(path_to_zip)
        # Add to PATH
        self.add_folder_to_path(folder_path=path_to_zip)

    @staticmethod
    def is_admin():
        """
        Checks whether the current executable runs as an admin
        :return: Boolen
        """
        try:
            return str2bool(ctypes.windll.shell32.IsUserAnAdmin())
        except ctypes.WinError() as err:
            print(err)

    def add_folder_to_path(self, folder_path):
        """
        Add the `folder` to windows' PATH.
        :param folder_path: Path to the folder.
        :return: None
        """
        if WarningDoesNotExists.is_admin():
            os.system(f'''setx PATH "%PATH%;{folder_path}"''')
            print(f'Folder ("{folder_path}") added to PATH')
        else:
            # Warn the users that they need to grant admin rights to the process
            WarningDoesNotExists(controller=self.controller, root=self.root,
                                 info='You have to run the application with administrator '
                                      '\nrights to complete the process.',
                                 program='Other', x=375, y=140)
            self.toplevel_quit()

    def url_target_version(self, version):
        """Returns the url of `version`"""

        return f'https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip'

    def download_and_run_chrome_installer(self):
        """
        Downloads the latest Chrome, locates the installer (saved in the Desktop folder), runs the installer and
        destroys the widget.
        """
        if self.download_latest_chrome():
            self.locate_and_run_Chrome_installer()
            self.toplevel_quit()

    def download_latest_chrome(self):
        """
        Downloads the latest version of Chrome.
        :return True if Chrome installer is downloaded successfully. Else: False.
        """
        try:
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless')
            # See: https://stackoverflow.com/a/42943611
            prefs = {"profile.default_content_settings.popups": 0,
                     "download.default_directory": f"{self.path_to_desktop}\\\\",
                     "directory_upgrade": True, "download.prompt_for_download": False,
                     "default_content_setting_values.notifications": 0,
                     "content_settings.exceptions.automatic_downloads.*.setting": 1,
                     "safebrowsing.disable_download_protection": True, "default_content_settings.popups": 0,
                     "managed_default_content_settings.popups": 0, "profile.password_manager_enabled": False,
                     "profile.default_content_setting_values.notifications": 2,
                     "profile.managed_default_content_settings.popups": 0,
                     "profile.default_content_setting_values.automatic_downloads": 1,
                     'download.extensions_to_open': 'exe',
                     'safebrowsing.enabled': True  # If True, Chrome does not prompt the "Discard harmful file" pop-up
                     }
            options.add_experimental_option(name='prefs', value=prefs)
            driver = webdriver.Chrome(options=options)
            driver.get(WarningDoesNotExists.url_chrome)
            WebDriverWait(driver, timeout=30).until(EC.element_to_be_clickable(
                (By.XPATH,
                 "/html/body/div[3]/section[1]/div/div[4]/div/div[1]/div[2]/button")))
            button = driver.find_element(By.XPATH,
                                         "/html/body/div[3]/section[1]/div/div[4]/div/div[1]/div[2]/button")
            button.click()
            time.sleep(1)
            return True
        except Exception as err:
            print(err)
            return False

    def locate_and_run_Chrome_installer(self):
        """
        pass
        :return:
        """
        chrome_setup_exe = os.path.join(self.path_to_desktop, 'ChromeSetup.exe')
        if os.path.isfile(chrome_setup_exe):

            bat_file = os.path.join(self.path_to_desktop, 'start.bat')
            str_dump = f'''    
                            @echo off
                            \nstart "" "{chrome_setup_exe}" 
                            \nexit
                        '''
            with open(bat_file, 'w+') as file:
                file.write(str_dump)
                print(f"{__name__} > Bat file is written: {bat_file}")
            try:
                subprocess.Popen(bat_file)
                print(f"{__name__} > Bat is started")
                with open(os.path.join(pathlib.Path.home(), "test.txt"), 'a+') as file:
                    file.write(f"\n{__name__} > Bat is started from {bat_file}")
            except BaseException as err:
                print(f'{__name__} > {err}')
            finally:  # Remove the bat file
                time.sleep(2)
                os.remove(bat_file)

    def toplevel_quit(self, widget=None):
        """how to bind a messagebox to toplevel window in python
           https://stackoverflow.com/questions/17910866/python-3-tkinter-messagebox-with-a-toplevel-as-master"""
        if widget is not None:
            if widget is tk.Tk:
                print(f'WarningDoesNotExists>toplevel_quit: Root is now exiting')
                sys.exit()
            else:
                self.destroy()
                widget.destroy()
                print(f'WarningDoesNotExists>toplevel_quit: {widget} & {self} is now destroyed')
        else:
            self.destroy()
            print(f'WarningDoesNotExists>toplevel_quit: {self} is now destroyed')

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
    tkinter_theme_calling(root)
    warning = WarningDoesNotExists(controller=None, root=root, info='Chromedriver is not installed',
                                   program='chromedriver', x=370, y=170)
    version_of_chromedriver_to_download = warning.check_chrome_version()
    print(version_of_chromedriver_to_download)
    warning.download_compatible_chromedriver(version_of_chromedriver_to_download)
    # warning = WarningDoesNotExists(controller=None, root=root, info='Chromedriver is not installed',
    #                               program='chrome')
    # WarningDoesNotExists(controller=None, root=root, info='Chromedriver is not installed', program='Chromedriver')
    root.mainloop()
