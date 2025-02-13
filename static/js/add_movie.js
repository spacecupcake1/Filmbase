// API endpoints
const API_URL = 'http://localhost:5000/api';

// DOM Elements
const addMovieForm = document.getElementById('addMovieForm');

// Add movie form submission
addMovieForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        title: document.getElementById('title').value,
        director: document.getElementById('director').value,
        releaseYear: parseInt(document.getElementById('releaseYear').value),
        genre: document.getElementById('genre').value,
        rating: parseFloat(document.getElementById('rating').value)
    };

    try {
        const response = await fetch(`${API_URL}/movies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('Movie added successfully!');
            window.location.href = '/';  // Redirect to the movie list page
        } else {
            const data = await response.json();
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Error adding movie: ' + error.message);
    }
});