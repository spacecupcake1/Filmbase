# Movie Management System

A web-based application for managing movies with role-based access control. Administrators can perform full CRUD operations, while clients have read-only access.

## Features

- **User Authentication**
  - Login/Register functionality
  - Role-based access control (Admin/Client)
  - Session management

- **Movie Management**
  - View all movies (All users)
  - Add new movies (Admin only)
  - Edit existing movies (Admin only)
  - Delete movies (Admin only)

## Technology Stack

- **Backend:**
  - Python 3.x
  - Flask
  - MySQL

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

- **Database:**
  - MySQL

## Prerequisites

- Python 3.11
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd Filmbase
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
     ```bash
     venv\Scripts\activate
     ```

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure MySQL:
   - Create a new database:
     ```sql
     CREATE DATABASE movie_db;
     ```
   - Update database configuration in `app.py`:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'your_username',
         'password': 'your_password',
         'database': 'movie_db'
     }
     ```

## Project Structure

```
movie-management-system/
├── app.py
├── templates/
│   ├── index.html
│   ├── add_movie.html
│   ├── login.html
│   └── register.html
└── static/
    ├── css/
    │   ├── styles.css
    │   └── auth.css
    └── js/
        ├── script.js
        ├── add_movie.js
        ├── login.js
        └── register.js
```

## Running the Application

1. Make sure your MySQL server is running

2. Start the Flask application:
   ```bash
   py app.py
   ```

3. Access the application:
   - Open your web browser and navigate to `http://localhost:5000`
   - You will be redirected to the login page

## Default Admin Account

The system creates a default admin account on first run:
- **Username:** admin
- **Password:** admin123

## User Roles

1. **Admin**
   - Full access to all features
   - Can perform CRUD operations on movies
   - Can view all movies

2. **Client**
   - Read-only access
   - Can only view the movie list

## API Endpoints

- **Authentication:**
  - `POST /api/login` - User login
  - `POST /api/register` - User registration
  - `GET /api/user-info` - Get current user information

- **Movies:**
  - `GET /api/movies` - Get all movies
  - `POST /api/movies` - Add new movie (Admin only)
  - `PUT /api/movies/<id>` - Update movie (Admin only)
  - `DELETE /api/movies/<id>` - Delete movie (Admin only)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
