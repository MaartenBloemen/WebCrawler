import random
import re
import threading
import time
from contextlib import closing
from hashlib import sha256

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from database_manager import ScraperDatabaseManager


class WebScrapeJob(threading.Thread):
    __USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    __HEADER = {'User-Agent': __USER_AGENT}

    def __init__(self, domain, start_urls, excludes, hop_count=5):
        self.db_manager = ScraperDatabaseManager()

        self.domain = domain
        self.start_urls = start_urls
        self.urls = []
        self.crawled = []
        self.hop_count = hop_count
        self.excludes = excludes
        threading.Thread.__init__(self)

    def run(self):
        for start_url in self.start_urls:
            self.urls.append(start_url)
            while True:
                if len(self.urls) == 0:
                    break

                url = self.urls.pop(0)
                raw_html = self.__simple_get(url)
                if raw_html is None:
                    continue
                self.crawled.append(url)
                html = BeautifulSoup(raw_html, 'html.parser')
                html_hash = sha256(raw_html).hexdigest()

                if not self.db_manager.exists_or_changed(url, html_hash):
                    self.db_manager.register_scrape(url, html_hash)
                    print('{}: {}, {}'.format(self.domain, html_hash, url))
                else:
                    print('Already indexed: {}'.format(url))
                self.__add_urls(html, )
                time.sleep(random.randint(1, 3))
        self.db_manager.print_db()
        self.db_manager.close_db()

    def __add_urls(self, html_page):
        added = 0
        for a in html_page.find_all('a', href=True):
            href = a['href']
            if self.domain in href and href not in self.urls and href not in self.crawled and not self.__exclude(href):
                if href.startswith('/'):
                    self.urls.append(self.domain + href)
                else:
                    self.urls.append(href)
                added += 1
            if added >= self.hop_count != -1:
                break

    def __simple_get(self, url):
        try:
            with closing(get(url, headers=self.__HEADER, stream=True)) as resp:
                if self.__is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException:
            return None

    def __is_good_response(self, resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def __exclude(self, url):
        for pattern in self.excludes:
            if re.match(pattern, url):
                return True

        return False
