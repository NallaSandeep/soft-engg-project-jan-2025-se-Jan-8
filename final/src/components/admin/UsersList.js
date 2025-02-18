import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaEdit, FaTrash } from "react-icons/fa";
import "bootstrap/dist/css/bootstrap.min.css";

const UsersList = () => {
    const navigate = useNavigate();
    const [filters, setFilters] = useState({ role: "", status: "", search: "" });

    // Placeholder user data
    const users = [
        { id: 1, first_name: "Alice", last_name: "Admin", username: "alice_admin", email: "alice@example.com", role: "admin", is_active: true },
        { id: 2, first_name: "Bob", last_name: "Student", username: "bob_student", email: "bob@example.com", role: "student", is_active: false },
        { id: 3, first_name: "Charlie", last_name: "TA", username: "charlie_ta", email: "charlie@example.com", role: "ta", is_active: true }
    ];

    // Function to handle filter change
    const handleFilterChange = (name, value) => {
        setFilters((prev) => ({ ...prev, [name]: value }));
    };

    // Apply filters to user list
    const filteredUsers = users.filter(user => {
        // Filter by role
        if (filters.role && user.role !== filters.role) return false;

        // Filter by status
        if (filters.status) {
            const isActive = filters.status === "active";
            if (user.is_active !== isActive) return false;
        }

        // Filter by search query (checking first name, last name, and email)
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            if (
                !user.first_name.toLowerCase().includes(searchTerm) &&
                !user.last_name.toLowerCase().includes(searchTerm) &&
                !user.email.toLowerCase().includes(searchTerm)
            ) {
                return false;
            }
        }

        return true;
    });

    const handleDelete = (userId) => {
        if (window.confirm("Are you sure you want to delete this user?")) {
            console.log("User deleted:", userId);
        }
    };

    return (
        <div className="container-fluid py-5 text-white" style={{ backgroundColor: "#1E1E1E", minHeight: "100vh" }}>
            {/* Page Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="text-warning fw-bold">Users</h2>
                <button className="btn btn-warning fw-bold shadow-sm" onClick={() => navigate("/admin/users/new")}>
                    Add User
                </button>
            </div>

            {/* Filters Section */}
            <div className="card bg-dark border-warning shadow-sm p-3 mb-4">
                <div className="row g-3">
                    <div className="col-md-4">
                        <label className="form-label text-warning fw-bold">Role</label>
                        <select className="form-select bg-dark text-white border-warning" value={filters.role} onChange={(e) => handleFilterChange("role", e.target.value)}>
                            <option value="">All Roles</option>
                            <option value="admin">Admin</option>
                            <option value="teacher">Teacher</option>
                            <option value="ta">Teaching Assistant</option>
                            <option value="student">Student</option>
                        </select>
                    </div>
                    <div className="col-md-4">
                        <label className="form-label text-warning fw-bold">Status</label>
                        <select className="form-select bg-dark text-white border-warning" value={filters.status} onChange={(e) => handleFilterChange("status", e.target.value)}>
                            <option value="">All Status</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                    <div className="col-md-4">
                        <label className="form-label text-warning fw-bold">Search</label>
                        <input
                            type="text"
                            className="form-control bg-dark text-white border-warning"
                            placeholder="Search users..."
                            value={filters.search}
                            onChange={(e) => handleFilterChange("search", e.target.value)}
                        />
                    </div>
                </div>
            </div>

            {/* Users Table */}
            <div className="card bg-dark border-warning shadow-lg">
                <div className="card-body">
                    <table className="table table-dark table-hover align-middle">
                        <thead className="border-warning">
                            <tr className="text-warning fw-bold">
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th className="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredUsers.length > 0 ? (
                                filteredUsers.map((user) => (
                                    <tr key={user.id} className="border-bottom border-warning">
                                        <td className="fw-semibold">{user.first_name} {user.last_name}</td>
                                        <td>{user.email}</td>
                                        <td>
                                            <span className={`badge ${user.role === "admin" ? "bg-primary" : user.role === "student" ? "bg-success" : "bg-info"}`}>
                                                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge ${user.is_active ? "bg-success" : "bg-danger"}`}>
                                                {user.is_active ? "Active" : "Inactive"}
                                            </span>
                                        </td>
                                        <td className="text-center">
                                            <button className="btn btn-sm btn-warning me-2 shadow-sm" onClick={() => navigate(`/admin/users/${user.id}/edit`)} title="Edit">
                                                <FaEdit />
                                            </button>
                                            <button className="btn btn-sm btn-danger shadow-sm" onClick={() => handleDelete(user.id)} title="Delete">
                                                <FaTrash />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center text-warning py-3">No users found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default UsersList;
