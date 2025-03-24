// API endpoints
const API_URL = '/api';

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

    // Modify your fetch request's response handling:
    try {
        const response = await fetch(`${API_URL}/movies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Add this to include cookies for session
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        console.log('Server response:', data);
        
        if (response.ok) {
            alert('Movie added successfully!');
            window.location.href = '/';
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Full error:', error);
        alert('Error adding movie: ' + error.message);
    }
});