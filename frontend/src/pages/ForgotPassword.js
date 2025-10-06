import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { forgotPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const result = await forgotPassword(email);
    
    if (result.success) {
      setSuccess(result.message);
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

      <div className="flex h-[calc(100vh-4rem)] w-full items-center justify-center">
        <form onSubmit={handleSubmit} className="md:w-[400px] w-80 flex flex-col items-center justify-center bg-white p-8 rounded-xl shadow-lg">
          <h2 className="text-3xl text-indigo-600 font-bold mb-2">Forgot Password?</h2>
          <p className="text-gray-500 text-center mb-6">
            Enter your email address and we'll send you a link to reset your password.
          </p>

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
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-full font-semibold mt-6 hover:bg-indigo-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>

          {/* Back to Login Link */}
          <p className="text-gray-500 text-sm mt-6">
            Remember your password? 
            <Link to="/login" className="text-indigo-600 hover:underline ml-1">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;