import time
import unittest
import dataclasses
import os
import re
import sqlite3
import sys
import threading
import tkinter.font as font
import tkinter as tk
from tkinter import ttk
import inspect

from scrape_tpp_gui.source.classes.database.helper import match_vowels

# Load modules from upper folders
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent_parent = os.path.dirname(parent)
sys.path.append(parent_parent)
from helper_functions import file_exists, center, tkinter_theme_calling, callback, headers, sortby, date_to_unix, \
    is_driver_open
from trace_error import trace_error
from source.classes.generictoplevel import GenericToplevel
from source.classes.NewsDataclass import NewsDataclass
from source.classes.database.helper import ToplevelArticleDatabase, wrapper_for_case_conversion, \
    convert_to_case_not_sensitive
from source.classes.database.SubPageReaderDB import SubPageReader
from source.classes.database.db import DatabaseWindow
from source.classes.database.helper import convert_to_case_not_sensitive, converted_stressed_vowels_to_non_stressed


class TestDB(unittest.TestCase):
    root = tk.Tk()
    window: DatabaseWindow = DatabaseWindow(root=root, controller=None)

    async def _start_tkinter(self):
        print("starting")
        TestDB.root.mainloop()

    def test_fetch_from_db(self):
        TestDB.window.fetched_news = TestDB.window.fetch_from_db(
            query="SELECT date, title, summary, category, id, url, main_content, author, author_url, date_unix FROM "
                  "news ORDER BY date_unix DESC")
        test_news = TestDB.window.fetched_news
        self.assertIsInstance(test_news, list)
        self.assertIsInstance(test_news[0], tuple)

    def test_boolean(self):
        time.sleep(0.1)
        self.assertTrue(TestDB.window.case_sensitive_boolean.get())

    def test_match_vowels(self):
        # Test Greek with stressed vowels plus Latin letters
        first_sentence = TestDB.window.match_vowels(' Not in για το Χρυσής Αυγή εισαγγελέας')
        self.assertEqual(' Not in για το Χρυσής Αυγή εισαγγελέας', first_sentence)
        # Test numbers
        numbers = TestDB.window.match_vowels('test 123123')
        self.assertEqual('test 123123', numbers)
        # It strips ".", ":", ",", "'"
        stripped_sentence = TestDB.window.match_vowels("test;;'.,")
        self.assertEqual('test', stripped_sentence)

    def test_convert_to_case_not_sensitive(self):
        sentence = convert_to_case_not_sensitive('Ανάλυση Intern 123')
        self.assertEqual('ανάλυση intern 123', sentence)

    def test_total_conversion(self):
        """
        1st: Lower all letters

        2nd: Match the greek vowels

        3rd: Convert the stressed vowel to non-stressed and the rest Greek letters (i.e. "ς" -> "σ")

        Note that all punctuation symbols are stripped.
        :return: None
        """
        # Α greek sentence
        sentence = "ΧΡΈΟΣ Το ΠάςΟκ να ΜΗΝ χρεώκοπήσει"
        sentence = converted_stressed_vowels_to_non_stressed(match_vowels(convert_to_case_not_sensitive(sentence)))
        self.assertEqual("χρεοσ το πασοκ να μην χρεωκοπησει", sentence)
        # English plus greek letters
        sentence = "IndEPEndent: ΤΟ παΣΌΚ ήΤΑΝ εδώ"
        sentence = converted_stressed_vowels_to_non_stressed(match_vowels(convert_to_case_not_sensitive(sentence)))
        self.assertEqual("independent το πασοκ ηταν εδω", sentence)
        # The char `:` will be stripped.
        sentence = "Τσίπρας:"
        sentence = converted_stressed_vowels_to_non_stressed(
            match_vowels(convert_to_case_not_sensitive(sentence)))
        self.assertEqual("τσιπρασ", sentence)
        # https://stackoverflow.com/questions/71098498/why-im-getting-unicodeencodeerror-charmap-codec-cant-encode-characters-in-p
        self.assertEqual(converted_stressed_vowels_to_non_stressed(
            match_vowels(convert_to_case_not_sensitive("Tσίπρας"))), "tσιπρασ")


if __name__ == '__main__':
    unittest.main(verbosity=2)
