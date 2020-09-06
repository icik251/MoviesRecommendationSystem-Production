import functools
from ast import literal_eval
import pandas as pd
import sqlalchemy as db

"""VARIABLES"""
"""create db engine so we can populate db"""
DB_ENGINE = db.create_engine('mysql+pymysql://root:pass@localhost/movies_system_prod')

"""Change dir to where data is"""
PATH_TO_DATA = 'D:\\Desktop\\Diplome_work\\Data\\Movies_big_dataset_original\\'


def process_movies_metadata(df):
    columns_to_preprocess = ['genres', 'production_companies', 'production_countries', 'spoken_languages',
                             'belongs_to_collection', 'adult', 'backdrop_path', 'video']
    df_without_preprocess = df[df.columns.difference(columns_to_preprocess)]

    """make release_date into datetime format"""
    df_without_preprocess['release_date'] = pd.to_datetime(df_without_preprocess['release_date'], errors='coerce')
    """change type of columns"""
    df_without_preprocess[["movie_id", "budget", "popularity"]] = \
        df_without_preprocess[["movie_id", "budget", "popularity"]].apply(pd.to_numeric, errors='coerce')
    df_without_preprocess.dropna(subset=['movie_id'], inplace=True)

    df_without_preprocess.to_sql('movies', DB_ENGINE, if_exists='append', index=False)


