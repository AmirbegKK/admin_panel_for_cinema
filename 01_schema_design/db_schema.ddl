-- Создание отдельной схемы для контента:
CREATE SCHEMA IF NOT EXISTS content;

-- Жанры кинопроизведений: 
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    description text,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Участники фильмов:
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name text NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

-- Информация о фильмах:
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
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
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    created timestamp with time zone
);

-- Информация об актерах и фильмах:
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    role text NOT NULL,
    created timestamp with time zone
);

CREATE UNIQUE INDEX film_work_person ON content.person_film_work (film_work_id, person_id, role); 
CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);
