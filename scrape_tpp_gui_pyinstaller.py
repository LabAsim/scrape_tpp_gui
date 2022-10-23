import os
import PyInstaller.__main__
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
name = sys.argv[0].split("/")[-1].replace("_pyinstaller", "")
images_dir_path = os.path.join(dir_path, 'images')
source_dir_path = os.path.join(dir_path, 'source')

PyInstaller.__main__.run([
    f'{name}',
    '--onedir',
    '--console',
    # '--nowindowed',
    # '--noconsole',
    f'--add-data={images_dir_path};images',
    f'--add-data={source_dir_path};source',
    '-y'
])
