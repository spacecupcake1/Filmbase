from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
from decimal import Decimal
import datetime

# MySQL database configuration
MYSQL_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'movie_db'
}

# MongoDB configuration
MONGO_DB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'filmbase'
}

def convert_decimal_to_float(data):
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
        elif isinstance(value, datetime.datetime):
            data[key] = value.isoformat()
    return data

def migrate_users_and_movies():
    mysql_connection = None
    try:
        mysql_connection = mysql.connector.connect(**MYSQL_DB_CONFIG)
        if mysql_connection.is_connected():
            mysql_cursor = mysql_connection.cursor(dictionary=True)

            # Fetch users
            mysql_cursor.execute("SELECT * FROM users")
            users = mysql_cursor.fetchall()

            # Connect to MongoDB
            mongo_client = MongoClient(MONGO_DB_CONFIG['host'], MONGO_DB_CONFIG['port'])
            mongo_db = mongo_client[MONGO_DB_CONFIG['database']]

            # Migrate users to MongoDB
            for user in users:
                user_data = {
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'created_at': user['created_at']
                }
                user_data = convert_decimal_to_float(user_data)
                mongo_db.users.insert_one(user_data)

            # Fetch movies
            mysql_cursor.execute("SELECT * FROM movies")
            movies = mysql_cursor.fetchall()

            # Migrate movies to MongoDB
            for movie in movies:
                movie_data = {
                    'title': movie['title'],
                    'director': movie['director'],
                    'release_year': movie['release_year'],
                    'genre': movie['genre'],
                    'rating': movie['rating'],
                    'created_at': movie['created_at']
                }
                movie_data = convert_decimal_to_float(movie_data)
                mongo_db.movies.insert_one(movie_data)

            print("Migration completed successfully.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if mysql_connection and mysql_connection.is_connected():
            mysql_cursor.close()
            mysql_connection.close()

if __name__ == '__main__':
    migrate_users_and_movies()