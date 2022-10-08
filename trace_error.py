import json
import os.path
import traceback
from helper_functions import file_exists
from misc import dir_path


def trace_error(to_print_error=True):
    """
    The function traces the exceptions by printing and logging the error.

    :param to_print_error: Boolean - If true, prints and logs. Else, its logs the errors in a separate txt file
    :return: None

    See also:
    # https://docs.python.org/3/library/traceback.html#traceback-examples
    """
    # exc_type, exc_value, exc_traceback = sys.exc_info()  # All the info from the exception
    formatted_lines = traceback.format_exc().splitlines()
    error_filepath = os.path.join(dir_path, 'errors.txt')
    json_data = ''
    for line in formatted_lines:
        if to_print_error:
            print(line)
        if file_exists(dir_path, 'errors.txt'):
            with open(error_filepath, 'r+', encoding='utf-8') as file:
                json_data = json.load(file)
                if len(json_data) == 0:  # To avoid empty string in the text file
                    json_data = line
                else:
                    json_data.update(line)
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
        else:
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                json_data.update(line)
                json.dump(json_data, file, indent=4)
