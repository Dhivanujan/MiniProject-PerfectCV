import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate passwords match
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await register(formData);
    
    if (result.success) {
      setSuccess('Registration successful! Please login to continue.');
      setTimeout(() => navigate('/login'), 2000);
    } else {
      setError(result.message);
    }
    
    setLoading(false);
  };

  return (
    <div className="bg-gradient-to-b from-[#F5F7FF] via-[#fffbee] to-[#E6EFFF]">
      {/* Navbar */}
      <header className="sticky top-0 bg-gradient-to-r from-indigo-50 to-blue-50 shadow-md z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center">
            <span className="font-extrabold text-2xl text-indigo-700 tracking-tight">📄 PerfectCV</span>
          </Link>
        </div>
      </header>

      <div className="flex h-[calc(100vh-4rem)] w-full">
        {/* Left Image for larger screens */}
        <div className="w-1/2 hidden md:inline-block p-4">
          <img className="h-full w-full object-contain" src="/static/CV.png" alt="leftSideImage" />
        </div>

        {/* Right Side Form */}
        <div className="w-full md:w-1/2 flex flex-col items-center justify-center">
          <form onSubmit={handleSubmit} className="md:w-[320px] w-64 flex flex-col items-center justify-center bg-white p-4 rounded-lg shadow-lg">
            <h2 className="text-2xl text-indigo-600 font-medium">Sign Up</h2>
            <p className="text-[10px] text-gray-500/90 mt-1 mb-2">Create your account to get started</p>

            {/* Flash Messages */}
            {error && (
              <div className="flex items-center justify-between text-red-600 w-full bg-red-600/20 h-7 shadow rounded-sm px-2 mb-2">
                <p className="text-[10px]">{error}</p>
                <button type="button" onClick={() => setError('')} className="active:scale-90 transition-all">✕</button>
              </div>
            )}
            
            {success && (
              <div className="flex items-center justify-between text-blue-600 w-full bg-blue-600/10 h-7 shadow rounded-sm px-2 mb-2">
                <p className="text-[10px]">{success}</p>
                <button type="button" onClick={() => setSuccess('')} className="active:scale-90 transition-all">✕</button>
              </div>
            )}

            {/* Full Name */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-8 rounded-full overflow-hidden pl-3 mt-2">
              <input
                placeholder="Full Name"
                className="bg-transparent text-gray-500/80 outline-none text-[11px] w-full h-full"
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
              />
            </div>

            {/* Username */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-8 rounded-full overflow-hidden pl-3 mt-2">
              <input
                placeholder="Username"
                className="bg-transparent text-gray-500/80 outline-none text-[11px] w-full h-full"
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>

            {/* Email */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-8 rounded-full overflow-hidden pl-3 mt-2">
              <input
                placeholder="Email Address"
                className="bg-transparent text-gray-500/80 outline-none text-[11px] w-full h-full"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            {/* Phone Number */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-8 rounded-full overflow-hidden pl-3 mt-2">
              <input
                placeholder="Phone Number"
                className="bg-transparent text-gray-500/80 outline-none text-[11px] w-full h-full"
                type="text"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required
              />
            </div>

            {/* Password */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-8 rounded-full overflow-hidden pl-3 mt-2">
              <input
                placeholder="Password"
                className="bg-transparent text-gray-500/80 outline-none text-[11px] w-full h-full"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            {/* Confirm Password */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-8 rounded-full overflow-hidden pl-3 mt-2">
              <input
                placeholder="Confirm Password"
                className="bg-transparent text-gray-500/80 outline-none text-[11px] w-full h-full"
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-2 rounded-full font-semibold mt-4 hover:bg-indigo-700 transition-all duration-300 text-xs disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>

            {/* Login Link */}
            <p className="text-gray-500 text-[10px] mt-4">
              Already have an account? 
              <Link to="/login" className="text-indigo-600 hover:underline ml-1">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;