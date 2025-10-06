import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = ({ showAuthButtons = true }) => {
  return (
    <header className="sticky top-0 bg-gradient-to-r from-indigo-50 to-blue-50 shadow-md z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        {/* Logo */}
        <Link to="/" className="flex items-center">
          <span className="font-extrabold text-2xl text-indigo-700 tracking-tight">
            📄 PerfectCV
          </span>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-6 text-gray-700 text-sm font-semibold">
          <Link 
            to="/" 
            className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300"
          >
            <span>🏠 Home</span>
          </Link>
          <a 
            href="#features" 
            className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300"
          >
            <span>✨ Features</span>
          </a>
          <a 
            href="#about" 
            className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300"
          >
            <span>ℹ️ About</span>
          </a>
          <a 
            href="#contact" 
            className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300"
          >
            <span>📧 Contact</span>
          </a>
        </nav>

        {/* Auth Buttons */}
        {showAuthButtons && (
          <div className="flex items-center gap-3">
            <Link 
              to="/login" 
              className="hidden md:flex items-center gap-2 px-5 py-2 text-indigo-700 font-semibold rounded-xl border border-indigo-200 hover:bg-indigo-50 transition-all duration-300"
            >
              <span>🔑 Login</span>
            </Link>
            <Link 
              to="/register" 
              className="flex items-center gap-2 px-5 py-2 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all duration-300 shadow-lg"
            >
              <span>🚀 Get Started</span>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;