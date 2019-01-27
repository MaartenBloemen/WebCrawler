import random
import re
import threading
import time
import urllib.robotparser as robots
from contextlib import closing
from hashlib import sha256

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from repositories.crawler_repository import CrawlerRepository


class WebCrawlerJob(threading.Thread):
    __USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    __HEADER = {'User-Agent': __USER_AGENT}

    def __init__(self, domain, start_urls, include_patterns, exclude_patterns, hop_count=5, ignore_robots=False):
        self.crawler_repository = CrawlerRepository()

        self.domain = re.compile(r"https?://(www\.)?").sub('', domain).strip().strip('/')
        self.start_urls = start_urls
        self.urls = []
        self.crawled = []
        self.hop_count = hop_count
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.ignore_robots = ignore_robots

        if not ignore_robots:
            self.__robots_parser()

        threading.Thread.__init__(self)

    def run(self):
        for start_url in self.start_urls:
            self.urls.append({'url': start_url, 'depth': 0})
            while True:
                if len(self.urls) == 0:
                    break

                url = self.urls.pop(0)
                raw_html = self.__simple_get(url['url'])
                if raw_html is None:
                    continue
                self.crawled.append(url['url'])
                html = self.__cleaned_html_soup(raw_html)
                html_hash = sha256(raw_html).hexdigest()

                if not self.crawler_repository.exists_or_changed(url['url'], html_hash):
                    self.crawler_repository.register_scrape(url['url'], html_hash)
                    print('{}: {}, {}'.format(self.domain, html_hash, url['url']))
                else:
                    print('Already indexed: {}'.format(url['url']))
                self.__add_urls(html, url['depth'])
                time.sleep(random.randint(1, 3))
        self.clean_up()

    def clean_up(self):
        self.crawler_repository.close_db()

    def __add_urls(self, html_page, current_depth):
        if current_depth > self.hop_count != -1:
            return
        for a in html_page.find_all('a', href=True):
            href = a['href']
            if self.domain in href and not any(d.get('url', None) == href for d in self.urls) \
                    and href not in self.crawled and not self.__exclude(href) and self.robots.can_fetch('*', href):
                if href.startswith('/'):
                    self.urls.append({'url': self.domain + href, 'depth': current_depth + 1})
                else:
                    self.urls.append({'url': href, 'depth': current_depth + 1})

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

    def __cleaned_html_soup(self, raw_html):
        html = BeautifulSoup(raw_html, 'html.parser')
        for remove in html(['script', 'style']):
            remove.decompose()
        return html

    def __exclude(self, url):
        for pattern in self.exclude_patterns:
            if re.match(pattern, url):
                return True

        return False

    def __robots_parser(self):
        self.robots = robots.RobotFileParser()
        self.robots.set_url('https://www.{}/robots.txt'.format(self.domain))
        self.robots.read()

    def get_job_as_json(self):
        return {
            'name': self.domain,
            'start_urls': self.start_urls,
            'include_patterns': self.include_patterns,
            'exclude_patterns': self.exclude_patterns,
            'hop_count': self.hop_count,
            'ignore_robots': self.ignore_robots
        }
