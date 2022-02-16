import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Person(UUIDMixin, TimeStampMixin):
    full_name = models.CharField(_('ФИО'), max_length=255)
    filmworks = models.ManyToManyField('Filmwork', through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('актер')
        verbose_name_plural = _('актеры')

    def __str__(self) -> str:
        return self.full_name


class Genre(UUIDMixin, TimeStampMixin):
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    filmworks = models.ManyToManyField('Filmwork', through='GenreFilmwork')

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self) -> str:
        return self.name


class Filmwork(UUIDMixin, TimeStampMixin):
    
    class Genres(models.TextChoices):
        MOVIE = 'movie', _('Фильм')
        TV_SHOW = 'TV show', _('ТВ шоу')


    title = models.CharField(_('заголовок'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата производства'), blank=True)
    rating = models.FloatField(_('рейтинг'), blank=True,
                                validators=[MinValueValidator(0),
                                            MaxValueValidator(100)])
    type = models.CharField(_('тип'),default=Genres.MOVIE, max_length=128, choices=Genres.choices)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self) -> str:
        return self.title
    

class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('жанр фильма')
        verbose_name_plural = _('жанры фильма')


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person =  models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('роль'), null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('актёр фильма')
        verbose_name_plural = _('актёры фильма')