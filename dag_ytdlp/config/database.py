from os import environ

from ..utils.database import get_database_url

DIALECT = "postgresql"
DRIVER = "psycopg2"
HOST = environ["PGSQL_HOST"]
DATABASE = environ["PGSQL_DB"]
PORT = environ["PGSQL_PORT"]
USERNAME = environ["PGSQL_USER"]
PASSWD = environ["PGSQL_PASSWORD"]


DATABASE_URL = get_database_url(DIALECT, DRIVER, USERNAME, PASSWD, HOST, PORT, DATABASE)
