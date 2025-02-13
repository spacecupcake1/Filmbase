from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from functools import wraps
import mysql.connector
from mysql.connector import Error
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'movie_db'
}

def get_db_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

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

def create_tables():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create movies table
            create_movies_table_query = """
            CREATE TABLE IF NOT EXISTS movies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                director VARCHAR(255),
                release_year INT,
                genre VARCHAR(100),
                rating DECIMAL(3,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_movies_table_query)
            
            # Create users table
            create_users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                role ENUM('admin', 'client') NOT NULL DEFAULT 'client',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table_query)
            connection.commit()

            # Create default admin user
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, email, role)
                    VALUES ('admin', %s, 'admin@example.com', 'admin')
                """, (admin_password,))
                connection.commit()
                print("Admin user created successfully")
            except Error as e:
                if e.errno == 1062:  # Duplicate entry error
                    print("Admin user already exists")
                else:
                    print(f"Error creating admin user: {e}")

        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Create tables when the application starts
create_tables()

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
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
            
            cursor.execute(
                "SELECT id, username, role FROM users WHERE username = %s AND password = %s",
                (data['username'], hashed_password)
            )
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                return jsonify({
                    "message": "Login successful",
                    "role": user['role']
                })
            else:
                return jsonify({"error": "Invalid username or password"}), 401
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
            
            insert_query = """
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data['username'],
                data['email'],
                hashed_password,
                'client'  # Default role for new registrations
            ))
            connection.commit()
            return jsonify({"message": "Registration successful"})
        except Error as e:
            if e.errno == 1062:
                return jsonify({"error": "Username or email already exists"}), 400
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

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
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM movies ORDER BY created_at DESC")
            movies = cursor.fetchall()
            movie_list = []
            for movie in movies:
                movie_dict = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'director': movie['director'],
                    'release_year': movie['release_year'],
                    'genre': movie['genre'],
                    'rating': float(movie['rating']) if movie['rating'] else None,
                    'created_at': movie['created_at'].isoformat() if movie['created_at'] else None
                }
                movie_list.append(movie_dict)
            return jsonify({'movies': movie_list})
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/movies', methods=['POST'])
@role_required(['admin'])
def add_movie():
    data = request.json
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO movies (title, director, release_year, genre, rating)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data['title'],
                data['director'],
                data['releaseYear'],
                data['genre'],
                data['rating']
            ))
            connection.commit()
            return jsonify({"message": "Movie added successfully", "id": cursor.lastrowid})
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
@role_required(['admin'])
def update_movie(movie_id):
    data = request.json
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            update_query = """
            UPDATE movies 
            SET title = %s, director = %s, release_year = %s, genre = %s, rating = %s
            WHERE id = %s
            """
            cursor.execute(update_query, (
                data['title'],
                data['director'],
                data['releaseYear'],
                data['genre'],
                data['rating'],
                movie_id
            ))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Movie not found"}), 404
            return jsonify({"message": "Movie updated successfully"})
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_movie(movie_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Movie not found"}), 404
            return jsonify({"message": "Movie deleted successfully"})
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)