# ThePressProject Scraper GUI

## Description

This is my first project in order to learn Python.
I have built it to access the news faster and in a more aggregated way than just reading the site.
It scrapes the news categories of [thepressproject.gr](https://thepressproject.gr/) site.

Any contributions or ideas are welcome!

It has been tested in Python 3.10 and Windows 10. 

**Important Note**: Unfortunately, the updater.exe inside the one-file executable scraper\_tpp\_gui.exe is flagged
as a threat by Avira antivirus, although it does not contain, of course, any malware.

## Table of Contents

*   [Dependencies](#dependencies)

*   [Usage](#usage)

*   [Convert to executable](#convert-to-executable)

*   [TODO](#TODO)

*   [Credits](#credits)

*   [Donate](#donate)

*   [License](#license)

## Dependencies

*   [Pillow](https://python-pillow.org/)

*   [undetected chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

*   [BeautifulSoup](https://code.launchpad.net/beautifulsoup/)

*   [tktooltip](https://github.com/gnikit/tkinter-tooltip)

*   [ttkwidgets](https://pypi.org/project/ttkwidgets/)

*   [requests](https://requests.readthedocs.io/en/latest/)

*   [pyperclip](https://github.com/asweigart/pyperclip)

## Usage

The usage is pretty straightforward.

The GUI automatically loads all the news titles and their date. The user can renew the titles through menu>renew titles.

If no news was loaded, try to renew titles via menu>renew titles(bypass). It requires Chromedriver and Chrome in order
to bypass Cloudflare bot protection. A Chrome window will be launched off the screen to access the news (headless mode
gets detected by Cloudflare).

There are 8 themes.

The default theme is [Azure](https://github.com/rdbende/Azure-ttk-theme) dark. If the user clicks again on the azure theme, it will switch to Azure light and vice versa.

The GUI:

![alt text](https://github.com/LabAsim/scrape_tpp_gui/blob/main/assets/images/image.png)

## Convert to executable

The script can be converted to an .exe by running in your terminal:

```null
cd {path/to/scrape_tpp_gui_folder}
py scrape_tpp_gui_pyinstaller.py 
```

You should also convert updater.py to updater.exe to use **check for updates** command in the menu. Currently, auto-updating does not work as a py script.

    cd {path/to/updater_folder}
    py pyinstaller_updater.py

## TODO

*   **SQLite Database**

    *   [x] Save to db option in menu

    *   [x] Periodically autosave to db

    *   [x] Let the user choose the frequency of autosaving

    *   [x] Let the user whether to autosave or not

    *   [ ] Create a toplevel window containing all the news from
        the database

        *   [ ] Add search option based on date (Greek format DD-MM-YY)

        *   [ ] Add advanced search (author, category, date)

*   Code refactoring
	* [ ] Move the files from ./classes to ./source/classes dir & consequently, fix the paths for the rest of the code
	* [ ] Move images to source
	* [ ] Rename the camelCase/PascalCase .py files to snake_case style.

## Credits

Thanks to all the 3rd party packages maintainers and the StackOverflow users.

## Donate

Do not forget to donate monthly to [ThePressProject team](https://community.thepressproject.gr/?lang=en). Recurrent monthly donation/funding is the only way for a truly independent journalism to exist.

## License

ThePressProject Trademark, name and all of its content belong to the ThePressProject team.
The 3rd party packages have their own licenses.
All the code written by me is released under the MIT license.

***
