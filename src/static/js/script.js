// API endpoints
const API_URL = 'http://localhost:5000/api';

// DOM Elements
const movieList = document.querySelector('.movie-list tbody');
const editModal = document.getElementById('editModal');
const editMovieForm = document.getElementById('editMovieForm');
const closeModal = document.querySelector('.close');
const adminControls = document.getElementById('adminControls');
const actionsHeader = document.getElementById('actionsHeader');
const username = document.getElementById('username');
const userRole = document.getElementById('userRole');

// Check user role on page load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/user-info');
        // Check if response redirects to login
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to get user info');
        }

        const data = await response.json();
        
        // Update user info
        username.textContent = data.username;
        userRole.textContent = data.role;

        // Show admin controls if user is admin
        if (data.role === 'admin') {
            adminControls.style.display = 'inline-block';
            actionsHeader.style.display = 'table-cell';
        }

        // Load movies
        loadMovies(data.role === 'admin');
    } catch (error) {
        console.error('Error loading user info:', error);
        // Redirect to login if there's an error
        window.location.href = '/login';
    }
});

// Load all movies
async function loadMovies(isAdmin) {
    try {
        const response = await fetch(`${API_URL}/movies`);
        
        // Check if response redirects to login
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to load movies');
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Received non-JSON response');
        }

        const data = await response.json();
        if (data.movies) {
            displayMovies(data.movies, isAdmin);
        } else {
            displayMovies([], isAdmin);
        }
    } catch (error) {
        console.error('Error details:', error);
        if (error.message.includes('JSON')) {
            // If we get HTML instead of JSON, redirect to login
            window.location.href = '/login';
        } else {
            alert('Error loading movies: ' + error.message);
        }
    }
}

// Display movies in table
function displayMovies(movies, isAdmin) {
    movieList.innerHTML = '';
    if (!Array.isArray(movies)) {
        console.error('Movies data is not an array:', movies);
        return;
    }

    // Safely escape text and handle null/undefined values
    const safeText = (text) => text ? text.toString().replace(/</g, '&lt;').replace(/'/g, '&#39;') : '';
    
    movies.forEach(movie => {
        const row = document.createElement('tr');
        let html = `
            <td>${safeText(movie.title) || ''}</td>
            <td>${safeText(movie.director) || ''}</td>
            <td>${movie.release_year || ''}</td>
            <td>${safeText(movie.genre) || ''}</td>
            <td>${movie.rating || ''}</td>
        `;

        // Only add action buttons for admin users
        if (isAdmin) {
            html += `
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
        }

        row.innerHTML = html;
        movieList.appendChild(row);
    });
}

// Edit and Delete functions remain the same...
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

        if (response.redirected) {
            window.location.href = response.url;
            return;
        }

        if (response.ok) {
            editModal.style.display = 'none';
            loadMovies(true);
            alert('Movie updated successfully!');
        } else {
            const data = await response.json();
            if (response.status === 403) {
                alert('You do not have permission to perform this action');
            } else {
                alert(`Error: ${data.error}`);
            }
        }
    } catch (error) {
        console.error('Error updating movie:', error);
        if (error.message.includes('JSON')) {
            window.location.href = '/login';
        } else {
            alert('Error updating movie: ' + error.message);
        }
    }
});

// Delete movie
async function deleteMovie(movieId) {
    if (confirm('Are you sure you want to delete this movie?')) {
        try {
            const response = await fetch(`${API_URL}/movies/${movieId}`, {
                method: 'DELETE'
            });

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            if (response.ok) {
                loadMovies(true);
                alert('Movie deleted successfully!');
            } else {
                const data = await response.json();
                if (response.status === 403) {
                    alert('You do not have permission to perform this action');
                } else {
                    alert(`Error: ${data.error}`);
                }
            }
        } catch (error) {
            console.error('Error deleting movie:', error);
            if (error.message.includes('JSON')) {
                window.location.href = '/login';
            } else {
                alert('Error deleting movie: ' + error.message);
            }
        }
    }
}