def process_belongs_to_collection(df):
    list_movies_ids = list(df['movie_id'].values)
    """convert string to dict"""
    list_belongs_to_collection = list(
        map(functools.partial(convert_str_to_dict, mode='collections'), list(df['belongs_to_collection'].values),
            list_movies_ids))

    df_collections = pd.DataFrame(list_belongs_to_collection, columns=['id', 'name'])

    """rename column cuz of db"""
    df_collections.rename(columns={'id': 'collection_id'},
                          inplace=True)

    df_collections.dropna(inplace=True)
    df_collections.drop_duplicates(subset=['collection_id'], keep='first', inplace=True)
    df_collections.to_sql('collections', DB_ENGINE, if_exists='append', index=False)

    """process collections to movies"""
    list_of_collections_to_movies_dicts = []
    for item in list_belongs_to_collection:
        del item['name'], item['poster_path'], item['backdrop_path']
        list_of_collections_to_movies_dicts.append(item)

    df_collections_to_movies = pd.DataFrame(list_of_collections_to_movies_dicts)
    """rename column cuz of db"""
    df_collections_to_movies.rename(columns={'id': 'collection_id'},
                                    inplace=True)
    df_collections_to_movies.dropna(inplace=True)
    df_collections_to_movies.drop_duplicates(['collection_id', 'movie_id'], keep='first', inplace=True)

    df_collections_to_movies.to_sql('collections_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_genres(df):
    list_movies_ids = list(df['movie_id'].values)
    list_genres = list(
        map(functools.partial(convert_str_to_dict, mode='genres'),
            list(df['genres'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_genres for item in sublist]

    df_genres = pd.DataFrame(flat_list_of_dicts)

    """rename column cuz of db"""
    df_genres.rename(columns={'id': 'genre_id'},
                     inplace=True)

    df_genres.drop_duplicates(subset=['genre_id'], keep='first', inplace=True)
    df_genres.drop(['movie_id'], axis=1, inplace=True)
    df_genres.to_sql('genres', DB_ENGINE, if_exists='append', index=False)

    """process genres to movies"""
    list_of_genres_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name']
        list_of_genres_to_movies_dicts.append(item)

    df_genres_to_movies = pd.DataFrame(list_of_genres_to_movies_dicts)
    """rename column cuz of db"""
    df_genres_to_movies.rename(columns={'id': 'genre_id'},
                               inplace=True)
    df_genres_to_movies.drop_duplicates(['genre_id', 'movie_id'], keep='first', inplace=True)

    df_genres_to_movies.to_sql('genres_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_production_companies(df):
    list_movies_ids = list(df['movie_id'].values)
    list_prod_companies = list(
        map(functools.partial(convert_str_to_dict, mode='production_companies'),
            list(df['production_companies'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_prod_companies for item in sublist]

    df_prod_companies = pd.DataFrame(flat_list_of_dicts)

    """rename column cuz of db"""
    df_prod_companies.rename(columns={'id': 'production_company_id'},
                             inplace=True)

    df_prod_companies.drop_duplicates(subset=['production_company_id'], keep='first', inplace=True)
    df_prod_companies.drop(['movie_id'], axis=1, inplace=True)
    df_prod_companies.to_sql('production_companies', DB_ENGINE, if_exists='append', index=False)

    """process production_companies to movies"""
    list_of_prod_companies_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name']
        list_of_prod_companies_to_movies_dicts.append(item)

    df_prod_companies_to_movies = pd.DataFrame(list_of_prod_companies_to_movies_dicts)
    """rename column cuz of db"""
    df_prod_companies_to_movies.rename(columns={'id': 'production_company_id'},
                                       inplace=True)
    df_prod_companies_to_movies.drop_duplicates(['production_company_id', 'movie_id'], keep='first', inplace=True)

    df_prod_companies_to_movies.to_sql('production_companies_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_production_countries(df):
    list_movies_ids = list(df['movie_id'].values)
    list_prod_countries = list(
        map(functools.partial(convert_str_to_dict, mode='production_countries'),
            list(df['production_countries'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_prod_countries for item in sublist]

    df_prod_countries = pd.DataFrame(flat_list_of_dicts)

    """rename column cuz of db"""
    df_prod_countries.rename(columns={'iso_3166_1': 'code'},
                             inplace=True)

    df_prod_countries.drop_duplicates(subset=['code'], keep='first', inplace=True)
    df_prod_countries.drop(['movie_id'], axis=1, inplace=True)
    df_prod_countries.to_sql('production_countries', DB_ENGINE, if_exists='append', index=False)

    """process production_countries to movies"""
    list_of_prod_countries_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name']
        list_of_prod_countries_to_movies_dicts.append(item)

    df_prod_countries_to_movies = pd.DataFrame(list_of_prod_countries_to_movies_dicts)
    """rename column cuz of db"""
    df_prod_countries_to_movies.rename(columns={'iso_3166_1': 'code'},
                                       inplace=True)
    df_prod_countries_to_movies.drop_duplicates(['code', 'movie_id'], keep='first', inplace=True)

    df_prod_countries_to_movies.to_sql('production_countries_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_spoken_languages(df):
    list_movies_ids = list(df['movie_id'].values)
    list_spoken_languages = list(
        map(functools.partial(convert_str_to_dict, mode='spoken_languages'),
            list(df['spoken_languages'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_spoken_languages for item in sublist]

    df_spoken_languages = pd.DataFrame(flat_list_of_dicts)

    """rename column cuz of db"""
    df_spoken_languages.rename(columns={'iso_639_1': 'code'},
                               inplace=True)

    df_spoken_languages.drop_duplicates(subset=['code'], keep='first', inplace=True)
    df_spoken_languages.drop(['movie_id'], axis=1, inplace=True)
    df_spoken_languages.to_sql('spoken_languages', DB_ENGINE, if_exists='append', index=False)

    """process spoken_languages to movies"""
    list_of_spoken_languages_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name']
        list_of_spoken_languages_to_movies_dicts.append(item)

    df_spoken_languages_to_movies = pd.DataFrame(list_of_spoken_languages_to_movies_dicts)
    """rename column cuz of db"""
    df_spoken_languages_to_movies.rename(columns={'iso_639_1': 'code'},
                                         inplace=True)
    df_spoken_languages_to_movies.drop_duplicates(['code', 'movie_id'], keep='first', inplace=True)

    df_spoken_languages_to_movies.to_sql('spoken_languages_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_keywords(df):
    list_movies_ids = list(df['movie_id'].values)
    list_spoken_langs = list(
        map(functools.partial(convert_str_to_dict, mode='keywords'),
            list(df['keywords'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_spoken_langs for item in sublist]

    df_keywords = pd.DataFrame(flat_list_of_dicts)

    """rename column cuz of db"""
    df_keywords.rename(columns={'id': 'keyword_id'},
                       inplace=True)

    df_keywords.drop_duplicates(subset=['keyword_id'], keep='first', inplace=True)
    df_keywords.drop(['movie_id'], axis=1, inplace=True)
    df_keywords.to_sql('keywords', DB_ENGINE, if_exists='append', index=False)

    """process keywords to movies"""
    list_of_keywords_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name']
        list_of_keywords_to_movies_dicts.append(item)

    df_keywords_to_movies = pd.DataFrame(list_of_keywords_to_movies_dicts)
    """rename column cuz of db"""
    df_keywords_to_movies.rename(columns={'id': 'keyword_id'},
                                 inplace=True)
    df_keywords_to_movies.drop_duplicates(['keyword_id', 'movie_id'], keep='first', inplace=True)

    df_keywords_to_movies.to_sql('keywords_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_casts(df):
    list_movies_ids = list(df['id'].values)
    list_casts = list(
        map(functools.partial(convert_str_to_dict, mode='cast'),
            list(df['cast'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_casts for item in sublist]
    """process casts table"""
    df_casts = pd.DataFrame(flat_list_of_dicts)
    df_casts.drop_duplicates(['id'], keep='first', inplace=True)
    df_casts.drop(df_casts.columns.difference(['id', 'name', 'gender']), axis=1, inplace=True)

    df_casts.to_sql('actors', DB_ENGINE, if_exists='append', index=False)

    """process casts to movies"""
    list_of_casts_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name'], item['gender'], item['profile_path']
        list_of_casts_to_movies_dicts.append(item)

    df_casts_to_movies = pd.DataFrame(list_of_casts_to_movies_dicts)
    """rename column cuz of db"""
    df_casts_to_movies.rename(columns={'id': 'actor_id'},
                              inplace=True)
    df_casts_to_movies.drop_duplicates(['actor_id', 'movie_id', 'cast_id'], keep='first', inplace=True)

    df_casts_to_movies.to_sql('actors_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_crews(df):
    list_movies_ids = list(df['id'].values)
    list_crews = list(
        map(functools.partial(convert_str_to_dict, mode='crew'),
            list(df['crew'].values), list_movies_ids))

    flat_list_of_dicts = [item for sublist in list_crews for item in sublist]
    """process casts table"""
    df_crews = pd.DataFrame(flat_list_of_dicts)
    df_crews.drop_duplicates(['id'], keep='first', inplace=True)
    df_crews.drop(df_crews.columns.difference(['id', 'name', 'gender']), axis=1, inplace=True)

    df_crews.to_sql('crews', DB_ENGINE, if_exists='append', index=False)

    """process crews to movies"""
    list_of_crews_to_movies_dicts = []
    for item in flat_list_of_dicts:
        del item['name'], item['gender'], item['profile_path']
        list_of_crews_to_movies_dicts.append(item)

    df_crews_to_movies = pd.DataFrame(list_of_crews_to_movies_dicts)
    """rename column cuz of db"""
    df_crews_to_movies.rename(columns={'id': 'crew_id'},
                              inplace=True)
    df_crews_to_movies.drop_duplicates(['crew_id', 'movie_id', 'job'], keep='first', inplace=True)

    df_crews_to_movies.to_sql('crews_to_movies', DB_ENGINE, if_exists='append', index=False)


def process_ratings(df):
    """split into multiple dataframes"""
    df.rename(columns={'userId': 'user_id',
                       'movieId': 'reference_movie_id',
                       'timestamp': 'datetime'},
              inplace=True)

    df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
    df.drop_duplicates(['user_id', 'reference_movie_id'], keep='first', inplace=True)
    chunk_size = int(len(df) / 4)
    print(chunk_size)
    df.to_sql('user_ratings_external', DB_ENGINE, if_exists='append', index=False, chunksize=chunk_size)


def process_reference_table(df):
    df.rename(columns={'movieId': 'reference_movie_id',
                       'imdbId': 'imdb_id',
                       'tmdbId': 'movie_id'},
              inplace=True)

    df.dropna(inplace=True)
    df.drop_duplicates(['movie_id'], keep='first', inplace=True)
    df.drop_duplicates(['movie_id', 'reference_movie_id'], keep='first', inplace=True)

    df.to_sql('reference_movie_ids', DB_ENGINE, if_exists='append', index=False)


def convert_str_to_dict(str_obj, movie_id, mode):
    movie_id = convert_movie_id_int(movie_id)
    if mode is 'collections':
        if not isinstance(str_obj, str) or not isinstance(movie_id, int):
            return {'id': None, 'name': None, 'poster_path': None, 'backdrop_path': None}
        try:
            """if there is some inconsistency in the data we will catch it"""
            converted_to_dict = literal_eval(str_obj)
            converted_to_dict['movie_id'] = movie_id
        except Exception as e:
            print(e)
            converted_to_dict = {'id': None, 'name': None, 'poster_path': None, 'backdrop_path': None}
        return converted_to_dict

    elif mode is 'cast' or mode is 'crew' or mode is 'genres' or mode is 'production_companies' or \
            mode is 'production_countries' or mode is 'spoken_languages' or mode is 'keywords':
        if not isinstance(str_obj, str) or not isinstance(movie_id, int):
            return []
        list_of_dicts = []
        try:
            """if there is some inconsistency in the data we will catch it"""
            converted_to_list = literal_eval(str_obj)
            for item in converted_to_list:
                item['movie_id'] = movie_id
                list_of_dicts.append(item)
        except Exception as e:
            print(e)
            return list_of_dicts

        return list_of_dicts


def convert_movie_id_int(movie_id):
    try:
        movie_id = int(movie_id)
        return movie_id
    except:
        print(movie_id)
        return None


"""Here we call each function that we need to populate the database"""


def populate_logic():
    """movies_metadata adding"""
    df_all_data = pd.read_csv(PATH_TO_DATA + 'movies_metadata.csv', low_memory=False)
    """rename id by movie_id which is going to be our identifier for a movie,
    then drop duplicates by the identifier"""
    df_all_data.rename(columns={'id': 'movie_id'}, inplace=True)
    df_all_data.drop_duplicates(subset="movie_id", inplace=True)

    """movies table adding"""
    process_movies_metadata(df=df_all_data)

    process_belongs_to_collection(df=df_all_data)
    process_genres(df=df_all_data)
    process_production_companies(df=df_all_data)
    process_production_countries(df=df_all_data)
    process_spoken_languages(df=df_all_data)

    """keywords adding"""
    df_keywords = pd.read_csv(PATH_TO_DATA + 'keywords.csv', low_memory=False)
    df_keywords.rename(columns={'id': 'movie_id'}, inplace=True)
    process_keywords(df=df_keywords)

    """credits adding"""
    df_credits = pd.read_csv(PATH_TO_DATA + 'credits.csv', low_memory=False)

    process_casts(df=df_credits)
    process_crews(df=df_credits)

    "user ratings import"""
    all_ratings = pd.read_csv(PATH_TO_DATA + 'ratings.csv', low_memory=False)
    process_ratings(df=all_ratings)

    """process reference table"""
    all_links = pd.read_csv(PATH_TO_DATA + 'links.csv', low_memory=False)
    process_reference_table(df=all_links)


if __name__ == "__main__":
    populate_logic()
