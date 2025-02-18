import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: ''
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError(null);
    };

    const validateForm = () => {
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return false;
        }
        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return false;
        }
        return true;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!validateForm()) return;
        setLoading(true);
        setTimeout(() => setLoading(false), 1000); // Simulating a request
    };

    return (
        <div className="d-flex justify-content-center align-items-center vh-100 bg-dark">
            <div className="card p-4 text-white" style={{ backgroundColor: '#333', width: '400px' }}>
                <h2 className="text-center text-warning">Create your account</h2>
                <p className="text-center">
                    Or <Link to="/login" className="text-warning">sign in to your existing account</Link>
                </p>
                {error && <div className="alert alert-danger">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label">Username</label>
                        <input
                            type="text"
                            name="username"
                            className="form-control bg-dark text-white border-secondary"
                            value={formData.username}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Email</label>
                        <input
                            type="email"
                            name="email"
                            className="form-control bg-dark text-white border-secondary"
                            value={formData.email}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">First Name</label>
                        <input
                            type="text"
                            name="first_name"
                            className="form-control bg-dark text-white border-secondary"
                            value={formData.first_name}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Last Name</label>
                        <input
                            type="text"
                            name="last_name"
                            className="form-control bg-dark text-white border-secondary"
                            value={formData.last_name}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Password</label>
                        <input
                            type="password"
                            name="password"
                            className="form-control bg-dark text-white border-secondary"
                            value={formData.password}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Confirm Password</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            className="form-control bg-dark text-white border-secondary"
                            value={formData.confirmPassword}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="btn btn-warning w-100"
                        disabled={loading}
                    >
                        {loading ? 'Creating account...' : 'Sign up'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Register;