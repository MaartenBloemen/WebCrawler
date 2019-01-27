from contextlib import closing

from repositories.database_repository import DatabaseRepository


class CrawlerRepository(DatabaseRepository):
    __CRAWLER_DB = 'config/databases/crawler.db'
    __CRAWLER_SCHEMA = 'config/schemas/crawler_schema.sql'

    def __init__(self):
        super(CrawlerRepository, self).__init__(self.__CRAWLER_DB, self.__CRAWLER_SCHEMA)

    def exists_or_changed(self, url, html_hash):
        with closing(self.connection.cursor()) as cursor:
            query = '''
            SELECT url, hash FROM crawled
            WHERE url = :url
            '''

            cursor.execute(query, {'url': url})
            for row in cursor.fetchall():
                found_url, found_hash = row
                return found_hash == html_hash

            return False

    def register_scrape(self, url, html_hash):
        with closing(self.connection.cursor()) as cursor:
            query = '''
            INSERT OR REPLACE INTO crawled (url, hash)
            VALUES (:url, :hash)
            '''

            cursor.execute(query, {'url': url, 'hash': html_hash})
