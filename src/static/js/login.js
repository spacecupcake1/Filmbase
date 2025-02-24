document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            // Store the token if you're using JWT
            localStorage.setItem('token', data.token);
            window.location.href = '/';  // Redirect to dashboard
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        alert('Error during login: ' + error.message);
    }
});