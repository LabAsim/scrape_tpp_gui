"""
The pyinstaller script for the updater
"""

import os
import shutil
import PyInstaller.__main__
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
name = sys.argv[0].split("/")[-1].replace("pyinstaller_", "")


parent_folder = os.path.dirname(dir_path)
parent_of_parent_folder = os.path.dirname(parent_folder)
version_module_path = os.path.join(parent_folder, 'version\\version_module.py')

PyInstaller.__main__.run([
    f'{name}',
    '--onefile',
    '--console',
    #'--nowindowed',
    #'--noconsole',
    f'--add-data={version_module_path};.',  # move the module to the same level as the updater.py
    '-y'
])

try:
    shutil.move(os.path.join(dir_path + '\\dist', 'updater.exe'), os.path.join(dir_path))
except shutil.Error as err:
    os.remove(os.path.join(dir_path, 'updater.exe'))
    shutil.move(os.path.join(dir_path + '\\dist', 'updater.exe'), os.path.join(dir_path))
