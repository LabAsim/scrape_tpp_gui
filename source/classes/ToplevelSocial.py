import os
import sys
import tkinter as tk
from tkinter import ttk
import tktooltip
from PIL import Image, ImageTk

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(parent_parent)
# Now, python can detect the helper_functions.py from the parent directory
from helper_functions import file_exists, center, callback


class ToplevelSocial:
    """Contains the links to TPP's social media"""
    x = 1000
    y = 500
    image_x_size = int(600 * 0.7)
    image_y_size = int(150 * 0.7)
    social_media_urls = ['https://www.facebook.com/ThePressProject',
                         'https://www.facebook.com/anaskopisi',
                         'https://twitter.com/intent/follow?screen_name=ThePressProject&tw_p=followbutton',
                         'https://libretooth.gr/@thepressproject']

    def __init__(self, controller, root):
        # https://stackoverflow.com/questions/69293836/tkinter-how-do-i-resize-an-image-to-fill-its-labelframe-and-have-that-labelfram
        self.controller = controller
        self.dir_path = self.find_the_path_of_main()
        self.toplevelsocial = tk.Toplevel()
        self.toplevelsocial.protocol("WM_DELETE_WINDOW", self.toplevel_quit)
        self.toplevelsocial.title('ThePressProject social media')
        # Set a fixed size
        self.toplevelsocial.maxsize(width=ToplevelSocial.x, height=ToplevelSocial.y)
        # Disable maximize / minimize button
        self.toplevelsocial.resizable(width=False, height=False)
        self.bigframe = ttk.Frame(self.toplevelsocial)
        self.bigframe.pack(expand=True, fill='both')
        self.topframe = ttk.Frame(self.bigframe)
        self.topframe.pack(expand=True, fill='both', side='top', padx=80, pady=10)
        self.middleframe = ttk.Frame(self.bigframe)
        self.middleframe.pack(expand=True, fill='both', side='top', padx=80, pady=10)
        self.bottomframe = ttk.Frame(self.bigframe)
        self.bottomframe.pack(expand=True, fill='both', side='bottom', padx=80, pady=10)
        # First image
        path_to_img_facebook = os.path.join(self.dir_path,
                                            'source\\multimedia\\images\\socialmedia\\facebook\\facebook.png')
        self.img_facebook = Image.open(path_to_img_facebook)
        self.img_facebook = self.img_facebook.resize((ToplevelSocial.image_x_size, ToplevelSocial.image_y_size),
                                                     Image.ANTIALIAS)
        # (int(self.toplevelsocial.winfo_width() * 200), int(self.toplevelsocial.winfo_height() * 200)),

        self.img_facebook_tk = ImageTk.PhotoImage(self.img_facebook)
        self.label_facebook = ttk.Label(self.topframe, image=self.img_facebook_tk, cursor='hand2')
        self.label_facebook.image = self.img_facebook_tk
        self.label_facebook.pack(expand=True, fill='both')
        self.label_facebook.bind('<Button-1>', lambda e: callback(ToplevelSocial.social_media_urls[0]))
        tktooltip.ToolTip(self.label_facebook, msg='Click to open the Facebook profile', delay=0.5)
        # 2nd image
        self.img_twitter = Image.open(os.path.join(self.dir_path,
                                                   'source\\multimedia\\images\\socialmedia\\twitter\\twitter.png'))
        self.img_twitter = self.img_twitter.resize((ToplevelSocial.image_x_size, ToplevelSocial.image_y_size),
                                                   Image.ANTIALIAS)
        # (int(self.toplevelsocial.winfo_width()/3), int(self.toplevelsocial.winfo_height()/3)),
        # Image.ANTIALIAS)
        self.img_twitter_tk = ImageTk.PhotoImage(self.img_twitter)
        self.label_twitter = ttk.Label(self.middleframe, image=self.img_twitter_tk, cursor='hand2')
        self.label_twitter.image = self.img_twitter_tk
        self.label_twitter.pack(expand=True, fill='both')
        self.label_twitter.bind('<Button-1>', lambda e: callback(ToplevelSocial.social_media_urls[2]))
        tktooltip.ToolTip(self.label_twitter, msg='Click to open the Twitter profile', delay=0.5)
        # 3rd image
        self.img_mastodon = Image.open(os.path.join(self.dir_path,
                                                    'source\\multimedia\\images\\socialmedia\\mastodon\\mastodon.png'))
        self.img_mastodon = self.img_mastodon.resize((ToplevelSocial.image_x_size, ToplevelSocial.image_y_size),
                                                     Image.ANTIALIAS)
        self.img_mastodon_tk = ImageTk.PhotoImage(self.img_mastodon)
        self.label_mastodon = ttk.Label(self.bottomframe, image=self.img_mastodon_tk, cursor='hand2')
        self.label_mastodon.image = self.img_mastodon_tk
        self.label_mastodon.pack(expand=True, fill='both')
        self.label_mastodon.bind('<Button-1>', lambda e: callback(ToplevelSocial.social_media_urls[3]))
        tktooltip.ToolTip(self.label_mastodon, msg='Click to open the Mastodon profile', delay=0.5)
        center(window=self.toplevelsocial, parent_window=root)
        # self.toplevelsocial.bind('<Configure>', func=self.resize_images)
        print((int(self.bigframe.winfo_width()), int(self.bigframe.winfo_height())))
        print((int(self.toplevelsocial.winfo_width()), int(self.toplevelsocial.winfo_height())))

    def resize_images(self, event):
        # self.img_facebook = Image.open(os.path.join(self.dir_path, 'Facebook_wikimedia.png'))
        img_facebook = self.img_facebook.resize(
            (int(self.toplevelsocial.winfo_width() / 3), int(self.toplevelsocial.winfo_height() / 3)))
        self.img_facebook_tk = ImageTk.PhotoImage(img_facebook)
        self.label_facebook.config(image=self.img_facebook_tk)
        # self.img_twitter = Image.open(os.path.join(self.dir_path, 'twitter_tpp.png'))
        img_twitter = self.img_twitter.resize(
            (int(self.bigframe.winfo_width() / 3), int(self.bigframe.winfo_height() / 3)),
            Image.ANTIALIAS)
        self.img_twitter_tk = ImageTk.PhotoImage(img_twitter)
        self.label_twitter.config(image=self.img_twitter_tk)
        self.label_twitter.image = img_twitter

    def find_the_path_of_main(self) -> str:
        """
        Returns The path of the directory of main.py or the .exe
        :return: The path of the directory of main.py or the .exe

        Note that if the current class is import in App.py as
        'from scrape_tpp_gui.source.classes.ToplevelSocial import ToplevelSocial',
        the path will contain scrape_tpp_gui\\, which does not exist in temporary directories.
        Thus, in this situation, you need the parent folder.
        It's easier to use 'source.classes.ToplevelSocial import ToplevelSocial' to avoid that

        """
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            '''
            The temporary path of the files (MEIPP).
            Note that if the current class is import in App.py as 
            'from scrape_tpp_gui.source.classes.ToplevelSocial import ToplevelSocial', 
            the path will contain \\scrape_tpp_gui\\, which does not exist in temporary directories. 
            Thus, in this situation, you need the parent folder.
            It's easier to use 'source.classes.ToplevelSocial import ToplevelSocial' to avoid that
            '''
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            # If the path until this step contains \\scrape_tpp_gui, get the parent dir, which is a temp dir(MEIPP).
            # self.dir_path = os.path.dirname(self.dir_path)
            print("ToplevelSocial>find_the_path_of_main():Exe:", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(__file__)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)
            print(f'ToplevelSocial>find_the_path_of_main():Script: {self.dir_path}')
            return self.dir_path

    def bring_focus_back(self):
        """
        Maximizes the toplevel window and forces the focus on it.
        """
        self.toplevelsocial.deiconify()
        self.bigframe.lift()
        self.bigframe.focus_force()

    def toplevel_quit(self):
        """It closes the window and set the controller variable back to None"""
        # Set the variable of this toplevel in the controller class back to None
        if self.controller:
            self.controller.toplevelsocial = None
        # Destroy the toplevel
        self.toplevelsocial.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    center(root)
    ToplevelSocial(controller=None, root=root)
    root.mainloop()
