import pickle
import random
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
import pandas as pd

"""if you want to init class in .py file, change relative path to '..\\serialized_objects\\..'"""
with open('.\\serialized_objects\\user_based\\tf_vectorizer_matrix.pkl', 'rb') as f:
    TF_VECTORIZER_MATRIX = pickle.load(f)

with open('.\\serialized_objects\\user_based\\tfidf_vectorizer_matrix.pkl', 'rb') as f:
    TFIDF_VECTORIZER_MATRIX = pickle.load(f)

QUALIFIED_MOVIES_DF = pd.read_csv('.\\data\\processed_movies\\qualified_all_metadata.csv')


class RecommendationHandlerExternalUser:
    def __init__(self, external_users_ratings):
        """load everything needed"""
        self.TFIDF_VECTORIZER_MATRIX = TFIDF_VECTORIZER_MATRIX
        self.TF_VECTORIZER_MATRIX = TF_VECTORIZER_MATRIX
        """copy dataframe as we make changes to it"""
        self.df = QUALIFIED_MOVIES_DF.copy(deep=True)

        self.external_users_ratings = external_users_ratings
        self.dict_of_movie_id_test_set = dict()
        self.dict_of_movie_id_preference = dict()
        self.list_of_accuracies = []
        self.list_of_precisions = []

        self.user_profile = None
        self.profile_best_matches = None

    def _build_user_favourites_df(self, all_movies, list_of_qualified_movie_ids, list_of_test_movie_ids):

        for item in all_movies:
            if item.rating is not None and item.movie_id in list_of_qualified_movie_ids:
                if item.movie_id in list_of_test_movie_ids:
                    self.dict_of_movie_id_test_set[item.movie_id] = item.rating
                else:
                    if 0.5 <= item.rating <= 1:
                        self.dict_of_movie_id_preference[item.movie_id] = -2
                    elif 1.5 <= item.rating <= 2.5:
                        self.dict_of_movie_id_preference[item.movie_id] = -1
                    elif 3.5 <= item.rating <= 4:
                        self.dict_of_movie_id_preference[item.movie_id] = 1
                    elif item.rating >= 4.5:
                        self.dict_of_movie_id_preference[item.movie_id] = 2

    def _add_user_favourites_to_df(self):

        def populate_user_preference(movie_id):
            if movie_id in self.dict_of_movie_id_preference.keys():
                return self.dict_of_movie_id_preference[movie_id]
            else:
                return 0

        self.df['user_preferences'] = self.df['movie_id'].apply((
            lambda x: populate_user_preference(x)))

    def _create_user_profile(self):
        """make dot product between users preference list, example: [2,-1,0,0,1,0,-2,1,1] and TF matrix
        to create user profile vector with len == len(vocabulary)"""

        user_favourites_list = list(self.df['user_preferences'])
        """adding dimension on 'user_favourite_list' and transposing TF matrix"""
        self.user_profile = linear_kernel([user_favourites_list], self.TF_VECTORIZER_MATRIX.T)

    def _calculate_similarity_user_profile_tfidf(self):
        self.profile_best_matches = cosine_similarity(self.user_profile, self.TFIDF_VECTORIZER_MATRIX)[0]

    def _extract_only_test_movies(self, list_tuples_of_idx_similarity):
        list_of_test_set_idx = self.df.index[self.df['movie_id'].isin(self.dict_of_movie_id_test_set.keys())].tolist()
        list_tuples_of_idx_similarity = [x for x in list_tuples_of_idx_similarity if x[0] in list_of_test_set_idx]
        return list_tuples_of_idx_similarity

    def _calculate_accuracy_precision(self, list_of_chosen_movies, list_tuples_of_idx_similarity):
        sum_matches = 0
        """count good movies in test set"""
        count_good_movies = len([x for x in list_of_chosen_movies if x.rating >= 3.5])
        count_bad_movies = len([x for x in list_of_chosen_movies if x.rating <= 2.5])

        movies_matched = 0
        if count_good_movies > 0:
            for movie_idx, similarity in dict(list_tuples_of_idx_similarity).items():
                curr_movie_id = self.df.loc[movie_idx, 'movie_id']
                for movie_obj in list_of_chosen_movies:
                    if movie_obj.movie_id == curr_movie_id:
                        """if movie matches +=1, this is for the accuracy """
                        movies_matched += 1

                        if 0.5 <= movie_obj.rating <= 1:
                            sum_matches -= 2
                        elif 1.5 <= movie_obj.rating <= 2.5:
                            sum_matches -= 1
                        elif 3.5 <= movie_obj.rating <= 4:
                            sum_matches += 1
                        elif movie_obj.rating >= 4.5:
                            sum_matches += 2

            if movies_matched > 0:
                self.list_of_accuracies.append(sum_matches / (2 * movies_matched))
            self.list_of_precisions.append(sum_matches / (2 * (count_good_movies + count_bad_movies)))

    def evaluate_system(self):
        """Whole evaluation process"""

        """get all movies ratings for user"""
        all_movies = self.external_users_ratings
        list_of_qualified_movie_ids = self.df['movie_id'].values
        list_of_ratings = []
        """remove all movies that are not qualified in our system"""
        for movie_obj in all_movies:
            if movie_obj.movie_id not in list_of_qualified_movie_ids:
                all_movies.remove(movie_obj)
            else:
                list_of_ratings.append(movie_obj.rating)

        window_size = 10
        num_of_iterations = int(len(all_movies) / window_size)
        self.list_of_accuracies = []
        self.list_of_precisions = []
        for i in range(num_of_iterations):
            list_of_chosen_movies = []

            for j in range(window_size):
                while True:
                    random_movie_num = random.randint(0, len(all_movies) - 1)
                    if all_movies[random_movie_num] in list_of_chosen_movies:
                        continue
                    else:
                        list_of_chosen_movies.append(all_movies[random_movie_num])
                        break

            list_of_test_movie_ids = [x.movie_id for x in list_of_chosen_movies]

            self.df = QUALIFIED_MOVIES_DF.copy(deep=True)
            self._build_user_favourites_df(all_movies, list_of_qualified_movie_ids, list_of_test_movie_ids)
            self._add_user_favourites_to_df()
            self._create_user_profile()
            self._calculate_similarity_user_profile_tfidf()

            list_tuples_of_idx_similarity = list(enumerate(self.profile_best_matches))
            list_tuples_of_idx_similarity = sorted(list_tuples_of_idx_similarity, key=lambda x: x[1], reverse=True)
            """get only the top n movies, and their indices"""
            list_tuples_of_idx_similarity = list_tuples_of_idx_similarity[:window_size]

            """method for calculating accuracy and precision"""
            self._calculate_accuracy_precision(list_of_chosen_movies=list_of_chosen_movies,
                                               list_tuples_of_idx_similarity=list_tuples_of_idx_similarity)

        """if a list is empty return Nones"""
        if len(self.list_of_accuracies) == 0 or len(self.list_of_precisions) == 0:
            return None, None

        """return average accuracy and precision for all windows of user"""
        return sum(self.list_of_accuracies) / len(self.list_of_accuracies), \
               sum(self.list_of_precisions) / len(self.list_of_precisions)
