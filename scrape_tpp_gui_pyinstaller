import os
import shutil
import PyInstaller.__main__
import sys
import pathlib
home_path = pathlib.Path.home()
dir_path = os.path.dirname(os.path.realpath(__file__))
name = sys.argv[0].split("/")[-1].replace("_pyinstaller", "")
images_dir_path = os.path.join(dir_path, 'images')
source_dir_path = os.path.join(dir_path, 'source')

PyInstaller.__main__.run([
    f'{name}',
    '--onedir',
    '--nowindowed',
    '--noconsole',
    f'--add-data={images_dir_path};images',
    f'--add-data=C:\\Users\\lapto\\PycharmProjects\\pythonProject\\source;source',
    '-y'
])
