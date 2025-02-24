from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error

# MySQL database configuration
MYSQL_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'movie_db'
}

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "movie_db"
MONGO_COLLECTION_NAME = "movies"

def get_mysql_connection():
    """Create a MySQL database connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def get_mongo_connection():
    """Create a MongoDB connection"""
    try:
        client = MongoClient(MONGO_URI)
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def migrate_data():
    mysql_conn = get_mysql_connection()
    mongo_client = get_mongo_connection()

    if mysql_conn and mongo_client:
        try:
            mysql_cursor = mysql_conn.cursor(dictionary=True)
            mysql_cursor.execute("SELECT * FROM movies")
            movies = mysql_cursor.fetchall()

            mongo_db = mongo_client[MONGO_DB_NAME]
            mongo_collection = mongo_db[MONGO_COLLECTION_NAME]

            for movie in movies:
                mongo_collection.insert_one(movie)

            print("Data migration completed successfully")
        except Error as e:
            print(f"Error during data migration: {e}")
        finally:
            if mysql_conn.is_connected():
                mysql_cursor.close()
                mysql_conn.close()
            mongo_client.close()

if __name__ == "__main__":
    migrate_data()