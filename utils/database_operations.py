"""Reading everything needed in one DataFrame"""
import json

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import asc
import pandas as pd

from utils.models import ActorsToMovie, Actor, Collection, Crew, CrewsToMovie, Genre, \
    Keyword, ProductionCompany, Movie, \
    ReferenceMovieId, ProductionCountry, UserRatingExternal, CollectionsToMovie, GenresToMovie, KeywordsToMovie, \
    ProductionCompaniesToMovie, ProductionCountriesToMovie, SpokenLanguagesToMovie

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
"""Create engine outside class to not create it every time"""
Session = sessionmaker(bind=create_engine('mysql+pymysql://root:pass@localhost/movies_system_prod'))

TMDB_API_KEY = 'f50831bf1fa264f6696f181b4c845225'


class DatabaseOperations:
    def __init__(self):
        """Create session to DB"""
        self.session = Session()

    def close_session(self):
        self.session.close()

    @staticmethod
    def process_db_list(list_from_db):
        if list_from_db:
            return [res for (res,) in list_from_db]
        else:
            return None

    def get_movie_by_movie_id(self, movie_id):
        movie = self.session.query(Movie).filter(Movie.movie_id == movie_id).first()
        return movie

    def populate_df(self):
        all_movies = self.session.query(Movie).all()

        list_to_create_df = []
        for movie_obj in all_movies:
            row_dict = self.create_df_row_for_movie(movie_obj)
            list_to_create_df.append(row_dict)

        df = pd.DataFrame(list_to_create_df)
        return df

    def create_df_row_for_movie(self, movie_obj):
        collection_name = self.get_collection_by_movie_id(movie_id=movie_obj.movie_id)
        list_actors = self.get_top_n_actors_by_movies_id(movie_id=movie_obj.movie_id)
        list_directors, list_producers, list_of_composers, list_of_screenplays = \
            self.get_director_producer_composers_screenplays_by_movie_id(movie_id=movie_obj.movie_id)
        list_genres = self.get_genres_by_movie_id(movie_id=movie_obj.movie_id)
        list_keywords = self.get_keywords_by_movie_id(movie_id=movie_obj.movie_id)
        list_prod_companies = self.get_prod_companies_by_movie_id(movie_id=movie_obj.movie_id)
        list_prod_countries = self.get_prod_countries_by_movie_id(movie_id=movie_obj.movie_id)
        list_spoken_languages = self.get_spoken_languages_by_movie_id(movie_id=movie_obj.movie_id)
        "create dict for qualified_movies_df"

        dict_of_data = {'movie_id': movie_obj.movie_id, 'budget': movie_obj.budget,
                        'original_language': movie_obj.original_language, 'title': movie_obj.title,
                        'overview': movie_obj.overview, 'popularity': movie_obj.popularity,
                        'release_date': movie_obj.release_date, 'revenue': movie_obj.revenue,
                        'runtime': movie_obj.runtime, 'tagline': movie_obj.tagline,
                        'vote_average': movie_obj.vote_average, 'vote_count': movie_obj.vote_count,
                        'genres': list_genres,
                        'collection': collection_name, 'actors': list_actors, 'directors': list_directors,
                        'producers': list_producers, 'composers': list_of_composers, 'screenplays': list_of_screenplays,
                        'keywords': list_keywords, 'production_company': list_prod_companies,
                        'production_country': list_prod_countries,
                        'spoken_languages': list_spoken_languages}

        return dict_of_data

    def get_top_n_actors_by_movies_id(self, movie_id, top_n=3):
        actors_orders_per_movie = self.session.query(Actor.name, ActorsToMovie.order). \
            filter(ActorsToMovie.movie_id == movie_id, ActorsToMovie.order < top_n). \
            filter(Actor.id == ActorsToMovie.actor_id).all()

        actors_per_movie = [actor_name + '_' + str(actor_order) for
                            (actor_name, actor_order) in actors_orders_per_movie]

        return actors_per_movie

    def get_movies_ids_ratings_by_user_id(self, user_id):
        user_ratings = self.session.query(UserRatingExternal.rating, ReferenceMovieId.movie_id,
                                          UserRatingExternal.datetime).filter(
            UserRatingExternal.user_id == user_id). \
            filter(ReferenceMovieId.reference_movie_id == UserRatingExternal.reference_movie_id).order_by(
            asc(UserRatingExternal.datetime)).all()

        return user_ratings

    def get_collection_by_movie_id(self, movie_id):
        try:
            collection_to_movie_obj = self.session.query(CollectionsToMovie).filter(
                CollectionsToMovie.movie_id == movie_id).one()
            if collection_to_movie_obj.collection_id:
                collection_obj = self.session.query(Collection).filter(
                    Collection.collection_id == collection_to_movie_obj.collection_id).first()
                return collection_obj.name
            else:
                return None
        except MultipleResultsFound:
            print('Multiple results found for collection to movies for movie id {}'.format(movie_id))
        except NoResultFound:
            pass

    def get_director_producer_composers_screenplays_by_movie_id(self, movie_id):
        producers = self.session.query(Crew.name). \
            filter(CrewsToMovie.movie_id == movie_id, CrewsToMovie.job == 'Producer'). \
            filter(Crew.id == CrewsToMovie.crew_id).all()

        directors = self.session.query(Crew.name). \
            filter(CrewsToMovie.movie_id == movie_id, CrewsToMovie.job == 'Director'). \
            filter(Crew.id == CrewsToMovie.crew_id).all()

        screenplays = self.session.query(Crew.name). \
            filter(CrewsToMovie.movie_id == movie_id, CrewsToMovie.job == 'Screenplay'). \
            filter(Crew.id == CrewsToMovie.crew_id).all()

        composers = self.session.query(Crew.name). \
            filter(CrewsToMovie.movie_id == movie_id, CrewsToMovie.job == 'Original Music Composer'). \
            filter(Crew.id == CrewsToMovie.crew_id).all()

        directors = self.process_db_list(directors)
        producers = self.process_db_list(producers)
        screenplays = self.process_db_list(screenplays)
        composers = self.process_db_list(composers)

        return directors, producers, composers, screenplays

    def get_genres_by_movie_id(self, movie_id):
        genres = self.session.query(Genre.name). \
            filter(GenresToMovie.movie_id == movie_id). \
            filter(Genre.genre_id == GenresToMovie.genre_id).all()

        genres = self.process_db_list(genres)

        return genres

    def get_keywords_by_movie_id(self, movie_id):
        keywords = self.session.query(Keyword.name). \
            filter(KeywordsToMovie.movie_id == movie_id). \
            filter(Keyword.keyword_id == KeywordsToMovie.keyword_id).all()

        keywords = self.process_db_list(keywords)

        return keywords

    def get_prod_companies_by_movie_id(self, movie_id):
        prod_companies = self.session.query(ProductionCompany.name). \
            filter(ProductionCompaniesToMovie.movie_id == movie_id). \
            filter(ProductionCompany.production_company_id == ProductionCompaniesToMovie.production_company_id).all()

        prod_companies = self.process_db_list(prod_companies)

        return prod_companies

    def get_prod_countries_by_movie_id(self, movie_id):
        prod_countries = self.session.query(ProductionCountry.name). \
            filter(ProductionCountriesToMovie.movie_id == movie_id). \
            filter(ProductionCountry.code == ProductionCountriesToMovie.code).all()

        prod_countries = self.process_db_list(prod_countries)

        return prod_countries

    def get_spoken_languages_by_movie_id(self, movie_id):
        spoken_languages = self.session.query(SpokenLanguagesToMovie.code). \
            filter(SpokenLanguagesToMovie.movie_id == movie_id).all()

        spoken_languages = self.process_db_list(spoken_languages)
        return spoken_languages

    def update_qualified_movies(self, list_of_movie_ids):
        all_movies = self.session.query(Movie).all()
        for movie_obj in all_movies:
            if movie_obj.movie_id in list_of_movie_ids:
                movie_obj.qualify = True
            else:
                movie_obj.qualify = False

        self.session.commit()

    def get_all_qualified_movies(self):
        all_movies = self.session.query(Movie).filter(Movie.qualify == True).all()
        return all_movies

    def update_poster_path(self, movie_obj):
        movie_id = movie_obj.movie_id
        request_url = 'https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US'.format(movie_id, TMDB_API_KEY)
        json_resp = requests.get(request_url)
        if json_resp.status_code == 200:
            response_dict = json.loads(json_resp.text)
            poster_path = response_dict.get('poster_path', None)
            if poster_path:
                movie_obj.poster_path = poster_path
                print('Poster path updated for movie_id: {}'.format(movie_id))
                self.session.commit()
            else:
                print('No poster path for movie_id: {}'.format(movie_id))
        else:
            print('Problems with movie_id: {}'.format(movie_id))
            print(json_resp.status_code)
        print('---------------------')



#Updating poster path as our data is old


#db_operations = DatabaseOperations()
#all_movies = db_operations.get_all_qualified_movies()
#count_passed = 0
#print(len(all_movies))
#for movie_obj in all_movies:
#    db_operations.update_poster_path(movie_obj)
#    count_passed += 1
#    if count_passed % 500 == 0:
#        print('Updated movies: {}'.format(count_passed))
#
