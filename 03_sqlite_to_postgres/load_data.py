import sqlite3
from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


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

    def save_all_data(self, data: SQLiteMetadata) -> None:
        try:
            for rows in data.movies:
                for row in rows:
                    self.connection.cursor().execute("""
                insert into content.film_work
                (id, title, description, creation_date, certificate, file_path, rating, type, created, modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, row)

            for rows in data.genres:
                for row in rows:
                    self.connection.cursor().execute("""
                insert into content.genre
                (id, name, description, created, modified)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, row)

            for rows in data.persons:
                for row in rows:
                    self.connection.cursor().execute("""
                insert into content.person
                (id, full_name, birth_date, created, modified)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, row)

            for rows in data.movie_genre:
                for row in rows:
                    self.connection.cursor().execute("""
                insert into content.genre_film_work
                (id, film_work_id, genre_id, created)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, row)

            for rows in data.movie_person:
                for row in rows:
                    self.connection.cursor().execute("""
                insert into content.person_film_work
                (id, film_work_id, person_id, role, created)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, row)
        except psycopg2.Error as exc:
            print('Error occurred while writing: ', exc)


@dataclass
class SQLiteLoader:
    connection: sqlite3.Connection

    def load_from_table(self, table_name: str) -> list:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')  # noqa: S608
        while data := cursor.fetchmany(20):
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
            print('Error occurred while reading: ', exc)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)
    data = sqlite_loader.load_data()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {
        'dbname': 'movies_database',
        'user': 'app',
        'password': '123qwe',
        'host': 'localhost',
        'port': 5432,
        'options': '-c search_path=content',
    }
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
