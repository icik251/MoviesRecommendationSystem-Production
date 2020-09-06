from fuzzywuzzy import fuzz
from flask_app import db
from flask_app.models import Movie


class SearchHandler:
    def __init__(self, searched_token):
        self.searched_tokens = searched_token

    def extract_qualified_movies(self):
        all_movies = db.session.query(Movie.title, Movie.poster_path, Movie.vote_average, Movie.vote_count,
                                      Movie.release_date, Movie.movie_id, Movie.overview). \
            filter(Movie.qualify == True).all()

        list_of_results = []
        "perform fuzzy"
        for item in all_movies:
            if item.title:
                if fuzz.token_set_ratio(item.title.lower(), self.searched_tokens) > 95:
                    list_of_results.append(item)

        """return list of db objects"""
        return list_of_results
