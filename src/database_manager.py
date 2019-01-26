import os
import sqlite3


class ScraperDatabaseManager:
    __SCRAPED_DB = 'scraper.db'
    __SCRAPED_SCHEMA = 'scraped_schema.sql'

    def __init__(self):
        db_is_new = not os.path.exists(self.__SCRAPED_DB)
        self.__connection = sqlite3.connect(self.__SCRAPED_DB, check_same_thread=False)
        if db_is_new:
            with open(self.__SCRAPED_SCHEMA, 'rt') as f:
                schema = f.read()
            self.__connection.executescript(schema)

    def close_db(self):
        self.__connection.commit()
        self.__connection.close()

    def print_db(self):
        cursor = self.__connection.cursor()

        cursor.execute("SELECT url, hash FROM scraped")

        for row in cursor.fetchall():
            found_url, found_hash = row
            print('{}: {}'.format(found_url, found_hash))

    def exists_or_changed(self, url, html_hash):
        cursor = self.__connection.cursor()

        query = '''
        SELECT url, hash FROM scraped
        WHERE url = :url
        '''

        cursor.execute(query, {'url': url})
        for row in cursor.fetchall():
            found_url, found_hash = row
            return found_hash == html_hash

        return False

    def register_scrape(self, url, html_hash):
        cursor = self.__connection.cursor()

        query = '''
        INSERT OR REPLACE INTO scraped (url, hash)
        VALUES (:url, :hash)
        '''

        cursor.execute(query, {'url': url, 'hash': html_hash})
