"""
Tests for some helper functions
"""
import time
import unittest
import os
import sys
import psutil
import undetected_chromedriver as uc

# Load modules from upper folders
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(parent_parent)
from helper_functions import file_exists, center, tkinter_theme_calling, callback, headers, sortby, date_to_unix, \
    is_driver_open


class TestHelperFunctions(unittest.TestCase):
    # The chromedriver
    driver: uc.Chrome | None = None

    def test_driver_is_None(self):
        # First the driver is None. It should return False
        self.assertFalse(is_driver_open(TestHelperFunctions.driver))

    def test_is_driver_open_true(self):
        # It should return True, because the Chrome is open.
        options = uc.ChromeOptions()
        TestHelperFunctions.driver = uc.Chrome(use_subprocess=True, options=options)
        TestHelperFunctions.driver.implicitly_wait(3)
        self.assertTrue(is_driver_open(TestHelperFunctions.driver))
        TestHelperFunctions.driver.close()
        TestHelperFunctions.driver.quit()

    def test_is_driver_open_false(self):
        # It should return False, because the Chrome is closed in this test.
        options = uc.ChromeOptions()
        TestHelperFunctions.driver = uc.Chrome(use_subprocess=True, options=options)
        TestHelperFunctions.driver.implicitly_wait(3)
        TestHelperFunctions.driver.close()
        TestHelperFunctions.driver.quit()
        self.assertFalse(is_driver_open(TestHelperFunctions.driver))

    def test_is_driver_open_false_user_interaction(self):
        # It should return False, because the Chrome is closed abruptly (from user or the OS).
        options = uc.ChromeOptions()
        TestHelperFunctions.driver = uc.Chrome(use_subprocess=True, options=options)
        current_pid = os.getpid()
        current_process = psutil.Process(current_pid)
        children_of_current = current_process.children(recursive=True)
        children_of_current.append(current_process)
        current_own_process = {child.name(): child.pid for child in children_of_current}
        print(f'processes: {current_own_process}')
        # Kill every chrome / chromedriver child instances of current python.exe to emulate the user closing the chrome.
        for child in children_of_current:
            print(f'Name: {child.name()}: {child.pid}')
            if "chrome" in child.name():
                psutil.Process(child.pid).kill()
        # Without time sleep, it fails.
        # In the App, there will be a time gap between closed Chrome and is_driver_open() call.
        time.sleep(0.1)
        self.assertFalse(is_driver_open(TestHelperFunctions.driver))


if __name__ == '__main__':
    unittest.main()
