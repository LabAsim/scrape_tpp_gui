import json
import os.path
import traceback
from helper_functions import file_exists, cprint, get_current_time, strip_ansi_characters
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
            cprint(line)
        if file_exists(dir_path, 'errors.txt'):
            with open(error_filepath, 'r+', encoding='utf-8') as file:
                file_contents = file.read()
                error_data = f'{file_contents}{strip_ansi_characters(get_current_time())} {line}\n'
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                file.write(strip_ansi_characters(error_data))
        else:
            with open(error_filepath, 'w+', encoding='utf-8') as file:
                file.write(f"{strip_ansi_characters(get_current_time())}{line}\n")  # Add \n in the end to format nicely
    print(f"Errors saved in {error_filepath}")


if __name__ == "__main__":
    # Example for trace_error()
    try:
        a = 2
        a + "b"
    except Exception:
        trace_error()
