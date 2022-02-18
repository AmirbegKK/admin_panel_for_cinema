-- Создание отдельной схемы для контента:
CREATE SCHEMA IF NOT EXISTS content;
CREATE EXTENSION "pgcrypto";

-- Жанры кинопроизведений: 
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    description text,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Участники фильмов:
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name text NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Информация о фильмах:
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    description text,
    creation_date DATE,
    rating float,
    type text NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Информация о фильмах и жанрах:
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    genre_id uuid NOT NULL REFERENCES content.genre,
    film_work_id uuid NOT NULL REFERENCES content.film_work,
    created timestamp with time zone
);

-- Информация об актерах и фильмах:
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id uuid NOT NULL REFERENCES content.person,
    film_work_id uuid NOT NULL REFERENCES content.film_work,
    role text NOT NULL,
    created timestamp with time zone
);

CREATE INDEX genre_name_idx ON content.genre (name)
CREATE INDEX filmwork_type_idx ON content.film_work (type)
CREATE INDEX filmwork_creation_date_idx ON content.film_work (creation_date)
CREATE INDEX filmwork_rating_idx ON content.film_work (rating)
CREATE UNIQUE INDEX film_work_person ON content.person_film_work (film_work_id, person_id, role); 
CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);
