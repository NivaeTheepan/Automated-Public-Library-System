import './HomePage.css';
import { IoMdPerson } from "react-icons/io";
import { FaLock, FaEye, FaEyeSlash } from "react-icons/fa6";
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [showPassword, setShowPassword] = useState(false); // New state for password visibility
    const navigate = useNavigate();

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        
        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
    
            const data = await response.json();
            
            if (data.success) {
                const storage = rememberMe ? localStorage : sessionStorage;
                storage.setItem('username', data.username);
                storage.setItem('authToken', data.token);
                storage.setItem('isAdmin', data.isAdmin.toString());
                
                // Redirect based on admin status
                if (data.isAdmin) {
                    navigate('/admin');
                } else {
                    navigate('/dashboard');
                }
            } else {
                setError(data.message || 'Invalid credentials');
            }
        } catch (err) {
            setError('Failed to connect to server');
        }
    };

    return (
        <div className="wrapper">
            <h1>RemoteShelf: Public Library Portal</h1>
            <h2>Login</h2>
            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="input-box">
                    <input 
                        type="text" 
                        placeholder="Username" 
                        required 
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        autoComplete="username"
                    />
                    <IoMdPerson className="icon" />
                </div>
                <div className="input-box">
                    <input 
                        type={showPassword ? "text" : "password"} 
                        placeholder="Password" 
                        required 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        autoComplete="current-password"
                    />
                    <div className="password-toggle" onClick={togglePasswordVisibility}>
                        {showPassword ? <FaEyeSlash className="icon" /> : <FaEye className="icon" />}
                    </div>
                    <FaLock className="icon lock-icon" />
                </div>
                <div className="remember-forgot">
                    <label>
                        <input 
                            type="checkbox" 
                            checked={rememberMe}
                            onChange={(e) => setRememberMe(e.target.checked)}
                        /> 
                        Remember Me?
                    </label>
                    <a href="#" onClick={(e) => {
                        e.preventDefault();
                        setError('Forgot password feature coming soon');
                    }}> 
                        Forgot Password?
                    </a>
                </div>
                <button 
                    type="submit" 
                    className="btn"
                    disabled={isLoading}
                >
                    {isLoading ? 'Logging in...' : 'Login'}
                </button>
            </form>
        </div>
    );
};

export default HomePage;