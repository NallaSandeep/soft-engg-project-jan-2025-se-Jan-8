import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

const mockUsers = {
    "admin@studyhub.com": { password: "admin123", role: "admin" },
    "student@studyhub.com": { password: "student123", role: "student" },
    "ta@studyhub.com": { password: "ta123", role: "ta" }
};

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        setTimeout(() => {
            if (mockUsers[email] && mockUsers[email].password === password) {
                const role = mockUsers[email].role;

                // ✅ Store user details in sessionStorage
                sessionStorage.setItem("userEmail", email);
                sessionStorage.setItem("userRole", role);

                // ✅ Redirect based on role
                const redirectPaths = {
                    admin: "/admin/dashboard",
                    student: "/student/dashboard",
                    ta: "/ta/dashboard"
                };
                navigate(redirectPaths[role] || "/dashboard");
            } else {
                setError('Invalid email or password');
            }
            setLoading(false);
        }, 1000);
    };

    return (
        <div className="d-flex align-items-center justify-content-center vh-100 bg-dark text-white">
            <div className="card p-4 shadow-lg" style={{ width: '350px', backgroundColor: '#333' }}>
                <h2 className="text-center text-warning">Login to StudyHub</h2>

                {error && <div className="alert alert-danger mt-3">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label text-white">Email</label>
                        <input 
                            type="email" 
                            className="form-control" 
                            value={email} 
                            onChange={(e) => setEmail(e.target.value)} 
                            required
                            placeholder="Enter your email" 
                            disabled={loading}
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label text-white">Password</label>
                        <input 
                            type="password" 
                            className="form-control" 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
                            required
                            placeholder="Enter your password" 
                            disabled={loading}
                        />
                    </div>
                    <button type="submit" className="btn btn-warning w-100" disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <div className="text-center mt-3">
                    <a href="/forgot-password" className="text-light">Forgot your password?</a>
                </div>
                <div className="text-center mt-2 text-white">
                    <span>Don't have an account? </span>
                    <a href="/register" className="text-warning">Sign up</a>
                </div>
            </div>
        </div>
    );
};

export default Login;
