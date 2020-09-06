from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

from flask_app import db
from flask_app.models import UsersToMovies
from flask_app.services.loader_handler import LoaderHandler

loader_handler = LoaderHandler()


class RecommendationHandlerProfile:
    def __init__(self, user_id):
        """load everything needed"""
        """get all needed items from loader"""
        self.TFIDF_VECTORIZER_MATRIX = loader_handler.get_tfidf_vectorizer_matrix()
        self.TF_VECTORIZER_MATRIX = loader_handler.get_tf_vectorizer_matrix()
        """copy dataframe as we make changes to it"""
        self.qualified_movies_df = loader_handler.get_movie_df().copy(deep=True)

        self.user_id = user_id
        self.dict_of_movie_id_preference = dict()

        self.user_profile = None
        self.profile_best_matches = None

    def _build_user_preferences(self):
        """get all movies from library by user"""
        all_movies = db.session.query(UsersToMovies).filter(
                UsersToMovies.user_id == self.user_id).all()

        for item in all_movies:
            """check if movie is in library or not"""
            if item.rating is not None:
                if 0.5 <= item.rating <= 1:
                    self.dict_of_movie_id_preference[item.movie_id] = -2
                elif 1.5 <= item.rating <= 2.5:
                    self.dict_of_movie_id_preference[item.movie_id] = -1
                elif 3.5 <= item.rating <= 4:
                    self.dict_of_movie_id_preference[item.movie_id] = 1
                elif item.rating >= 4.5:
                    self.dict_of_movie_id_preference[item.movie_id] = 2

    def _add_user_preferences_to_df(self):

        def populate_user_preference(movie_id):
            if movie_id in self.dict_of_movie_id_preference.keys():
                return self.dict_of_movie_id_preference[movie_id]
            else:
                return 0

        self.qualified_movies_df['user_preferences'] = self.qualified_movies_df['movie_id'].apply((
            lambda x: populate_user_preference(x)))

    def _create_user_profile(self):
        """make dot product between users preference list, example: [2,-1,0,0,1,0,-2,1,1] and TF matrix
        to create user profile vector with len == len(vocabulary)"""

        user_favourites_list = list(self.qualified_movies_df['user_preferences'])
        """adding dimension on 'user_favourite_list' and transposing TF matrix"""
        self.user_profile = linear_kernel([user_favourites_list], self.TF_VECTORIZER_MATRIX.T)

    def _calculate_similarity_user_profile_tfidf(self):
        self.profile_best_matches = cosine_similarity(self.user_profile, self.TFIDF_VECTORIZER_MATRIX)[0]

    def _remove_movies_already_in_library(self, list_tuples_of_idx_similarity):
        result_list_tuples_of_idx_similarity = []
        for tuple_idx_similarity in list_tuples_of_idx_similarity:
            if self.qualified_movies_df.loc[tuple_idx_similarity[0], 'movie_id'] in self.dict_of_movie_id_preference.keys():
                continue
            else:
                result_list_tuples_of_idx_similarity.append(tuple_idx_similarity)

        return result_list_tuples_of_idx_similarity

    def get_recommendations(self, page_num=1, request_id='good'):
        self._build_user_preferences()
        self._add_user_preferences_to_df()
        self._create_user_profile()
        self._calculate_similarity_user_profile_tfidf()

        if self.profile_best_matches is not None:
            list_tuples_of_idx_similarity = list(enumerate(self.profile_best_matches))
            list_tuples_of_idx_similarity = self._remove_movies_already_in_library(list_tuples_of_idx_similarity)

            if request_id == 'good':
                """sort it by value before returning it"""
                list_tuples_of_idx_similarity = sorted(list_tuples_of_idx_similarity, key=lambda x: x[1], reverse=True)

            elif request_id == 'neutral':
                """sort by abs value to get most closed movies to 0"""
                list_tuples_of_idx_similarity = sorted(list_tuples_of_idx_similarity, key=lambda x: abs(x[1]))

            """get only the movies for the needed page, and their indices"""
            list_tuples_of_idx_similarity = list_tuples_of_idx_similarity[(page_num-1)*10:page_num*10]
            movie_indices = [i[0] for i in list_tuples_of_idx_similarity]

            """add similarity column"""
            self.qualified_movies_df = self.qualified_movies_df.iloc[movie_indices]
            self.qualified_movies_df['similarity'] = [i[1] for i in list_tuples_of_idx_similarity]

            """return qualified_movies_df with the chosen movie indices"""
            return self.qualified_movies_df
