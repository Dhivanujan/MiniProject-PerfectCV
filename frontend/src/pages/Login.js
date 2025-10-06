import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { login } = useAuth();
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

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      setSuccess('Login successful! Redirecting...');
      setTimeout(() => navigate('/dashboard'), 1500);
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

        {/* Right Side Login Form */}
        <div className="w-full md:w-1/2 flex flex-col items-center justify-center">
          <form onSubmit={handleSubmit} className="md:w-[400px] w-80 flex flex-col items-center justify-center bg-white p-6 rounded-xl shadow-lg">
            {/* Logo & Title */}
            <h1 className="text-4xl font-bold text-indigo-600 mb-2">PerfectCV</h1>
            <p className="text-gray-500 mb-6 text-center">Sign in to enhance your CV and unlock your potential</p>

            {/* Flash Messages */}
            {error && (
              <div className="flex items-center justify-between text-red-600 w-full bg-red-600/20 h-10 shadow rounded-sm px-2 mb-4">
                <p className="text-sm">{error}</p>
                <button type="button" onClick={() => setError('')} className="active:scale-90 transition-all">✕</button>
              </div>
            )}
            
            {success && (
              <div className="flex items-center justify-between text-blue-600 w-full bg-blue-600/10 h-10 shadow rounded-sm px-2 mb-4">
                <p className="text-sm">{success}</p>
                <button type="button" onClick={() => setSuccess('')} className="active:scale-90 transition-all">✕</button>
              </div>
            )}

            {/* Email Input */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-12 rounded-full overflow-hidden pl-6 mt-4">
              <input
                placeholder="Email Address"
                className="bg-transparent text-gray-500/80 outline-none text-sm w-full h-full"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            {/* Password Input */}
            <div className="flex items-center w-full bg-transparent border border-gray-300/60 h-12 rounded-full overflow-hidden pl-6 mt-4">
              <input
                placeholder="Password"
                className="bg-transparent text-gray-500/80 outline-none text-sm w-full h-full"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex justify-between items-center w-full mt-4">
              <label className="flex items-center text-gray-500 text-sm cursor-pointer">
                <input type="checkbox" className="mr-2 accent-indigo-600" />
                Remember me
              </label>
              <Link to="/forgot-password" className="text-indigo-600 text-sm hover:underline">
                Forgot Password?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 rounded-full font-semibold mt-6 hover:bg-indigo-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>

            {/* Sign Up Link */}
            <p className="text-gray-500 text-sm mt-6">
              Don't have an account? 
              <Link to="/register" className="text-indigo-600 hover:underline ml-1">
                Sign up
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;