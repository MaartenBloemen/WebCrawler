import random
import string
from contextlib import closing
from hashlib import sha256

from repositories.database_repository import DatabaseRepository


class UserRepository(DatabaseRepository):
    __CRAWLER_DB = 'config/databases/users.db'
    __CRAWLER_SCHEMA = 'config/schemas/users_schema.sql'

    __SALT_LENGTH = 10

    def __init__(self):
        super(UserRepository, self).__init__(self.__CRAWLER_DB, self.__CRAWLER_SCHEMA)
        self.register_user('admin', 'admin')

    def verify_credentials(self, name, password):
        with closing(self.connection.cursor()) as cursor:
            query = '''
            SELECT name, password, salt FROM users
            WHERE name = :name
            '''

            cursor.execute(query, {'name': name})
            for row in cursor.fetchall():
                found_name, found_password, found_salt = row
                return found_password == sha256(password + found_salt).hexdigest()

            return False

    def register_user(self, name, password):
        salt = self.__random_salt()
        hashed_password = sha256(password + salt).hexdigest()

        with closing(self.connection.cursor()) as cursor:
            query = '''
            INSERT OR IGNORE INTO users (name, password, salt)
            VALUES (:name, :password, :salt)
            '''

            cursor.execute(query, {'name': name, 'password': hashed_password, 'salt': salt})

    def __random_salt(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                       for _ in range(self.__SALT_LENGTH))
