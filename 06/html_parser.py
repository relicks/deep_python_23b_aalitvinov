from abc import ABC, abstractmethod
from html.parser import HTMLParser


class HTMLDataParser(HTMLParser, ABC):
    @abstractmethod
    def handle_data(self, data: str) -> None:
        pass

    @property
    @abstractmethod
    def parsed_data(self) -> list[str]:
        pass


class WordParser(HTMLDataParser, HTMLParser):
    def __init__(self):
        super().__init__()
        self._text: list[str] = []

    def handle_data(self, data):
        start_tag = self.get_starttag_text()
        parsed_data = [word.lower() for word in data.split() if word.isalpha()]
        if (
            start_tag is not None
            and parsed_data
            and not any(substr in start_tag for substr in ("script", "style"))
        ):
            self._text.extend(parsed_data)

    @property
    def parsed_data(self) -> list[str]:
        return self._text


def parse_html(body: str) -> list[str]:
    parser = WordParser()
    parser.feed(body)
    return parser.parsed_data
