from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Table, Text
from sqlalchemy.dialects.mysql import BIGINT, BIT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Actor(Base):
    __tablename__ = 'actors'

    id = Column(BIGINT(20), primary_key=True)
    gender = Column(BIGINT(20))
    name = Column(Text)


class Collection(Base):
    __tablename__ = 'collections'

    collection_id = Column(BIGINT(20), primary_key=True)
    name = Column(Text)

    movies = relationship('Movie', secondary='collections_to_movies')


class Crew(Base):
    __tablename__ = 'crews'

    id = Column(BIGINT(20), primary_key=True)
    gender = Column(BIGINT(20))
    name = Column(Text)


class Genre(Base):
    __tablename__ = 'genres'

    genre_id = Column(BIGINT(20), primary_key=True)
    name = Column(Text)

    movies = relationship('Movie', secondary='genres_to_movies')


class Keyword(Base):
    __tablename__ = 'keywords'

    keyword_id = Column(BIGINT(20), primary_key=True)
    name = Column(Text)

    movies = relationship('Movie', secondary='keywords_to_movies')


class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(BIGINT(20), primary_key=True)
    budget = Column(BIGINT(20))
    homepage = Column(Text)
    imdb_id = Column(Text)
    original_language = Column(Text)
    original_title = Column(Text)
    overview = Column(Text)
    popularity = Column(Float(asdecimal=True))
    poster_path = Column(Text)
    release_date = Column(DateTime)
    revenue = Column(Float(asdecimal=True))
    runtime = Column(Float(asdecimal=True))
    status = Column(Text)
    tagline = Column(Text)
    title = Column(Text)
    vote_average = Column(Float(asdecimal=True))
    vote_count = Column(Float(asdecimal=True))
    qualify = Column(BIT(1))

    production_companys = relationship('ProductionCompany', secondary='production_companies_to_movies')


class ProductionCompany(Base):
    __tablename__ = 'production_companies'

    production_company_id = Column(BIGINT(20), primary_key=True)
    name = Column(Text)


class ProductionCountry(Base):
    __tablename__ = 'production_countries'

    code = Column(String(200), primary_key=True)
    name = Column(Text)

    movies = relationship('Movie', secondary='production_countries_to_movies')


class ReferenceMovieId(Base):
    __tablename__ = 'reference_movie_ids'

    reference_movie_id = Column(BIGINT(20), primary_key=True, nullable=False)
    movie_id = Column(BIGINT(20), primary_key=True, nullable=False)
    imdb_id = Column(BIGINT(20))


class SpokenLanguage(Base):
    __tablename__ = 'spoken_languages'

    code = Column(String(200), primary_key=True)
    name = Column(Text)

    movies = relationship('Movie', secondary='spoken_languages_to_movies')


class UserRatingExternal(Base):
    __tablename__ = 'user_ratings_external'

    user_id = Column(BIGINT(20), primary_key=True, nullable=False)
    reference_movie_id = Column(BIGINT(20), primary_key=True, nullable=False, index=True)
    rating = Column(Float(asdecimal=True))
    datetime = Column(DateTime)


class User(Base):
    __tablename__ = 'users'

    id = Column(BIGINT(20), primary_key=True)
    username = Column(String(60), unique=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(128))


class ActorsToMovie(Base):
    __tablename__ = 'actors_to_movies'

    actor_id = Column(ForeignKey('actors.id'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)
    cast_id = Column(BIGINT(20), primary_key=True, nullable=False)
    character = Column(Text)
    credit_id = Column(Text)
    order = Column(BIGINT(20))

    actor = relationship('Actor')
    movie = relationship('Movie')


class CollectionsToMovie(Base):
    __tablename__ = 'collections_to_movies'

    collection_id = Column(ForeignKey('collections.collection_id'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)

    collection = relationship('Collection')
    movie = relationship('Movie')


class CrewsToMovie(Base):
    __tablename__ = 'crews_to_movies'

    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False)
    crew_id = Column(ForeignKey('crews.id'), primary_key=True, nullable=False, index=True)
    job = Column(String(200), primary_key=True, nullable=False)
    credit_id = Column(Text)
    department = Column(Text)

    crew = relationship('Crew')
    movie = relationship('Movie')


class GenresToMovie(Base):
    __tablename__ = 'genres_to_movies'

    genre_id = Column(ForeignKey('genres.genre_id'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)

    genre = relationship('Genre')
    movie = relationship('Movie')


class KeywordsToMovie(Base):
    __tablename__ = 'keywords_to_movies'

    keyword_id = Column(ForeignKey('keywords.keyword_id'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)

    keyword = relationship('Keyword')
    movie = relationship('Movie')


class ProductionCompaniesToMovie(Base):
    __tablename__ = 'production_companies_to_movies'

    production_company_id = Column(ForeignKey('production_companies.production_company_id'), primary_key=True,
                                   nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)

    movie = relationship('Movie')
    production_company = relationship('ProductionCompany')


class ProductionCountriesToMovie(Base):
    __tablename__ = 'production_countries_to_movies'

    code = Column(ForeignKey('production_countries.code'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)

    production_country = relationship('ProductionCountry')
    movie = relationship('Movie')


class Recommendation(Base):
    __tablename__ = 'recommendations'

    main_movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False)
    recommended_movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)
    similarity = Column(Float(asdecimal=True))
    features = Column(String(8000))

    main_movie = relationship('Movie', primaryjoin='Recommendation.main_movie_id == Movie.movie_id')
    recommended_movie = relationship('Movie', primaryjoin='Recommendation.recommended_movie_id == Movie.movie_id')


class SpokenLanguagesToMovie(Base):
    __tablename__ = 'spoken_languages_to_movies'

    code = Column(ForeignKey('spoken_languages.code'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)

    spoken_language = relationship('SpokenLanguage')
    movie = relationship('Movie')


class UsersToMovie(Base):
    __tablename__ = 'users_to_movies'

    user_id = Column(ForeignKey('users.id'), primary_key=True, nullable=False)
    movie_id = Column(ForeignKey('movies.movie_id'), primary_key=True, nullable=False, index=True)
    rating = Column(Float(asdecimal=True))
    datetime = Column(DateTime)

    movie = relationship('Movie')
    user = relationship('User')
