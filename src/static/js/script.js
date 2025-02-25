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
document.addEventListener('DOMContentLoaded', function() {
    const userInfo = document.getElementById('userInfo');
    const usernameSpan = document.getElementById('username');
    const userRoleSpan = document.getElementById('userRole');
    const adminControls = document.getElementById('adminControls');
    const actionsHeader = document.getElementById('actionsHeader');
    const movieList = document.querySelector('.movie-list tbody');
    const editModal = document.getElementById('editModal');
    const editMovieForm = document.getElementById('editMovieForm');
    const closeModal = document.querySelector('.close');

    // Fetch user info
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            usernameSpan.textContent = data.username;
            userRoleSpan.textContent = data.role;
            if (data.role === 'admin') {
                adminControls.style.display = 'block';
                actionsHeader.style.display = 'table-cell';
            }
        });

    // Fetch movies
    fetch('/api/movies')
        .then(response => response.json())
        .then(data => {
            data.movies.forEach(movie => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${movie.title}</td>
                    <td>${movie.director}</td>
                    <td>${movie.release_year}</td>
                    <td>${movie.genre}</td>
                    <td>${movie.rating}</td>
                    <td class="actions" style="display: ${userRoleSpan.textContent === 'admin' ? 'table-cell' : 'none'};">
                        <button class="edit-btn" data-id="${movie.id}">Edit</button>
                        <button class="delete-btn" data-id="${movie.id}">Delete</button>
                    </td>
                `;
                movieList.appendChild(row);
            });

            // Add event listeners for edit and delete buttons
            document.querySelectorAll('.edit-btn').forEach(button => {
                button.addEventListener('click', handleEdit);
            });
            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', handleDelete);
            });
        });

    // Handle edit button click
    function handleEdit(event) {
        const movieId = event.target.dataset.id;
        fetch(`/api/movies/${movieId}`)
            .then(response => response.json())
            .then(movie => {
                editMovieForm.editTitle.value = movie.title;
                editMovieForm.editDirector.value = movie.director;
                editMovieForm.editReleaseYear.value = movie.release_year;
                editMovieForm.editGenre.value = movie.genre;
                editMovieForm.editRating.value = movie.rating;
                editMovieForm.dataset.id = movieId;
                editModal.style.display = 'block';
            });
    }

    // Handle delete button click
    function handleDelete(event) {
        const movieId = event.target.dataset.id;
        fetch(`/api/movies/${movieId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                event.target.closest('tr').remove();
            } else {
                alert(data.error);
            }
        });
    }

    // Handle edit form submission
    editMovieForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const movieId = editMovieForm.dataset.id;
        const updatedMovie = {
            title: editMovieForm.editTitle.value,
            director: editMovieForm.editDirector.value,
            release_year: editMovieForm.editReleaseYear.value,
            genre: editMovieForm.editGenre.value,
            rating: editMovieForm.editRating.value
        };
        fetch(`/api/movies/${movieId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedMovie)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                location.reload();
            } else {
                alert(data.error);
            }
        });
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        editModal.style.display = 'none';
    });

    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
    });
});