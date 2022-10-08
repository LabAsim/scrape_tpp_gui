import dataclasses
from typing import Any


@dataclasses.dataclass
class NewsDataclass:
    date: Any
    url: str = ''
    main_content: str = ''
    summary: str = ''
    title: str = ''

    def __str__(self):
        return f'Name:"{self.url}"'