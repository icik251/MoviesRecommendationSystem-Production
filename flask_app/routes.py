import json
from datetime import datetime
from flask_login import current_user, login_user, logout_user
from flask import render_template, flash, redirect, url_for, request
from flask_app import app, db
from flask_app.forms import SearchForm, LoginForm, RegistrationForm
from flask_app.models import User, Movie, UsersToMovies, GenresToMovie, Genre
from flask_app.services.recommendation_handler_profile import RecommendationHandlerProfile
from flask_app.services.recommendations_handler import RecommendationsHandler

from flask_app.services.search_handler import SearchHandler
from flask_app.services.user_library_handler import UserLibraryHandler


@app.route('/search', methods=['GET', 'POST'])
def search():
    if current_user.is_authenticated:
        form = SearchForm()

        if form.validate_on_submit():
            start_time = datetime.now()
            searched_tokens = form.search_field.data.lower()

            """extract search results"""
            search_handler = SearchHandler(searched_token=searched_tokens)
            list_of_qualified_movies_obj = search_handler.extract_qualified_movies()

            current_user_id = current_user.id
            user_library_handler = UserLibraryHandler(user_id=current_user_id)

            """get dict of movie_id(int) : in library(bool)"""
            dict_of_movie_id_in_library = user_library_handler.get_dict_of_movie_id_in_library(
                list_of_movies_obj=list_of_qualified_movies_obj)

            "process for checked boxes and unchecked movies"
            if request.form.get('apply_changes'):
                list_of_checked = request.form.getlist('add_to_library')
                list_of_checked = list(map(int, list_of_checked))
                user_library_handler.update_user_library(list_of_checked_boxes=list_of_checked)

            end_time = datetime.now()
            return render_template('search.html', title='Search results', form=form,
                                   results=list_of_qualified_movies_obj, time_taken=end_time - start_time,
                                   dict_movies_lib=dict_of_movie_id_in_library,
                                   tmdb_base_url=app.config['TMDB_BASE_PATH_URL'])

        return render_template('search.html', title='Search movies', form=form)

    return redirect(url_for('login'))


@app.route('/library', methods=['GET', 'POST'])
def library():
    if current_user.is_authenticated:
        current_user_id = current_user.id

        user_library_handler = UserLibraryHandler(user_id=current_user_id)

        if request.method == 'GET':
            """get list of tuples (movie_obj, user_rating_for the movie)"""
            all_lib_movies_ratings = user_library_handler.get_all_library_movies_and_ratings()
            return render_template('library.html', title='Library', results=all_lib_movies_ratings,
                                   rating_scale=app.config['RATING_SCALE'],
                                   tmdb_base_url=app.config['TMDB_BASE_PATH_URL'])

        else:
            if request.form.get('apply_changes'):
                """update user ratings"""
                list_of_ratings = request.form.getlist('ratings')
                user_library_handler.update_user_ratings(list_of_ratings=list_of_ratings)

                """remove movies from favourites"""
                are_changes_made = False
                list_of_checked = request.form.getlist('remove_from_library')
                list_of_checked = list(map(int, list_of_checked))

                for checked_movie_id in list_of_checked:
                    are_changes_made = True
                    user_library_handler.remove_movie_from_library(checked_movie_id)

                if are_changes_made:
                    flash("Selected movies removed successfully!")
                    db.session.commit()

                return redirect(url_for('library'))

            if request.form.get('get_recommendations'):
                """get movie id for which the user wants recommendations"""
                movie_id = request.form.get("get_recommendations")
                start_time = datetime.now()
                return redirect(url_for('recommendations', movie_id=movie_id, start_time=start_time))

    return redirect(url_for('login'))


