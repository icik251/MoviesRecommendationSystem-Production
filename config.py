class Config(object):
    SECRET_KEY = '213243adasd21323'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:pass@localhost/movies_system_prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RATING_SCALE = ['Not rated yet!', 1, 2, 3, 4, 5]
    TMDB_BASE_PATH_URL = "http://image.tmdb.org/t/p/w300"
    DEBUG = False