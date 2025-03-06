from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from functools import wraps
from pymongo import MongoClient
import hashlib
import secrets
import datetime
from bson import ObjectId

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# MongoDB configuration
MONGO_DB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'filmbase'
}

def get_mongo_connection():
    """Create a MongoDB connection"""
    client = MongoClient(MONGO_DB_CONFIG['host'], MONGO_DB_CONFIG['port'])
    db = client[MONGO_DB_CONFIG['database']]
    return db

# Login required decorator with role checking
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if 'role' not in session or session['role'] not in allowed_roles:
                return jsonify({"error": "Unauthorized"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Basic login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route handlers
@app.route('/login', methods=['GET'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.json
    db = get_mongo_connection()
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    user = db.users.find_one({"username": data['username'], "password": hashed_password})
    
    if user:
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            "message": "Login successful",
            "role": user['role']
        })
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    db = get_mongo_connection()
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    
    user = {
        "username": data['username'],
        "email": data['email'],
        "password": hashed_password,
        "role": "client",  # Default role for new registrations
        "created_at": datetime.datetime.utcnow()
    }
    
    try:
        db.users.insert_one(user)
        return jsonify({"message": "Registration successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/add_movie')
@role_required(['admin'])
def add_movie_page():
    return render_template('add_movie.html')

@app.route('/api/user-info')
@login_required
def get_user_info():
    return jsonify({
        'username': session.get('username'),
        'role': session.get('role')
    })

@app.route('/api/movies', methods=['GET'])
@login_required
def get_movies():
    db = get_mongo_connection()
    movies = db.movies.find().sort("created_at", -1)
    movie_list = []
    for movie in movies:
        movie_dict = {
            'id': str(movie['_id']),
            'title': movie['title'],
            'director': movie['director'],
            'release_year': movie['release_year'],
            'genre': movie['genre'],
            'rating': movie['rating'],
            'created_at': movie['created_at'] if isinstance(movie['created_at'], str) else movie['created_at'].isoformat()
        }
        movie_list.append(movie_dict)
    return jsonify({'movies': movie_list})

@app.route('/api/movies', methods=['POST'])
@role_required(['admin'])
def add_movie():
    data = request.json
    db = get_mongo_connection()
    movie = {
        "title": data['title'],
        "director": data['director'],
        "release_year": data['releaseYear'],
        "genre": data['genre'],
        "rating": data['rating'],
        "created_at": datetime.datetime.utcnow()
    }
    
    try:
        result = db.movies.insert_one(movie)
        return jsonify({"message": "Movie added successfully", "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies/<string:movie_id>', methods=['GET'])
@login_required
def get_movie(movie_id):
    db = get_mongo_connection()
    movie = db.movies.find_one({"_id": ObjectId(movie_id)})
    if movie:
        movie_dict = {
            'id': str(movie['_id']),
            'title': movie['title'],
            'director': movie['director'],
            'release_year': movie['release_year'],
            'genre': movie['genre'],
            'rating': movie['rating'],
            'created_at': movie['created_at'] if isinstance(movie['created_at'], str) else movie['created_at'].isoformat()
        }
        return jsonify(movie_dict)
    else:
        return jsonify({"error": "Movie not found"}), 404

@app.route('/api/movies/<string:movie_id>', methods=['PUT'])
@role_required(['admin'])
def update_movie(movie_id):
    data = request.get_json()
    update_fields = {
        "title": data.get('title'),
        "director": data.get('director'),
        "release_year": data.get('releaseYear', None),  # Provide a default value if 'releaseYear' is missing
        "genre": data.get('genre'),
        "rating": data.get('rating')
    }
    
    # Remove keys with None values
    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    db = get_mongo_connection()
    result = db.movies.update_one(
        {"_id": ObjectId(movie_id)},
        {"$set": update_fields}
    )

    if result.modified_count > 0:
        return jsonify({"message": "Movie updated successfully"}), 200
    else:
        return jsonify({"message": "No changes made to the movie"}), 400

@app.route('/api/movies/<string:movie_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_movie(movie_id):
    db = get_mongo_connection()
    
    try:
        result = db.movies.delete_one({"_id": ObjectId(movie_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Movie not found"}), 404
        return jsonify({"message": "Movie deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)