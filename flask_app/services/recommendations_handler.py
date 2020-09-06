import json
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy import asc, desc

from flask_app import db
from flask_app.models import Recommendation, Movie, UsersToMovies
from flask_app.services.loader_handler import LoaderHandler

"""blocks warnings from pandas"""
pd.options.mode.chained_assignment = None
loader_handler = LoaderHandler()


class RecommendationsHandler:
    def __init__(self, movie_id, user_id):
        """get all needed items from loader"""
        self.DICT_OF_MOVIE_ID_INDEX = loader_handler.get_dict_of_movie_id_index()
        self.COUNT_VECTORIZER_MATRIX = loader_handler.get_count_vectorizer_matrix()
        self.COUNT_VECTORIZER = loader_handler.get_count_vectorizer()
        """copy dataframe as we make changes to it"""
        self.qualified_movies_df = loader_handler.get_movie_df().copy(deep=True)

        """create other items needed"""
        self.movie_id = int(movie_id)
        self.user_id = int(user_id)
        self.movie_idx = self.DICT_OF_MOVIE_ID_INDEX.get(self.movie_id, None)
        self.list_of_recommendation_features_dicts = list()
        self.recommendations_df = None

    def _calculate_similarity_by_movie_idx(self):
        similarity_vector = linear_kernel(self.COUNT_VECTORIZER_MATRIX[self.movie_idx], self.COUNT_VECTORIZER_MATRIX)[0]
        """enumerate the vector so we have the index of every movie and the token matches as values"""
        list_tuples_of_idx_similarity = list(enumerate(similarity_vector))
        """sort it by value before returning it"""
        list_tuples_of_idx_similarity = sorted(list_tuples_of_idx_similarity, key=lambda x: x[1], reverse=True)

        return list_tuples_of_idx_similarity

    def _remove_movie_already_in_library(self, list_tuples_of_idx_similarity):
        """get movies in library"""
        list_of_library_movie_ids = db.session.query(UsersToMovies.movie_id).filter(
            UsersToMovies.user_id == self.user_id).all()

        list_of_library_movie_ids = [x for (x,) in list_of_library_movie_ids]

        result_list_tuples_of_idx_similarity = []
        for tuple_idx_similarity in list_tuples_of_idx_similarity:
            if self.qualified_movies_df.loc[tuple_idx_similarity[0], 'movie_id'] in list_of_library_movie_ids and \
                    self.movie_id != self.qualified_movies_df.loc[tuple_idx_similarity[0], 'movie_id']:
                continue
            else:
                result_list_tuples_of_idx_similarity.append(tuple_idx_similarity)

        return result_list_tuples_of_idx_similarity

    def _get_recommendations(self, top_n=50):
        list_tuples_of_idx_similarity = self._calculate_similarity_by_movie_idx()
        list_tuples_of_idx_similarity = self._remove_movie_already_in_library(list_tuples_of_idx_similarity)

        """get top n movies and their indices"""
        list_tuples_of_idx_similarity = list_tuples_of_idx_similarity[0:top_n + 1]
        movie_indices = [i[0] for i in list_tuples_of_idx_similarity]

        """return qualified_movies_df with the chosen movie indices and dict of movie index and similarity"""
        return self.qualified_movies_df.iloc[movie_indices], dict(list_tuples_of_idx_similarity)

    def _get_features_for_recommendation(self, recommendation_movies_indices_sim_scores):
        """create dict with main movie words"""
        main_movie_dict = list(map(lambda row: dict(zip(self.COUNT_VECTORIZER.get_feature_names(), row)),
                                   self.COUNT_VECTORIZER_MATRIX[self.movie_idx].toarray()))[0]

        """remove main movie"""
        recommendation_movies_indices_sim_scores.pop(self.movie_idx)
        """get only the movies indices"""
        list_of_rec_movies_indices = list(recommendation_movies_indices_sim_scores.keys())

        """create list of dicts with recommended movies words"""
        rec_movies_list_of_dicts = list(map(lambda row: dict(zip(self.COUNT_VECTORIZER.get_feature_names(), row)),
                                            self.COUNT_VECTORIZER_MATRIX[list_of_rec_movies_indices].toarray()))

        main_movie_dict = {k: int(v) for k, v in main_movie_dict.items() if v != 0}

        self.list_of_recommendation_features_dicts = [main_movie_dict]
        for rec_dict in rec_movies_list_of_dicts:
            rec_dict = {k: int(v) for k, v in rec_dict.items() if v != 0}
            res_rec_dict = dict()
            for word, count in main_movie_dict.items():
                if word in rec_dict.keys():
                    res_rec_dict[word] = int(rec_dict[word])
            self.list_of_recommendation_features_dicts.append(res_rec_dict)

    def _add_additional_data_to_df(self, recommendation_movies_indices_sim_scores, type='similarity'):
        if type == 'similarity':
            self.recommendations_df['similarity'] = 0
            for movie_idx, similarity in recommendation_movies_indices_sim_scores.items():
                self.recommendations_df.loc[
                    self.recommendations_df['movie_index'] == movie_idx, ['similarity']] = similarity

        elif type == 'rec_features':
            self.recommendations_df['rec_features'] = self.list_of_recommendation_features_dicts

    def _remove_useless_movie_indices(self, recommendation_movies_indices_sim_scores):
        list_of_remaining_movie_indices_from_df = list(self.recommendations_df['movie_index'])
        result_recommended_movie_indices_sim_scores = dict()
        for movie_idx_df in list_of_remaining_movie_indices_from_df:
            if movie_idx_df in recommendation_movies_indices_sim_scores.keys():
                result_recommended_movie_indices_sim_scores[movie_idx_df] = \
                    recommendation_movies_indices_sim_scores[movie_idx_df]

        return result_recommended_movie_indices_sim_scores

    def _optimize_recommendations_by_rating(self, top_n=10, min_movie_threshold=1):
        """create groupby qualified_movies_df"""
        grouped_df_by_score = self.recommendations_df.groupby('similarity')

        """the rec score for the best movie"""
        curr_best_recommendation_score = self.recommendations_df.loc[
            self.recommendations_df.index[1], 'similarity']

        """the result qualified_movies_df starts with the main movie, after that we append the others"""
        result_df = self.recommendations_df.loc[[self.recommendations_df.index[0]]]

        while True:
            try:
                curr_group = grouped_df_by_score.get_group(curr_best_recommendation_score)
                if len(curr_group) > min_movie_threshold:
                    curr_group = curr_group.sort_values('vote_average', ascending=False)

                result_df = result_df.append(curr_group)
                curr_best_recommendation_score -= 1
                if len(result_df) >= top_n + 1:
                    break
            except:
                curr_best_recommendation_score -= 1

        return result_df.head(top_n + 1)

    def get_recommendation_if_exists(self):
        movie_recommendation_obj = db.session.query(Recommendation, Movie).filter(
            Recommendation.main_movie_id == self.movie_id).filter(
            Movie.movie_id == Recommendation.recommended_movie_id).order_by(
            asc(Recommendation.position)).all()

        if movie_recommendation_obj:
            return movie_recommendation_obj
        else:
            return None

    def add_recommendation_to_db(self, df):
        df.reset_index(inplace=True)
        for index, row in df.iterrows():
            new_rec = Recommendation(main_movie_id=self.movie_id,
                                     recommended_movie_id=row['movie_id'], similarity=row['similarity'],
                                     features=json.dumps(row['rec_features']), position=index)
            db.session.add(new_rec)
        db.session.commit()

    def delete_recommendation_from_db_by_movie_id(self):
        db.session.query(Recommendation).filter(Recommendation.main_movie_id == self.movie_id).delete()
        db.session.commit()

    def get_recommendations(self, top_n=50):
        """get recommendations"""
        if self.movie_idx is not None:
            self.recommendations_df, recommendation_movies_indices_sim_scores = self._get_recommendations(top_n=top_n)

            """VERY IMPORTANT STEP is to reset the index and save the old index column in the qualified_movies_df
            as we will need it in the last step, features analysis"""
            self.recommendations_df = self.recommendations_df.reset_index()

            """add similarity column so we can do weighted rating in the next step"""
            self._add_additional_data_to_df(recommendation_movies_indices_sim_scores, type='similarity')

            """optimize recommendation based on weighted rating if they have the same count"""
            self.recommendations_df = self._optimize_recommendations_by_rating()

            """remove useless movie indices to reduce time for the next step"""
            recommendation_movies_indices_sim_scores = self._remove_useless_movie_indices(
                recommendation_movies_indices_sim_scores)

            """at the end when the dataframe is with 10 movies only,
            make the analysis by which features the movies were recommended"""
            self._get_features_for_recommendation(recommendation_movies_indices_sim_scores)

            """add the extracted features to the dataframe"""
            self._add_additional_data_to_df(recommendation_movies_indices_sim_scores, type='rec_features')

            """Replace all nan with None"""
            self.recommendations_df = self.recommendations_df.astype(object).where(pd.notnull(self.recommendations_df),
                                                                                   None)

            return self.recommendations_df
        else:
            return None
