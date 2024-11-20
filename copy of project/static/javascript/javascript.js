// Wait for the DOM to be fully loaded before executing JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Select the login form element
    const loginForm = document.getElementById('loginForm');

    // Add event listener for form submission
    loginForm.addEventListener('submit', function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Get the values from the form inputs
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Hardcoded username and password (for demonstration purposes)
        const correctUsername = 'Admin';
        const correctPassword = 'password';

        // Check if the entered username and password match the hardcoded values
        if (username === correctUsername && password === correctPassword) {
            // Display a colorful prompt message for successful login
            alert('Successful Login! Welcome');

            // Simulate redirect to dashboard (replace with actual redirect code)
            setTimeout(function() {
                window.location.href = '/dashboard'; // Redirect to dashboard page
            }, 1000); // Redirect after 1 second (1000 milliseconds)
        } else {
            // Display a colorful prompt message for failed login
            alert('Login Failed. Please try again!');
        }
    });
});
