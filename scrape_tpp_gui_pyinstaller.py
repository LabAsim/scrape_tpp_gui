import os
import PyInstaller.__main__
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
#name = sys.argv[0].split("/")[-1].replace("pyinstaller_", "")
name = 'main.py'
images_dir_path = os.path.join(dir_path, 'images')
source_dir_path = os.path.join(dir_path, 'source')

PyInstaller.__main__.run([
    f'{name}',
    '--onefile',
    '--console',
    '--nowindowed',
    '--noconsole',
    f'--add-data={source_dir_path};source',
    '-y'
])

os.remove(os.path.join(dir_path + '\\dist', 'scrape_tpp_gui.exe'))
os.rename(os.path.join(dir_path + '\\dist', 'main.exe'), os.path.join(dir_path + '\\dist', 'scrape_tpp_gui.exe'))