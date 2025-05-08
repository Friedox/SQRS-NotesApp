import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import './style.css';
import '../../style/style.css';
import mkad from "../../assets/icon/MKAD.svg";

const API_BASE = process.env.REACT_APP_API_BASE_URL;

function Login() {
    // State variables for toggling between login/register, form fields, and error message
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault(); // Prevent default form submission
        setError(null); // Reset error message

        // Define API endpoint based on login/register mode
        const endpoint = isLogin
            ? '/api/v1/auth/login/'
            : '/api/v1/auth/register/';

        // Prepare request payload
        const payload = isLogin
            ? {email, password}
            : {email, password, name: name};

        try {
            // Send request to backend API
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                // Try to extract detailed error message
                let errMsg = `Ошибка ${res.status}`;
                try {
                    const errJson = await res.json();
                    errMsg = errJson.detail || JSON.stringify(errJson);
                } catch {
                    // Fallback to status text
                }
                throw new Error(errMsg);
            }

            const data = await res.json();

            // Extract auth token from response
            const token = data.detail.auth_token;
            console.log(data);
            if (!token) {
                throw new Error('auth_token не найден в ответе');
            }

            // Store token in session storage
            sessionStorage.setItem('auth_token', token);
            // Optionally store user info
            sessionStorage.setItem('user', JSON.stringify(data.detail.new_user || {}));

            // Redirect to notes page
            navigate('/notes');
        } catch (err) {
            setError(err.message); // Show error to user
            console.error(err); // Log error for debugging
        }
    };

    // Disable submit button if email or password is empty
    const isDisabled = !(email.trim() && password.trim());

    return (
        <div className="center_block">
            <div className="form-wrapper">
                {/* Logo */}
                <img src={mkad} alt="Your Logo" className="logo"/>

                {/* Login/Register title */}
                <span className="login">{isLogin ? 'Login' : 'Register'}</span>

                {/* Display error message if exists */}
                {error && <div className="error">{error}</div>}

                {/* Form for login or registration */}
                <form onSubmit={handleSubmit}>
                    {/* Name field shown only for registration */}
                    {!isLogin && (
                        <input
                            type="name"
                            name="name"
                            placeholder="Name"
                            value={name}
                            onChange={e => setName(e.target.value)}
                            required
                            className="input-field"
                        />
                    )}

                    {/* Email input field */}
                    <input
                        type="email"
                        name="email"
                        placeholder="Email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        required
                        className="input-field"
                    />

                    {/* Password input field */}
                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                        className="input-field"
                    />

                    {/* Submit button */}
                    <button
                        type="submit"
                        className="submit-button"
                        disabled={isDisabled}
                    >
                        {isLogin ? 'Login' : 'Register'}
                    </button>
                </form>

                {/* Toggle between login and register modes */}
                <button
                    type="button"
                    onClick={() => {
                        setIsLogin(!isLogin);
                        setError(null); // Clear any existing error
                    }}
                    className="toggle-link"
                >
                    {isLogin
                        ? "Don't have an account? Register"
                        : 'Already have an account? Login'}
                </button>
            </div>
        </div>
    );
}

export default Login;
