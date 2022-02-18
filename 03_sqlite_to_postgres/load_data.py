import logging
import os
import sqlite3
from contextlib import closing
from dataclasses import dataclass


import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


BATCH_SIZE = 50


@dataclass
class SQLiteMetadata:
    movies: list
    genres: list
    persons: list
    movie_genre: list
    movie_person: list


@dataclass
class PostgresSaver:
    connection: _connection

    def __post_init__(self):
        self.cursor = self.connection.cursor()

    def _get_args(self, rows: list, args_string: str) -> str:
        return ','.join(self.cursor.mogrify(args_string, item).decode() for item in rows)

    def save_all_data(self, data: SQLiteMetadata) -> None:
        try:
            for rows in data.movies:
                # This approach more faster then execute_batch() from psycopg.extras
                # https://www.datacareer.de/blog/improve-your-psycopg2-executions-for-postgresql-in-python/
                args = self._get_args(rows, '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
                self.cursor.execute(f"""
                INSERT INTO content.film_work
                (id, title, description, creation_date, certificate, file_path, rating, type, created, modified)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING
                """)

            for rows in data.genres:
                args = self._get_args(rows, "(%s, %s, %s, %s, %s)")
                self.cursor.execute(f"""
                insert into content.genre
                (id, name, description, created, modified)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING
                """)

            for rows in data.persons:
                args = self._get_args(rows, "(%s, %s, %s, %s, %s)")
                self.cursor.execute(f"""
                insert into content.person
                (id, full_name, birth_date, created, modified)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING
                """)

            for rows in data.movie_genre:
                args = self._get_args(rows, "(%s, %s, %s, %s)")
                self.cursor.execute(f"""
                insert into content.genre_film_work
                (id, film_work_id, genre_id, created)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING
                """)

            for rows in data.movie_person:
                args = self._get_args(rows, "(%s, %s, %s, %s, %s)")
                self.cursor.execute(f"""
                insert into content.person_film_work
                (id, film_work_id, person_id, role, created)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING
                """)
        except psycopg2.Error as exc:
            logging.critical('Error occurred while writing: ', exc)


@dataclass
class SQLiteLoader:
    connection: sqlite3.Connection

    def load_from_table(self, table_name: str) -> list:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')  # noqa: S608
        while data := cursor.fetchmany(BATCH_SIZE):
            yield data

    def load_data(self):
        try:
            return SQLiteMetadata(
                movies=self.load_from_table('film_work'),
                genres=self.load_from_table('genre'),
                persons=self.load_from_table('person'),
                movie_person=self.load_from_table('person_film_work'),
                movie_genre=self.load_from_table('genre_film_work'),
            )
        except sqlite3.Error as exc:
            logging.critical('Error occurred while reading: ', exc)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)
    data = sqlite_loader.load_data()
    postgres_saver.save_all_data(data)


def env(key: str) -> str:
    return os.environ[key]


if __name__ == '__main__':
    load_dotenv()
    dsl = {
        'dbname': env('DB_NAME'),
        'user': env('DB_USER'),
        'password': env('DB_PASSWORD'),
        'host': env('DB_HOST'),
        'port': env('DB_PORT'),
        'options': '-c search_path=content',
    }
    with closing(sqlite3.connect('db.sqlite')) as sqlite_conn, \
         closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
