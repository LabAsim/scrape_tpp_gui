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
    error_data = ""
    # Alternative, just print and write traceback.format_exc()
    for line in formatted_lines:
        if to_print_error:
            print(line)
        if file_exists(dir_path, 'errors.txt'):
            with open(error_filepath, 'r+', encoding='utf-8') as file:
                file_contents = file.read()
                error_data =  file_contents + line + "\n"
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                file.write(error_data)
        else:
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                file.write(f"{line}\n")  # Add \n in the end to format nicely


if __name__ == "__main__":
    # Example for trace_error()
    try:
        a = 2
        a + "b"
    except Exception:
        trace_error()
