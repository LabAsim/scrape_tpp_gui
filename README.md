# ThePressProject Scraper GUI

## Description

This is my first project in order to learn Python. 
I have built it to access the news faster and in a more aggregated way than just reading the site.
It scrapes the news categories of ThePressProject site.

It has been tested in Python 3.10. It heavily relies on 3rd party packages.


## Table of Contents
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Convert to executable](#convert-to-executable)
- [Credits](#credits)
- [Donate](#donate)
- [License](#license)

## Dependencies

- Pillow
- undetected chromedriver
- BeautifulSoup
- [tktooltip](https://github.com/gnikit/tkinter-tooltip)
- ttkwidgets
- requests

## Usage

The usage is pretty straightforward. 

The GUI automatically loads all the news titles and their date. The user can renew the titles through menu>renew titles.

If no news are loaded, try to renew titles via menu>renew titles(bypass). It requires Chromedriver and Chrome in order 
to bypass Cloudflare bot protection. A Chrome window will be launched off the screen to access the news (headless mode
gets detected by Cloudflare).

There are 8 themes. 

The default theme is [Azure](https://github.com/rdbende/Azure-ttk-theme) dark. If the user clicks again on the azure theme, it will switch to Azure light and vice versa. 

The GUI:


    
![alt text](https://github.com/LabAsim/scrape_tpp_gui/blob/main/assets/images/image.png)


## Convert to executable

The script can be converted to an .exe by running in your terminal: 

	py scrape_tpp_gui_pyinstaller.py 


Note that the folders images & source, as well as, the .exe must be in the **same directory** in order the .exe to successfully run.

## Credits

Thanks to all the 3rd party packages maintainers and the StackOverflow users.
## Donate

Do not forget to donate monthly to [ThePressProject team](https://community.thepressproject.gr/?lang=en). Recurrent monthly donation/funding is the only way for a truly independable journalism to exist. 

## License
ThePressProject Trademark, name and all of its content belong to the ThePressProject team. 
The 3rd party packages have their own licenses.
All the code written by me is released under the MIT license.

---


