import mysql.connector
from mysql.connector import Error
from datetime import datetime

class MovieManager:
    def __init__(self, host, user, password, database):
        """Initialize database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor()
            self.create_table()
        except Error as e:
            print(f"Error connecting to MySQL Database: {e}")

    def create_table(self):
        """Create movies table if it doesn't exist"""
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
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def add_movie(self, title, director, release_year, genre, rating):
        """Add a new movie to the database"""
        insert_query = """
        INSERT INTO movies (title, director, release_year, genre, rating)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(insert_query, (title, director, release_year, genre, rating))
            self.connection.commit()
            print("Movie added successfully!")
        except Error as e:
            print(f"Error adding movie: {e}")

    def view_all_movies(self):
        """View all movies in the database"""
        select_query = "SELECT * FROM movies"
        try:
            self.cursor.execute(select_query)
            movies = self.cursor.fetchall()
            if not movies:
                print("No movies found in the database.")
                return
            
            print("\nMovie List:")
            print("-" * 100)
            print(f"{'ID':<5} {'Title':<30} {'Director':<20} {'Year':<6} {'Genre':<15} {'Rating':<7}")
            print("-" * 100)
            
            for movie in movies:
                print(f"{movie[0]:<5} {movie[1]:<30} {movie[2]:<20} {movie[3]:<6} {movie[4]:<15} {movie[5]:<7}")
        except Error as e:
            print(f"Error viewing movies: {e}")

    def edit_movie(self, movie_id, title=None, director=None, release_year=None, genre=None, rating=None):
        """Edit an existing movie's information"""
        try:
            # First check if movie exists
            self.cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
            if not self.cursor.fetchone():
                print(f"No movie found with ID {movie_id}")
                return

            # Build update query based on provided fields
            update_parts = []
            values = []
            if title:
                update_parts.append("title = %s")
                values.append(title)
            if director:
                update_parts.append("director = %s")
                values.append(director)
            if release_year:
                update_parts.append("release_year = %s")
                values.append(release_year)
            if genre:
                update_parts.append("genre = %s")
                values.append(genre)
            if rating:
                update_parts.append("rating = %s")
                values.append(rating)

            if not update_parts:
                print("No fields provided for update")
                return

            values.append(movie_id)
            update_query = f"UPDATE movies SET {', '.join(update_parts)} WHERE id = %s"
            
            self.cursor.execute(update_query, tuple(values))
            self.connection.commit()
            print("Movie updated successfully!")
        except Error as e:
            print(f"Error updating movie: {e}")

    def delete_movie(self, movie_id):
        """Delete a movie from the database"""
        try:
            # First check if movie exists
            self.cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
            if not self.cursor.fetchone():
                print(f"No movie found with ID {movie_id}")
                return

            delete_query = "DELETE FROM movies WHERE id = %s"
            self.cursor.execute(delete_query, (movie_id,))
            self.connection.commit()
            print("Movie deleted successfully!")
        except Error as e:
            print(f"Error deleting movie: {e}")

    def close_connection(self):
        """Close the database connection"""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed.")

def main():
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'movie_db'
    }

    # Initialize MovieManager
    movie_manager = MovieManager(**DB_CONFIG)

    while True:
        print("\nMovie Management System")
        print("1. Add new movie")
        print("2. View all movies")
        print("3. Edit movie")
        print("4. Delete movie")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            title = input("Enter movie title: ")
            director = input("Enter director name: ")
            release_year = int(input("Enter release year: "))
            genre = input("Enter genre: ")
            rating = float(input("Enter rating (0-10): "))
            movie_manager.add_movie(title, director, release_year, genre, rating)

        elif choice == '2':
            movie_manager.view_all_movies()

        elif choice == '3':
            movie_id = int(input("Enter movie ID to edit: "))
            print("\nEnter new values (press Enter to skip):")
            title = input("New title: ") or None
            director = input("New director: ") or None
            release_year = int(input("New release year: ")) if input("New release year: ") else None
            genre = input("New genre: ") or None
            rating = float(input("New rating: ")) if input("New rating: ") else None
            movie_manager.edit_movie(movie_id, title, director, release_year, genre, rating)

        elif choice == '4':
            movie_id = int(input("Enter movie ID to delete: "))
            confirm = input("Are you sure you want to delete this movie? (y/n): ")
            if confirm.lower() == 'y':
                movie_manager.delete_movie(movie_id)

        elif choice == '5':
            movie_manager.close_connection()
            print("Thank you for using Movie Management System!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()