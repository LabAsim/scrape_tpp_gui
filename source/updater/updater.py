"""
The updater module.
It has to be turned into an exe to run.
"""

import time
import sys
print("Loading updater")

if getattr(sys, 'frozen', False):
    # If the script is frozen, the modules are placed from the other folders in the same folder
    # containing the updater.py
    try:
        import argparse
        import os
        import pathlib
        import subprocess
        import psutil
        import requests
        from version_module import check_online_version
    except (ImportError, BaseException) as err:
        print(err)
        time.sleep(3)
else:
    try:
        import argparse
        import os
        import pathlib
        import subprocess
        import psutil
        import requests

        parent_folder = os.path.dirname(os.path.dirname(__file__))
        parent_of_parent_folder = os.path.dirname(parent_folder)
        print(parent_of_parent_folder)
        sys.path.append(parent_of_parent_folder)
        from trace_error import trace_error
        from source.version.version_module import check_online_version
    except ImportError as err:
        print(err)
        time.sleep(2)


def start_updating_process(path, pid_of_main):
    """
    A function which downloads the update
    :param pid_of_main: The pid of the main app.
    :param path: The path to download the update to.
    :return:
    """
    pid_of_main = int(pid_of_main)
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    children_of_current = current_process.children(recursive=True)
    children_of_current.append(current_process)
    current_own_process = {child.name(): child.pid for child in children_of_current}
    print(f'mp.processes: {current_own_process}')
    for child in children_of_current:
        print(f'Name: {child.name()}: {child.pid}')
        with open(os.path.join(pathlib.Path.home(), "test.txt"), 'w+') as file:
            file.write(f'\nName: {child.name()}: {child.pid}')
    kill_process_and_children(pid_to_kill=pid_of_main, current_own_process=current_own_process)
    # time.sleep(0.5)
    with open(os.path.join(pathlib.Path.home(), "test.txt"), 'a+') as file:
        file.write("\nDownloading...")
    print("Downloading...")
    download_update(path)
    # path_to_the_exe = os.path.join(path, 'scrape_tpp_gui.exe')
    # cmd_arguments = [os.path.join(path, 'scrape_tpp_gui.exe'), 'start ', '/wait ']
    # os.system(f'''@echo off\nstart "" "{path_to_the_exe}" \nexit''')
    print("Starting...")
    with open(os.path.join(pathlib.Path.home(), "test.txt"), 'a+') as file:
        file.write("\nStarting...")
    create_and_start_bat(path_to_dir=path)
    # Kill the current process
    with open(os.path.join(pathlib.Path.home(), "test.txt"), 'a+') as file:
        file.write("\nKilling updater...")
    psutil.Process(current_pid).kill()
    # kill_process_and_children(current_pid, {"name": 900000})  # arbitrary dict


def kill_process_and_children(pid_to_kill: int, current_own_process: dict):
    """
    Iterate over the children and parent except current mp.Process.
    :param current_own_process:
    :param pid_to_kill:
    :return:
    """
    process_list = []
    own_parent_child_process = {}
    parent = psutil.Process(pid_to_kill)
    own_parent_child_process[parent.name()] = pid_to_kill
    children = parent.children(recursive=True)
    children.append(parent)  # Include the parent process in the children
    for child in children:
        if child.name not in current_own_process:
            try:
                child_name = child.name()
                child_pid = child.pid
                if child_pid != (os.getpid()):
                    if child_pid not in list(current_own_process.values()):
                        # child.send_signal(signal.SIGTERM)
                        child.kill()
                        print(f'kill_process_and_children>{child_name}:{child_pid} is killed '
                              f'from program {psutil.Process(os.getpid())}')
            except psutil.NoSuchProcess:
                pass
            except BaseException:
                pass
    gone, alive = psutil.wait_procs(children, timeout=None,
                                    callback=None)
    with open(os.path.join(pathlib.Path.home(), "test.txt"), 'w+') as file:
        file.write(str(gone))
    print(f"kill_process_and_children>Gone: {gone}"
          f"\n\tStill alive{alive}")
    if len(alive) != 0:
        for alive_process in alive:
            try:
                alive_process.kill()
            except (psutil.NoSuchProcess, BaseException):
                pass
    gone, alive = psutil.wait_procs(children)
    print(f"kill_process_and_children>Gone: {gone}"
          f"\nStill alive{alive}")


def download_update(path):
    """
    Downloads the updated exe to the given path.
    :return: None
    """
    base_github_release_url = "https://github.com/LabAsim/scrape_tpp_gui/releases/download/"
    new_version = check_online_version()
    if new_version is not None:
        github_url = base_github_release_url + new_version + "/scrape_tpp_gui.exe"
        response = requests.get(github_url)
        path_to_new_file = os.path.join(path, f"scrape_tpp_gui.exe")
        with open(path_to_new_file, 'wb+') as file:
            file.write(response.content)
        print(f"The new version saved to {path_to_new_file}")
        with open(os.path.join(pathlib.Path.home(), "test.txt"), 'a+') as file:
            file.write(f"\nThe new version saved to {path_to_new_file}")


def create_and_start_bat(path_to_dir):
    """

    :param path_to_dir: The path of the bat file
    """
    bat_file = os.path.join(path_to_dir, 'start.bat')
    path_to_the_exe = os.path.join(path_to_dir, 'scrape_tpp_gui.exe')
    str_dump = f'''
                    \nstart "" "{path_to_the_exe}" 
                    \nexit
                '''
    with open(bat_file, 'w+') as file:
        file.write(str_dump)
        print(f"file is written: {bat_file}")
    try:
        subprocess.Popen(bat_file)
        print(f"Bat is started")
        with open(os.path.join(pathlib.Path.home(), "test.txt"), 'a+') as file:
            file.write(f"\nBat is started")
    except BaseException as err:
        print(err)
    finally:  # Remove the bat file
        os.remove(bat_file)


def parse_arguments():
    """
    Parser for commandline arguments.
    :return: my_parser.parse_args()
    """
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--path', type=str, action='store', const=True, nargs='?', required=False,
                           default=os.path.dirname(os.path.realpath(__file__)),
                           help='The path to the scrape_tpp_gui.exe')
    my_parser.add_argument('--parentpid', type=str, action='store', const=True, nargs='?', required=False,
                           default=None,
                           help='The parent pid')
    return my_parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    # The path passed
    path = args.path
    parent_pid = args.parentpid
    print(f'Path argument: {path}')
    time.sleep(1)
    # Check for a new version at the remote repository
    # path = os.path.dirname(os.path.realpath(__file__))
    try:
        start_updating_process(path=path, pid_of_main=parent_pid)
        # kill_process_and_children(parent_pid)
        # download_update(path)
        # create_and_start_bat(path)
        time.sleep(10)
    except BaseException as err:
        print(err)

        time.sleep(10)
