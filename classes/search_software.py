"""
A module containing a Class to search both registry and windows PATH.
"""
import os
import pathlib
import re
import shutil
from future.moves import winreg


class InstalledSoftware:
    """
    Contains all info for the program.
    """

    def __init__(self, name_or_pattern):
        self.name_or_pattern = name_or_pattern
        self.list_containing_all_programs = self.get_all_software()
        self.installed_programs = []
        self.search_executable_in_installed_programmes(name_or_pattern)
        self.program_in_windows_path = {'name': None,
                                        'path': None}

    def get_software_from(self, hive, flag):
        """
        https://stackoverflow.com/questions/16452540/registry-path-to-find-all-the-installed-applications

        :param hive:
        :param flag:
        :return: A list of dictionaries
        i.e.   [{'name': 'Visual Studio Community 2017', 'version': '15.9.46', 'publisher': 'Microsoft Corporation'},
                {'name': 'MSI Afterburner 4.6.4 Beta 3', 'version': '4.6.4 Beta 3', 'publisher': 'MSI Co., LTD'}]

        See also:
        https://stackoverflow.com/a/54825112 or https://github.com/netinvent/windows_tools

        Microsoft-docs for keys' names of the registry:
        https://learn.microsoft.com/en-us/previous-versions/tn-archive/ee156540(v=technet.10)?redirectedfrom=MSDN
        https://learn.microsoft.com/en-us/previous-versions/windows/desktop/legacy/aa394378(v=vs.85)?redirectedfrom=MSDN

        """
        a_reg = winreg.ConnectRegistry(None, hive)
        with winreg.OpenKey(a_reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                            0, winreg.KEY_READ | flag) as aKey:

            count_subkey = winreg.QueryInfoKey(aKey)[0]

            software_list = []

            for i in range(count_subkey):
                software = {}
                try:
                    asubkey_name = winreg.EnumKey(aKey, i)
                    with winreg.OpenKey(aKey, asubkey_name) as asubkey:
                        software['name'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]

                        try:
                            software['version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
                        except EnvironmentError:
                            software['version'] = 'undefined'
                        try:
                            software['path'] = winreg.QueryValueEx(asubkey, 'InstallLocation')[0]
                        except EnvironmentError:
                            software['path'] = 'undefinded'
                        try:
                            software['publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]
                        except EnvironmentError:
                            software['publisher'] = 'undefined'
                        try:
                            software['display_name'] = winreg.QueryValueEx(asubkey, 'DisplayName')[0]
                        except EnvironmentError:
                            software['display_name'] = 'undefinded'

                        software_list.append(software)

                except EnvironmentError:
                    continue

        return software_list

    def get_all_software(self):
        """
        Sums all installed software and returns a list of dictionaries containing all installed software
        retrieved from the registry of the Local machine and the current user.

        Example:
        [{'name': 'Visual Studio Community 2017', 'version': '15.9.46', 'publisher': 'Microsoft Corporation'},
        {'name': 'MSI Afterburner 4.6.4 Beta 3', 'version': '4.6.4 Beta 3', 'publisher': 'MSI Co., LTD'}]

        :return: A list of dictionaries: list[{str: str}]

        See also:

        Python-docs:
        https://docs.python.org/3.10/library/winreg.html#winreg.HKEY_CURRENT_USER
        https://docs.python.org/3.10/library/winreg.html#winreg.KEY_WOW64_32KEY

        """
        software_list_to_return = self.get_software_from(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)
        software_list_to_return += self.get_software_from(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY)
        software_list_to_return += self.get_software_from(winreg.HKEY_CURRENT_USER, 0)
        return software_list_to_return

    def search_executable_in_installed_programmes(self, name_or_pattern: str | re.Pattern):
        """
        Searches for the `name_or_pattern` in `self.list_containing_all_programs`
        and appends its dictionary to `self.installed_programs`

        :param name_or_pattern: Str or a Regex pattern
        :return: None

        """
        if isinstance(name_or_pattern, re.Pattern):
            for program in self.list_containing_all_programs:
                if re.search(name_or_pattern, program['name']):
                    self.installed_programs.append(program)
        else:
            for program in self.list_containing_all_programs:
                if name_or_pattern.lower() in program['name'].lower():
                    self.installed_programs.append(program)

    def search_windows_path(self, name_or_pattern: str | re.Pattern):
        """

        Searches the folder (not sub-folders) for the given `name_or_pattern` and returns True if found, else False.
        Alternative, use shutil.which().

        :param name_or_pattern: str or a Regex pattern
        :return: Boolean
        """

        path_list = []

        for _key, _value in os.environ.items():
            if _key == 'PATH':
                path_list = _value.split(';')

        for path_from_path_list in path_list:
            path_to_search = pathlib.Path(path_from_path_list)
            if os.path.exists(path_to_search):
                for filename in os.listdir(path_to_search):
                    filename_path = os.path.join(path_to_search, filename)
                    if os.path.isfile(filename_path):
                        if isinstance(name_or_pattern, re.Pattern):
                            if re.search(name_or_pattern, filename):
                                self.program_in_windows_path = {'name': filename,
                                                                'path': filename_path}
                                return True
                        else:
                            if name_or_pattern.lower() in filename:
                                self.program_in_windows_path = {'name': filename,
                                                                'path': filename_path}
                                return True
        return False

    @staticmethod
    def program_path(name: str):
        """
        Check whether `name` is on PATH and marked as executable.
        The name can be written with or without the suffix `.exe`.

        :parameter name: str
        :returns: The path of the `name`

        """

        path_of_exe = shutil.which(name)
        if path_of_exe is not None:
            path_of_exe = re.sub(f'{name}\.[Ee][Xx][Ee]', "", path_of_exe)
        return path_of_exe

    @staticmethod
    def program_exists(name: str):
        """
        Check whether `name` is in PATH and marked as executable.
        The name can be written with or without the suffix `.exe`.

        :parameter name: str
        :returns: Boolean

        """

        return shutil.which(name) is not None


if __name__ == "__main__":
    # Check whether a software is in the installed applications
    program_to_find = InstalledSoftware('chrome')
    print(f'Installed programs: {program_to_find.installed_programs}')

    # Search in the PATH
    flexible_name = 'chrome'
    print()
    print(program_to_find.search_windows_path(flexible_name))  # More flexible, but rather slower.
    print(program_to_find.program_in_windows_path)
    # Use of shutil.which()
    print()
    print(program_to_find.program_exists('chromedriver'))
    print(program_to_find.program_path('chromedriver'))