@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if current_user.is_authenticated:
        current_user_id = current_user.id
        movie_id = request.values.get('movie_id')
        start_time = request.values.get('start_time', str(datetime.now()))
        """convert to datetime if needed"""
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")

        recommendations_handler = RecommendationsHandler(movie_id=movie_id, user_id=current_user_id)

        """check if we have recommendations for this movie"""
        recommendations_from_db = recommendations_handler.get_recommendation_if_exists()
        if recommendations_from_db:
            list_of_recommendations, list_of_movies = zip(*recommendations_from_db)
            """cast to list as right now they are tuples"""
            list_of_recommendations = list(list_of_recommendations)
            list_of_movies = list(list_of_movies)

            """get genres for all movies"""
            list_of_genres = []
            for movie_obj in list_of_movies:
                list_of_genres.append(', '.join([res for (res,) in db.session.query(Genre.name).filter
                (GenresToMovie.movie_id == movie_obj.movie_id).filter(Genre.genre_id == GenresToMovie.genre_id).all()]))

            """get main movie and mark tokens which are in the recommended ones,
            so we can see which tokens matter and which doesn't, after that we pop the main
             movie from the two lists"""
            main_movie_idx = None
            set_of_saved_tokens = set()
            for idx, item in enumerate(list_of_recommendations):
                if item.main_movie_id == item.recommended_movie_id:
                    main_movie_idx = idx
                else:
                    recommended_movie_features = json.loads(item.features).keys()
                    for feature in recommended_movie_features:
                        set_of_saved_tokens.add(feature)

            user_library_handler = UserLibraryHandler(user_id=current_user_id)
            """get dict of movie_id(int) : in library(bool)"""
            dict_of_movie_id_in_library = user_library_handler.get_dict_of_movie_id_in_library(
                list_of_movies_obj=list_of_movies)

            """pop the main movie and mark which tokens are used to recommend from the 10 movies"""
            main_movie_genres = list_of_genres.pop(0)
            main_movie_rec_obj = list_of_recommendations.pop(main_movie_idx)
            main_movie_movie_obj = list_of_movies.pop(main_movie_idx)
            dict_main_movie_features = json.loads(main_movie_rec_obj.features)
            for key_feature, value_count in dict_main_movie_features.items():
                if key_feature in set_of_saved_tokens:
                    dict_main_movie_features[key_feature] = (value_count, True)
                else:
                    dict_main_movie_features[key_feature] = (value_count, False)

            "process for checked boxes and unchecked movies"
            if request.form.get('apply_changes'):
                list_of_checked = request.form.getlist('add_to_library')
                list_of_checked = list(map(int, list_of_checked))
                user_library_handler.update_user_library(list_of_checked_boxes=list_of_checked)

            list_of_movies_obj_genres = list(zip(list_of_movies, list_of_genres))

            end_time = datetime.now()
            return render_template('recommendations.html', title='Recommendations',
                                   rec_objects=list_of_recommendations, list_of_movies_obj_genres=list_of_movies_obj_genres,
                                   time_taken=end_time - start_time, main_movie_rec_obj=main_movie_rec_obj,
                                   dict_main_movie_features=dict_main_movie_features,
                                   main_movie_movie_obj=main_movie_movie_obj,
                                   main_movie_genres=main_movie_genres,
                                   dict_movies_lib=dict_of_movie_id_in_library,
                                   tmdb_base_url=app.config['TMDB_BASE_PATH_URL'])

        else:
            """else we create them and save them for future use"""
            recommendation_df = recommendations_handler.get_recommendations()

            if recommendation_df is not None:
                """save the whole qualified_movies_df including the main movie"""
                recommendations_handler.add_recommendation_to_db(recommendation_df)
                return redirect(url_for('recommendations', movie_id=movie_id, start_time=start_time))

            return render_template('recommendations.html')

    return redirect(url_for('login'))


@app.route('/recommendations_user_profile/<string:id>/<int:page_num>/'
           '', methods=['GET', 'POST'])
def recommendations_user_profile(id, page_num=1):
    if current_user.is_authenticated:
        current_user_id = current_user.id
        start_time = datetime.now()

        if page_num < 1:
            page_num = 1
        elif page_num > 10:
            page_num = 10

        """check if user has interacted with enough movies so we can recommend"""
        all_library_movies = db.session.query(UsersToMovies).filter(
            UsersToMovies.user_id == current_user_id).all()

        count_positive_rated_movies = 0
        for movie in all_library_movies:
            if movie.rating is not None and movie.rating > 3:
                count_positive_rated_movies += 1

        if count_positive_rated_movies < 5:
            return render_template('recommendations_user_profile.html')

        else:
            recommendation_handler_profile = RecommendationHandlerProfile(user_id=current_user_id)
            result_df = recommendation_handler_profile.get_recommendations(page_num=page_num, request_id=id)

            """get movies objects from db"""
            list_of_movies_obj = []
            list_of_genres = []
            for movie_id in result_df['movie_id']:
                list_of_movies_obj.append(db.session.query(Movie).filter(Movie.movie_id == movie_id).first())
                list_of_genres.append(', '.join([res for (res,) in db.session.query(Genre.name).filter
                (GenresToMovie.movie_id == movie_id).filter(Genre.genre_id == GenresToMovie.genre_id).all()]))

            user_library_handler = UserLibraryHandler(user_id=current_user_id)
            """get dict of movie_id(int) : in library(bool)"""
            dict_of_movie_id_in_library = user_library_handler.get_dict_of_movie_id_in_library(
                list_of_movies_obj=list_of_movies_obj)

            "process for checked boxes and unchecked movies"
            if request.form.get('apply_changes'):
                list_of_checked = request.form.getlist('add_to_library')
                list_of_checked = list(map(int, list_of_checked))
                user_library_handler.update_user_library(list_of_checked_boxes=list_of_checked)

            """merge the two lists"""
            list_of_movies_obj_genres = list(zip(list_of_movies_obj, list_of_genres))

            end_time = datetime.now()
            return render_template('recommendations_user_profile.html', title='Recommendations tailored for you!',
                                   list_of_movies_obj_genres=list_of_movies_obj_genres,
                                   list_of_similarities=list(result_df['similarity'].values),
                                   time_taken=end_time - start_time,
                                   dict_movies_lib=dict_of_movie_id_in_library, page_num=page_num, id=id,
                                   tmdb_base_url=app.config['TMDB_BASE_PATH_URL'])

    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('search'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
