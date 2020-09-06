from datetime import datetime
from flask import flash
from sqlalchemy import asc, desc

from flask_app import db
from flask_app.models import UsersToMovies, Movie


class UserLibraryHandler:

    def __init__(self, user_id):
        self.user_id = user_id
        self.dict_of_movie_id_in_library = dict()
        self.all_library_movies_by_id = list()

    def _create_list_of_library_movies(self):
        self.all_library_movies_by_id = db.session.query(UsersToMovies.movie_id).filter(
            UsersToMovies.user_id == self.user_id).all()

        if self.all_library_movies_by_id:
            self.all_library_movies_by_id = [res for (res,) in self.all_library_movies_by_id]

    "check which movies are already into favourites for current user"
    def get_dict_of_movie_id_in_library(self, list_of_movies_obj):
        if not self.all_library_movies_by_id:
            self._create_list_of_library_movies()

        for movie_obj in list_of_movies_obj:
            if movie_obj.movie_id in self.all_library_movies_by_id:
                self.dict_of_movie_id_in_library[movie_obj.movie_id] = True
            else:
                self.dict_of_movie_id_in_library[movie_obj.movie_id] = False

        return self.dict_of_movie_id_in_library

    "process for checked boxes and unchecked movies"
    def update_user_library(self, list_of_checked_boxes):
        """To run this function self.dict_of_movie_id_in_library must be created"""
        are_changes_made = False

        for key, value in self.dict_of_movie_id_in_library.items():
            if value is False:
                if key in list_of_checked_boxes:
                    are_changes_made = True
                    "user has checked new movie to add into favourites"
                    self.dict_of_movie_id_in_library[key] = True
                    new_movie_to_user = UsersToMovies(user_id=self.user_id, movie_id=key,
                                                      datetime=datetime.now())
                    db.session.add(new_movie_to_user)
            else:
                if key not in list_of_checked_boxes:
                    are_changes_made = True
                    self.dict_of_movie_id_in_library[key] = False
                    self.remove_movie_from_library(movie_id=key)

        if are_changes_made:
            db.session.commit()
            flash("Changes completed!")

    def update_user_ratings(self, list_of_ratings):
        """get all library movies by user"""
        all_movies_to_user = db.session.query(UsersToMovies).filter(
            UsersToMovies.user_id == self.user_id).order_by(
            desc(UsersToMovies.datetime)).all()

        are_changes_made = False
        for rating, user_to_movie in zip(list_of_ratings, all_movies_to_user):
            """if rating is 0 because that's how it comes from the site"""
            if float(rating) == 0:
                rating = None
            else:
                rating = float(rating)

            if user_to_movie.rating != rating:
                are_changes_made = True
                user_to_movie.rating = rating

        if are_changes_made:
            flash("Selected ratings updated successfully!")
            db.session.commit()

    def remove_movie_from_library(self, movie_id):
        UsersToMovies.query.filter(UsersToMovies.user_id == self.user_id,
                                   UsersToMovies.movie_id == movie_id).delete()

    def get_all_library_movies_and_ratings(self):
        all_lib_movies_ratings = (db.session.query(Movie, UsersToMovies.rating)
                                  .filter(UsersToMovies.user_id == self.user_id)
                                  .filter(Movie.movie_id == UsersToMovies.movie_id).order_by(
            desc(UsersToMovies.datetime)).all())

        return all_lib_movies_ratings
