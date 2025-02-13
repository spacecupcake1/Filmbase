from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

# Create the movies table if it doesn't exist
def create_table():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
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
            cursor.execute(create_table_query)
            connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Create the table when the application starts
create_table()

# Route to serve the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get all movies
@app.route('/api/movies', methods=['GET'])
def get_movies():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM movies ORDER BY created_at DESC")
            movies = cursor.fetchall()
            return jsonify(movies)
        except Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"error": "Database connection failed"}), 500

# API endpoint to add a new movie
@app.route('/api/movies', methods=['POST'])
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

# API endpoint to update a movie
@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
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

# API endpoint to delete a movie
@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
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