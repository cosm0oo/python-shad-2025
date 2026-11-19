from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


SAVED_JSON_DIR = Path(__file__).parent / 'visited_paths'


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc:
        if parsed.netloc not in ['ru.wikipedia.org', 'www.ru.wikipedia.org']:
            return url
        path = parsed.path
    else:
        path = url
    if path.startswith('/wiki/'):
        return f"https://ru.wikipedia.org{path}"
    return url


def distance(source_url: str, target_url: str) -> int | None:
    visited = set()
    current_url = _normalize_url(source_url)
    target_url = _normalize_url(target_url)
    dist = 0

    if current_url == target_url:
        return 0

    while True:
        if current_url in visited:
            return None

        visited.add(current_url)

        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return None

        parser_output = content_div.find('div', class_='mw-parser-output')
        if not parser_output:
            return None

        first_paragraph = None
        for element in parser_output.children:
            if element.name == 'p':
                text = element.get_text(strip=True)
                if text and len(text) > 50:
                    first_paragraph = element
                    break

        if not first_paragraph:
            return None

        links = []
        for link in first_paragraph.find_all('a', href=True):
            href = link['href']
            if href.startswith('/wiki/'):
                article_name = href.split('/wiki/')[1].split('#')[0]
                if ':' in article_name:
                    continue
                full_url = _normalize_url(href)
                if full_url not in visited:
                    links.append(full_url)

        if not links:
            return None

        current_url = links[0]
        dist += 1

        if current_url == target_url:
            return dist
