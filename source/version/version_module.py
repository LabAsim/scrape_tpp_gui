import json
import os
import pathlib
import re
import tempfile
from datetime import datetime
import requests


def file_exists(dir_path, name) -> bool:
    """Returns true if the path exists"""
    path_to_name = pathlib.Path(os.path.join(dir_path, name))
    if path_to_name.exists():
        return True
    else:
        return False

def check_new_version():
    """
    Checks the version of version.json at the remote repo and compares it with the current version of the application.
    Note that the version.json is located in a temporary file when the script runs as a .py file or as one-file exe.
    :return: True if a newer version exists at the remote repo.
    """
    version_url = "https://raw.githubusercontent.com/LabAsim/scrape_tpp_gui/main/source/version/version.json"
    base_github_release_url = "https://github.com/LabAsim/scrape_tpp_gui/releases/tag/"
    new_online_version = None
    dir_path = os.path.dirname(os.path.realpath(__file__))  # A temporary dir both in .py file and one-file exe.
    print(f"check_version(): {dir_path}")
    # Load current version
    current_version = ''
    with open(os.path.join(dir_path, "version.json")) as current_version_file:
        json_data = json.load(current_version_file)
        current_version = json_data['version'].strip()
    # Convert the string to a datetime obj
    current_version = current_version.split("-")
    year = int(current_version[-1])
    month = int(current_version[1])
    day = int(current_version[0])
    current_version = datetime(year, month, day)
    print(f'Current version: {current_version}')
    # https://docs.python.org/3/library/tempfile.html#examples
    online_version = ""
    with tempfile.TemporaryDirectory() as tempdir:
        version_file = os.path.join(tempdir, 'version.json')
        response = requests.get(version_url)
        response_code = str(response.status_code)
        # Check that the response code is not in 20x
        if re.search(response_code, "20[0-3]"): # https://stackoverflow.com/a/16575064
            if response_code == "204":
                print("The target url for the new version is empty")
                return "The target url for the new version is empty"
            else:
                print(f"Wrong url provided for the new version")
                return "Wrong url provided for the new version"
        # Write response's content to a file
        with open(version_file, 'wb+') as pyfile:
            pyfile.write(response.content)
        print(file_exists(tempdir, "version.json"), version_file)
        with open(version_file, "r", encoding='utf-8') as jsonfile:
            json_data = json.load(jsonfile)
            # json_data = json.loads(jsonfile.read())  # Alternative https://stackoverflow.com/a/58647394
            online_version = json_data['version'].strip()
        new_online_version = f"{online_version}"
        # Convert the string to a datetime obj
        online_version = online_version.split("-")
        year = int(online_version[-1])
        month = int(online_version[1])
        day = int(online_version[0])
        online_version = datetime(year, month, day)
    print(f"Online version: {online_version}")
    if online_version > current_version:
        print("A new version is online.\n"
              f"See {base_github_release_url + new_online_version}")
        return True
    else:
        print("The application is up to date!")
        return False


if __name__ == "__main__":
    # Example
    print(f'Is current version not up to date? {check_new_version()}')