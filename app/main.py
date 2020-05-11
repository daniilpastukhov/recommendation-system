from flask import Flask, render_template, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, \
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from bson.json_util import dumps
import pandas as pd
import numpy as np
from datetime import datetime
import os

GAMES_AMOUNT = 27075
DATA_FOLDER = os.path.join('..', 'data')


class GamesClient:
    def __init__(self, mongo_client, db, collection):
        self.games = mongo_client[db][collection]
        self.games.create_index([("name", "text")])

    def get_random_games(self, limit=6):
        return list(self.games.aggregate([{'$sample': {'size': limit}}]))

    def find_list_of_games(self, id_list):
        return [self.find_game_by_id(game_id) for game_id in id_list]

    def find_game_by_id(self, game_id):
        return self.games.find_one({'appid': game_id})

    def find_game(self, text):
        return self.games.find({'$text': {'$search': text}}).limit(18)

    @staticmethod
    def games_user_like(user, games):
        return [game for game in games if game['appid'] in user['likes']]

    @staticmethod
    def games_user_dislike(user, games):
        return [game for game in games if game['appid'] in user['dislikes']]


class UserClient:
    def __init__(self, mongo_client, db, collection):
        self.users = mongo_client[db][collection]

    def create_user(self, user):
        self.users.insert_one({'username': user.username, 'email': user.email, 'password': user.password,
                               'likes': [], 'dislikes': []})

    def find_user(self, user, auth_type='email'):
        if auth_type == 'username':
            return self.find_by_username(user.username)
        elif auth_type == 'email':
            return self.find_by_email(user.email)

    def find_by_username(self, username):
        user = self.users.find_one({'username': username})
        return user

    def find_by_email(self, email):
        user = self.users.find_one({'email': email})
        return user

    @staticmethod
    def check_password(password='', entered_password=''):
        return bcrypt.check_password_hash(password, entered_password)


class User:
    def __init__(self, username='', email='', password=''):
        self.username = username
        self.email = email
        self.password = password

    def __getitem__(self, key):
        if key == 'username':
            return self.username
        elif key == 'email':
            return self.email
        elif key == 'password':
            return self.password


class TokenBlacklistClient:
    def __init__(self, mongo_client, db, collection):
        self.tokens = mongo_client[db][collection]
        self.tokens.create_index('created_at', expireAfterSeconds=3600)

    def is_token_in_blacklist(self, token):
        return self.tokens.find_one({'token': token}) is not None

    def blacklist_token(self, token):
        self.tokens.insert_one({'created_at': datetime.now(), 'token': token})


def df_from_indices(df, indices):
    result_df = [df.iloc[i] for i in indices]

    return pd.DataFrame(result_df)


def make_dummies(df, column, dummy_column_vals, sep=';'):
    categories = set()
    [categories.add(i) for l in df[column].apply(lambda x: x.split(sep)).values for i in l]

    for category in list(categories):
        df[category.lower()] = df[column].str.contains(category).astype(np.uint8)

    dummy_column_vals[column] = list(categories)


def min_max_scaling(df, scaling_values, column):
    col_min = df[column].min()
    col_max = df[column].max()
    scaling_values[column] = (col_min, col_max)
    df[column] = (df[column] - col_min) / (col_max - col_min)


def l2_norm(a, b):
    return np.sum(np.sqrt((a - b) ** 2), axis=0)


def cosine(a, b):
    return (a @ b) / (np.sqrt(np.sum(a ** 2, axis=0)) * np.sqrt(np.sum(b ** 2, axis=0)))


def knn(vec, X, k=5, metric='l2_norm', weights=None):
    if weights is None:
        weights = [0.5, 0.5]
    dists = np.empty((X.shape[0],))
    for i, row in enumerate(X):
        if np.array_equal(row, vec):
            continue
        if metric == 'l2_norm':
            dists[i] = -l2_norm(vec, row)
        elif metric == 'cosine':
            dists[i] = cosine(vec, row)
        elif metric == 'combined':
            dists[i] = weights[0] * -l2_norm(vec, row) + weights[1] * cosine(vec, row)

    return dists.argsort()[-k:][::-1]


def process_user_preferences(df, user, indices, val=1):
    for i in indices:
        genres = set()
        categories = set()
        game = df.loc[df['appid'] == i].iloc[0]
        [genres.add(i) for i in game['genres'].split(';')]
        [categories.add(i) for i in game['categories'].split(';')]
        for genre in genres:
            user[genre] += val
        for category in categories:
            user[category] += val


