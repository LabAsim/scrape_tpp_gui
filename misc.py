import os

url_list = {"newsroom": ["https://thepressproject.gr/article_type/newsroom/",
                         "https://thepressproject.gr/article_type/newsroom/page/2/"],
            "politics": "https://thepressproject.gr/category/politics/",
            "economy": "https://thepressproject.gr/category/economy/",
            "international": "https://thepressproject.gr/category/international/",
            "report": "https://thepressproject.gr/article_type/report/",
            "analysis": "https://thepressproject.gr/article_type/analysis/"}

url_list_second_page = {"newsroom": "https://thepressproject.gr/article_type/newsroom/page/2/",
                        "politics": "https://thepressproject.gr/category/politics/page/2/",
                        "economy": "https://thepressproject.gr/category/economy/page/2/",
                        "international": "https://thepressproject.gr/category/international/page/2/",
                        "report": "https://thepressproject.gr/article_type/report/page/2/",
                        "analysis": "https://thepressproject.gr/article_type/analysis/page/2/"}


dir_path = os.path.dirname(os.path.realpath(__file__))

themes_paths = {"azure": os.path.join(dir_path, 'source/azure/azure.tcl'),
                "plastik": os.path.join(dir_path, 'source/plastik/plastik.tcl'),
                "radiance": os.path.join(dir_path, 'source/radiance/radiance.tcl'),
                "aquativo": os.path.join(dir_path, 'source/aquativo/aquativo.tcl'),
                "adapta": os.path.join(dir_path, 'source/adapta/adapta.tcl'),
                "yaru": os.path.join(dir_path, 'source/yaru/yaru.tcl'),
                "arc": os.path.join(dir_path, 'source/arc/arc.tcl')}