import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { Link } from 'react-router-dom';

const Home = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="bg-gradient-to-b from-[#F5F7FF] via-[#fffbee] to-[#E6EFFF]">
      {/* Navbar with mobile menu functionality */}
      <header className="sticky top-0 bg-gradient-to-r from-indigo-50 to-blue-50 shadow-md z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <span className="font-extrabold text-2xl text-indigo-700 tracking-tight">📄 PerfectCV</span>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-6 text-gray-700 text-sm font-semibold">
            <Link to="/" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">
              <span>🏠 Home</span>
            </Link>
            <a href="#features" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">
              <span>✨ Features</span>
            </a>
            <a href="#about" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">
              <span>ℹ️ About</span>
            </a>
            <a href="#contact" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">
              <span>📧 Contact</span>
            </a>
          </nav>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/login" className="text-gray-700 hover:text-indigo-800 text-sm font-semibold px-4 py-2 rounded-xl hover:bg-indigo-100 transition-all duration-300">🔑 Login</Link>
            <Link to="/register" className="bg-indigo-600 text-white px-6 py-2 rounded-full text-sm font-semibold hover:bg-indigo-700 transition-all duration-300 shadow-md hover:shadow-lg">🚀 Get Started</Link>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden text-gray-700 focus:outline-none"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} 
              />
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <nav className="md:hidden bg-indigo-50 text-gray-700 text-sm font-semibold">
            <div className="flex justify-end px-6 py-4">
              <button 
                className="text-gray-700 focus:outline-none"
                onClick={() => setMobileMenuOpen(false)}
              >
                <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex flex-col items-center gap-4 py-4">
              <Link to="/" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">🏠 Home</Link>
              <a href="#features" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">✨ Features</a>
              <a href="#about" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">ℹ️ About</a>
              <a href="#contact" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">📧 Contact</a>
              <Link to="/login" className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-indigo-100 hover:text-indigo-800 transition-all duration-300">🔑 Login</Link>
              <Link to="/register" className="bg-indigo-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-indigo-700 transition-all duration-300">🚀 Get Started</Link>
            </div>
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-grow flex flex-col-reverse lg:flex-row items-center justify-between max-w-7xl mx-auto w-full mt-16 px-6 sm:px-10 gap-12">
        <div className="flex flex-col items-center lg:items-start text-center lg:text-left">
          <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent font-extrabold text-4xl sm:text-5xl lg:text-6xl leading-tight">
            Create the <br className="hidden sm:block"/> Perfect CV in minutes
          </h1>
          <p className="mt-6 text-gray-600 max-w-md text-base sm:text-lg leading-relaxed">
            Build professional, ATS-friendly resumes quickly with <span className="font-semibold text-indigo-600">PerfectCV</span>.
            Stand out and land your dream job effortlessly.
          </p>
          <div className="flex gap-4 mt-8">
            <Link to="/register"
               className="bg-indigo-600 text-white px-8 py-3 rounded-full text-sm sm:text-base font-medium shadow-lg hover:bg-indigo-700 hover:shadow-xl transition">
              🚀 Get Started
            </Link>
            <Link to="/login"
               className="bg-white border border-indigo-600 text-indigo-600 px-8 py-3 rounded-full text-sm sm:text-base font-medium shadow hover:shadow-md hover:bg-indigo-50 transition">
              🔑 Login
            </Link>
          </div>
        </div>
        <div className="w-full lg:w-1/2 flex justify-center">
          <img className="rounded-3xl shadow-lg hover:scale-105 transition-transform duration-500 max-h-[450px] object-cover"
               src="/static/Hero.png"
               alt="PerfectCV Hero Image" />
        </div>
      </main>

      {/* Features Section */}
      <section id="features" className="mt-20 px-3 sm:px-10 max-w-7xl mx-auto">
        <h2 className="text-center text-2xl font-bold text-gray-900 mb-10">Why Choose PerfectCV?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <img src="https://img.icons8.com/fluency/48/000000/idea.png" className="mx-auto mb-4" alt="AI Icon"/>
            <h3 className="font-semibold text-lg mb-2">AI-powered Suggestions</h3>
            <p className="text-gray-600 text-sm">Get smart recommendations to improve your CV content and format instantly.</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <img src="https://img.icons8.com/fluency/48/000000/template.png" className="mx-auto mb-4" alt="Template Icon"/>
            <h3 className="font-semibold text-lg mb-2">Professional Templates</h3>
            <p className="text-gray-600 text-sm">Choose from a variety of ready-made templates that are modern and recruiter-friendly.</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <img src="https://img.icons8.com/fluency/48/000000/download.png" className="mx-auto mb-4" alt="Download Icon"/>
            <h3 className="font-semibold text-lg mb-2">Download as PDF</h3>
            <p className="text-gray-600 text-sm">Save your CV in a professional PDF format ready to send to employers.</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="mt-20 mb-10 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Ready to make your perfect CV?</h2>
        <Link to="/register" className="bg-indigo-600 text-white px-8 py-3 rounded-full text-sm font-medium hover:bg-indigo-700 transition">
          Get Started
        </Link>
      </section>

      {/* Footer */}
      <footer className="px-6 md:px-16 lg:px-24 xl:px-32 w-full">
        <div className="flex flex-col md:flex-row items-start justify-center gap-10 py-10 border-b border-gray-500/30">
          <div className="max-w-96">
            <span className="font-bold text-lg md:text-xl text-gray-900">PerfectCV</span>
            <p className="mt-6 text-sm text-gray-500">
              Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been.
            </p>
            <div className="flex items-center gap-2 mt-3">
              <a href="#"><svg width="20" height="20"></svg></a>
              <a href="#"><svg width="20" height="20"></svg></a>
              <a href="#"><svg width="20" height="20"></svg></a>
            </div>
          </div>
          <div className="w-1/2 flex flex-wrap md:flex-nowrap justify-between">
            <div>
              <h2 className="font-semibold text-gray-900 mb-5">RESOURCES</h2>
              <ul className="text-sm text-gray-500 space-y-2 list-none">
                <li><a href="#">Documentation</a></li>
                <li><a href="#">Tutorials</a></li>
                <li><a href="#">Community</a></li>
              </ul>
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 mb-5">COMPANY</h2>
              <ul className="text-sm text-gray-500 space-y-2 list-none">
                <li><Link to="/">Home</Link></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
        <p className="py-4 text-center text-xs md:text-sm text-gray-500">
          Copyright 2024 © <Link to="/">PerfectCV</Link>. All Right Reserved.
        </p>
      </footer>
    </div>
  );
};

export default Home;