def recommend(df, recommendation_df, user_preferences, k=5):
    res = (recommendation_df.values @ user_preferences.values.T).reshape(len(recommendation_df), )
    res_indices = res.argsort(axis=0)[-k:][::-1]
    return df_from_indices(df, res_indices)


def preprocess(df):
    df = df.fillna(np.mean)

    dummy_columns = ['categories', 'genres', 'owners']
    dummy_column_vals = {}

    for dummy in dummy_columns:
        make_dummies(df, dummy, dummy_column_vals)

    df['oc_windows'] = df['platforms'].str.contains('windows').astype(np.uint8)
    df['oc_linux'] = df['platforms'].str.contains('linux').astype(np.uint8)
    df['oc_mac'] = df['platforms'].str.contains('mac').astype(np.uint8)

    df['release_date'] = df['release_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df['release_date'] = (df['release_date'] - datetime(1970, 1, 1)).apply(lambda x: x.total_seconds())

    columns_to_scale = ['release_date', 'positive_ratings', 'negative_ratings',
                        'average_playtime', 'median_playtime', 'price']
    scaling_values = {}

    for col in columns_to_scale:
        min_max_scaling(df, scaling_values, col)

    return df, dummy_column_vals


def pipeline(df, user):
    global dummy_column_values
    user_preference = pd.DataFrame([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ], columns=dummy_column_values['genres'] + dummy_column_values['categories'])

    process_user_preferences(df, user_preference.iloc[0], user['likes'], val=1)
    process_user_preferences(df, user_preference.iloc[0], user['dislikes'], val=-1)
    genres_df = df[
        [col.lower() for col in list(dummy_column_values['genres']) + list(dummy_column_values['categories'])]]

    return recommend(df, genres_df, pd.DataFrame(user_preference), k=20)


app = Flask(__name__, template_folder=os.getenv('FLASK_TEMPLATE_FOLDER'),
                      static_folder=os.getenv('FLASK_STATIC_FOLDER'))
cors = CORS(app)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_SECRET_KEY'] = os.getenv('FLASK_JWT_SECRET_KEY')
app.config['JWT_HEADER_TYPE'] = ''
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

bcrypt = Bcrypt()
jwt = JWTManager(app)

client = MongoClient(os.environ.get('MONGODB_URI'))

user_client = UserClient(client, 'auth', 'user')
games_client = GamesClient(client, 'recommendation-system', 'games')
tokens_blacklist_client = TokenBlacklistClient(client, 'auth', 'tokens_blacklist')

games_df = pd.read_csv(os.path.join(DATA_FOLDER, 'steam_merged.csv'))
games_df, dummy_column_values = preprocess(games_df)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return tokens_blacklist_client.is_token_in_blacklist(jti)


@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    form = request.get_json()
    auth_type = form['type']
    user = User(form['username'], form['email'], form['password'])
    found_user = user_client.find_user(user, auth_type)

    if found_user is None:
        return {'message': 'User {} doesn\'t exist'.format(user.username)}, 500

    if user_client.check_password(found_user['password'], user.password):
        access_token = create_access_token(identity=user[auth_type])
        refresh_token = create_refresh_token(identity=user[auth_type])
        return {'message': 'Logged in as {}'.format(user[auth_type]),
                'access_token': access_token,
                'refresh_token': refresh_token}, 200
    else:
        return {'message': 'Wrong credentials'}, 500


@app.route('/api/logout', methods=['DELETE'])
@cross_origin()
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    tokens_blacklist_client.blacklist_token(jti)
    return jsonify({'message': 'Successfully logged out'}), 200


@app.route('/api/register', methods=['POST', 'GET'])
@cross_origin()
def register():
    form = request.get_json()
    auth_type = form['type']
    user = User(form['username'], form['email'], bcrypt.generate_password_hash(form['password']))
    found_user = user_client.find_user(user, auth_type)

    if found_user is not None:
        return {'message': 'User {} already exists'.format(user[auth_type])}, 500

    try:
        user_client.create_user(user)
        access_token = create_access_token(identity=user[auth_type])
        refresh_token = create_refresh_token(identity=user[auth_type])
        return {'message': 'Logged in as {}'.format(user[auth_type]),
                'access_token': access_token,
                'refresh_token': refresh_token}
    except:
        return {'message': 'Something went wrong'}, 500


@app.route('/api/user', methods=['GET'])
@cross_origin()
@jwt_required
def user_info():
    current_user = get_jwt_identity()
    return jsonify(user=current_user), 200


@app.route('/api/refresh', methods=['POST'])
@cross_origin()
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return {'access_token': access_token}, 200


@app.route('/api/games', methods=['POST'])
@cross_origin()
@jwt_required
def get_games():
    random_games = games_client.get_random_games(request.get_json()['limit'])
    current_user = get_jwt_identity()
    found_user = user_client.find_by_email(current_user)
    liked_games = games_client.games_user_like(found_user, random_games)
    disliked_games = games_client.games_user_dislike(found_user, random_games)
    for game in random_games:
        found = False
        for liked_game in liked_games:
            if game['id'] == liked_game['id']:
                random_games.remove(game)
                found = True
                break
        for disliked_game in disliked_games:
            if found:
                break
            if game['id'] == disliked_game['id']:
                random_games.remove(game)
                break
    return {'random_games': dumps(random_games),
            'liked_games': dumps(liked_games),
            'disliked_games': dumps(disliked_games)}, 200


@app.route('/api/games/like', methods=['POST'])
@cross_origin()
@jwt_required
def like():
    current_user = get_jwt_identity()
    game_id = request.get_json()['id']
    user_client.users.update_one({'email': current_user}, {'$addToSet': {'likes': game_id}})
    user_client.users.update_one({'email': current_user}, {'$pull': {'dislikes': game_id}})
    return {'message': 'Put the like successfully'}, 200


@app.route('/api/games/dislike', methods=['POST'])
@cross_origin()
@jwt_required
def dislike():
    current_user = get_jwt_identity()
    game_id = request.get_json()['id']
    user_client.users.update_one({'email': current_user}, {'$addToSet': {'dislikes': game_id}})
    user_client.users.update_one({'email': current_user}, {'$pull': {'likes': game_id}})
    return {'message': 'Put the dislike successfully'}, 200


@app.route('/api/games/delete', methods=['POST'])
@cross_origin()
@jwt_required
def delete():
    current_user = get_jwt_identity()
    game_id = request.get_json()['id']
    user_client.users.update_one({'email': current_user}, {'$pull': {'dislikes': game_id}})
    user_client.users.update_one({'email': current_user}, {'$pull': {'likes': game_id}})
    return {'message': 'Deleted the game successfully'}, 200


@app.route('/api/games/list', methods=['POST'])
@cross_origin()
@jwt_required
def games_list():
    games_type = request.get_json()['type']
    current_user = get_jwt_identity()
    found_user = user_client.find_by_email(current_user)
    if games_type == 'likes':
        return {'message': 'Retrieve was done successfully',
                'games': dumps(games_client.find_list_of_games(found_user['likes']))}, 200
    elif games_type == 'dislikes':
        return {'message': 'Retrieve was done successfully',
                'games': dumps(games_client.find_list_of_games(found_user['dislikes']))}, 200
    else:
        return {'message': 'Something went wrong...'}, 400


@app.route('/api/user/rated_games', methods=['POST'])
@cross_origin()
@jwt_required
def count():
    current_user = get_jwt_identity()
    found_user = user_client.find_by_email(current_user)
    return {'rated_games': len(found_user['likes'] + len(found_user['dislikes']))}, 200


@app.route('/api/games/recommendation', methods=['POST'])
@cross_origin()
@jwt_required
def recommendation():
    current_user = get_jwt_identity()
    found_user = user_client.find_by_email(current_user)
    recommended_games = pipeline(games_df, found_user)
    return {'message': 'Success', 'recommendation': recommended_games.to_json(orient='records')}, 200


@app.route('/api/games/search', methods=['POST'])
@cross_origin()
@jwt_required
def search():
    text = request.get_json()['text']
    current_user = get_jwt_identity()
    found_user = user_client.find_by_email(current_user)
    all_games = list(games_client.find_game(text))
    liked_games = games_client.games_user_like(found_user, all_games)
    disliked_games = games_client.games_user_dislike(found_user, all_games)
    for game in all_games:
        found = False
        for liked_game in liked_games:
            if game['id'] == liked_game['id']:
                all_games.remove(game)
                found = True
                break
        for disliked_game in disliked_games:
            if found:
                break
            if game['id'] == disliked_game['id']:
                all_games.remove(game)
                break

    return {'all_games': dumps(all_games),
            'liked_games': dumps(liked_games),
            'disliked_games': dumps(disliked_games)}, 200


# Start development web server
if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', 5000), debug=True)
