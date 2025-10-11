// Footer.jsx
import React from "react";
import { FaLinkedin, FaTwitter, FaFacebook, FaGithub } from "react-icons/fa";

function Footer() {
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-300 px-6 md:px-16 lg:px-24 xl:px-32 w-full">
      <div className="flex flex-col md:flex-row justify-between gap-10 py-12 border-t border-gray-300/30 dark:border-gray-700/50">
        {/* Branding */}
        <div className="max-w-xs">
          <span className="font-bold text-2xl text-indigo-600 dark:text-indigo-400">PerfectCV</span>
          <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            Create professional, ATS-friendly resumes in minutes with AI-powered suggestions.
            Stand out and land your dream job effortlessly.
          </p>
          <div className="flex items-center gap-4 mt-4">
            <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400"><FaLinkedin size={20} /></a>
            <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400"><FaTwitter size={20} /></a>
            <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400"><FaFacebook size={20} /></a>
            <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400"><FaGithub size={20} /></a>
          </div>
        </div>

        {/* Links */}
        <div className="flex flex-wrap md:flex-nowrap gap-10">
          <div>
            <h2 className="font-semibold text-gray-900 dark:text-gray-200 mb-4">RESOURCES</h2>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Documentation</a>
              </li>
              <li>
                <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Tutorials</a>
              </li>
              <li>
                <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Community</a>
              </li>
            </ul>
          </div>

          <div>
            <h2 className="font-semibold text-gray-900 dark:text-gray-200 mb-4">COMPANY</h2>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Home</a>
              </li>
              <li>
                <a href="/features" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Features</a>
              </li>
              <li>
                <a href="/about" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">About</a>
              </li>
              <li>
                <a href="/contact" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Contact</a>
              </li>
            </ul>
          </div>

          <div>
            <h2 className="font-semibold text-gray-900 dark:text-gray-200 mb-4">LEGAL</h2>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Privacy Policy</a>
              </li>
              <li>
                <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Terms of Service</a>
              </li>
              <li>
                <a href="#" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Cookie Policy</a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom */}
      <div className="text-center py-4 text-xs md:text-sm text-gray-500 dark:text-gray-400">
        © 2024 <a href="/" className="text-indigo-600 dark:text-indigo-400 font-medium">PerfectCV</a>. All rights reserved.
      </div>
    </footer>
  );
}

export default Footer;
