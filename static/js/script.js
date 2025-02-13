// API endpoints
const API_URL = 'http://localhost:5000/api';

// DOM Elements
const movieList = document.querySelector('.movie-list tbody');
const editModal = document.getElementById('editModal');
const editMovieForm = document.getElementById('editMovieForm');
const closeModal = document.querySelector('.close');

// Load movies when page loads
document.addEventListener('DOMContentLoaded', loadMovies);

// Load all movies
async function loadMovies() {
    try {
        const response = await fetch(`${API_URL}/movies`);
        const data = await response.json();
        if (data.movies) {
            displayMovies(data.movies);
        } else {
            displayMovies([]);  // Display empty array if no movies
        }
    } catch (error) {
        console.error('Error details:', error);
        alert('Error loading movies: ' + error.message);
    }
}

// Display movies in table
function displayMovies(movies) {
    movieList.innerHTML = '';
    if (!Array.isArray(movies)) {
        console.error('Movies data is not an array:', movies);
        return;
    }
    movies.forEach(movie => {
        const row = document.createElement('tr');
        // Safely escape text and handle null/undefined values
        const safeText = (text) => text ? text.replace(/</g, '&lt;').replace(/'/g, '&#39;') : '';
        
        row.innerHTML = `
            <td>${safeText(movie.title) || ''}</td>
            <td>${safeText(movie.director) || ''}</td>
            <td>${movie.release_year || ''}</td>
            <td>${safeText(movie.genre) || ''}</td>
            <td>${movie.rating || ''}</td>
            <td>
                <div class="action-buttons">
                    <button class="edit-btn" onclick="openEditModal(
                        ${movie.id || 0}, 
                        '${safeText(movie.title) || ''}', 
                        '${safeText(movie.director) || ''}', 
                        ${movie.release_year || 0}, 
                        '${safeText(movie.genre) || ''}', 
                        ${movie.rating || 0}
                    )">Edit</button>
                    <button class="delete-btn" onclick="deleteMovie(${movie.id || 0})">Delete</button>
                </div>
            </td>
        `;
        movieList.appendChild(row);
    });
}

// Open edit modal
function openEditModal(id, title, director, releaseYear, genre, rating) {
    editModal.style.display = 'block';
    document.getElementById('editTitle').value = title;
    document.getElementById('editDirector').value = director;
    document.getElementById('editReleaseYear').value = releaseYear;
    document.getElementById('editGenre').value = genre;
    document.getElementById('editRating').value = rating;
    editMovieForm.dataset.movieId = id;
}

// Close modal
closeModal.onclick = function() {
    editModal.style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == editModal) {
        editModal.style.display = 'none';
    }
}

// Edit movie form submission
editMovieForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const movieId = editMovieForm.dataset.movieId;
    const formData = {
        title: document.getElementById('editTitle').value,
        director: document.getElementById('editDirector').value,
        releaseYear: parseInt(document.getElementById('editReleaseYear').value),
        genre: document.getElementById('editGenre').value,
        rating: parseFloat(document.getElementById('editRating').value)
    };

    try {
        const response = await fetch(`${API_URL}/movies/${movieId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            editModal.style.display = 'none';
            loadMovies();
            alert('Movie updated successfully!');
        } else {
            const data = await response.json();
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Error updating movie: ' + error.message);
    }
});

// Delete movie
async function deleteMovie(movieId) {
    if (confirm('Are you sure you want to delete this movie?')) {
        try {
            const response = await fetch(`${API_URL}/movies/${movieId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadMovies();
                alert('Movie deleted successfully!');
            } else {
                const data = await response.json();
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert('Error deleting movie: ' + error.message);
        }
    }
}