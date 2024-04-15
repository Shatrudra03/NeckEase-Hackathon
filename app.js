// app.js

import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent form submission

    const email = loginForm.email.value;
    const password = loginForm.password.value;

    try {
        const auth = getAuth();
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        console.log('User logged in:', user.email);
        // Add code to redirect or display success message
    } catch (error) {
        console.error('Login error:', error.message);
        alert('Login failed. Please check your credentials.');
    }
});
