import pickle
import pandas as pd


class LoaderHandler:
    def __init__(self):
        with open('.\\serialized_objects\\user_based\\tf_vectorizer_matrix.pkl', 'rb') as f:
            self._TF_VECTORIZER_MATRIX = pickle.load(f)

        with open('.\\serialized_objects\\user_based\\tfidf_vectorizer_matrix.pkl', 'rb') as f:
            self._TFIDF_VECTORIZER_MATRIX = pickle.load(f)

        with open('.\\serialized_objects\\movie_based\\count_vectorizer_matrix.pkl', 'rb') as f:
            self._COUNT_VECTORIZER_MATRIX = pickle.load(f)

        with open('.\\serialized_objects\\movie_based\\count_vectorizer.pkl', 'rb') as f:
            self._COUNT_VECTORIZER = pickle.load(f)

        self._QUALIFIED_MOVIES_DF = pd.read_csv(
            '.\\data\\processed_movies\\qualified_all_metadata.csv')
        self._QUALIFIED_MOVIES_DF['movie_index'] = self._QUALIFIED_MOVIES_DF.index

        self._DICT_OF_MOVIE_ID_INDEX = dict(
            zip(list(self._QUALIFIED_MOVIES_DF['movie_id']), list(self._QUALIFIED_MOVIES_DF.index)))

    def get_tf_vectorizer_matrix(self):
        return self._TF_VECTORIZER_MATRIX

    def get_tfidf_vectorizer_matrix(self):
        return self._TFIDF_VECTORIZER_MATRIX

    def get_count_vectorizer_matrix(self):
        return self._COUNT_VECTORIZER_MATRIX

    def get_count_vectorizer(self):
        return self._COUNT_VECTORIZER

    def get_movie_df(self):
        return self._QUALIFIED_MOVIES_DF

    def get_dict_of_movie_id_index(self):
        return self._DICT_OF_MOVIE_ID_INDEX
