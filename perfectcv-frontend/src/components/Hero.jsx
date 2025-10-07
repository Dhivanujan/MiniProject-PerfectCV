import React from "react";
import { Link } from "react-router-dom";
import heroImage from "../assets/Hero.png"; // replace with your image path

export default function Hero() {
  return (
    <main id="hero"className="fade-in flex-grow flex flex-col-reverse lg:flex-row items-center justify-between max-w-7xl mx-auto w-full px-6 sm:px-10 gap-12">
      
      {/* Left Content */}
      <div className="flex flex-col items-center lg:items-start text-center lg:text-left space-y-6 mt-5">
        <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent font-extrabold text-4xl sm:text-5xl lg:text-6xl leading-tight animate-fade-in-down">
          Create the <br className="hidden sm:block" /> Perfect CV in Minutes
        </h1>
        <p className="text-gray-700 max-w-md text-base sm:text-lg leading-relaxed dark:text-gray-100">
          Build <span className="font-semibold text-indigo-600">professional, ATS-friendly</span> resumes in minutes. 
          Stand out, impress recruiters, and land your dream job effortlessly.
        </p>
        <div className="flex flex-wrap gap-4 mt-4 justify-center lg:justify-start">
          <Link
            to="/register"
            className="bg-indigo-600 text-white px-8 py-3 rounded-full text-sm sm:text-base font-medium shadow-lg hover:bg-indigo-700 hover:shadow-xl transition transform hover:-translate-y-1"
          >
            🚀 Get Started
          </Link>
          <Link
            to="/login"
            className="bg-white border border-indigo-600 text-indigo-600 px-8 py-3 rounded-full text-sm sm:text-base font-medium shadow hover:shadow-md hover:bg-indigo-50 transition transform hover:-translate-y-1"
          >
            🔑 Login
          </Link>
        </div>
      </div>

      {/* Right Image */}
      <div className="w-full lg:w-1/2 flex justify-center mt-5">
        <div className="relative">
          <img
            className="rounded-3xl shadow-2xl hover:scale-105 transition-transform duration-700 ease-in-out max-h-[450px] object-cover"
            src={heroImage}
            alt="PerfectCV Hero Image"
          />
          <div className="absolute inset-0 bg-gradient-to-tr from-indigo-600/20 via-purple-600/20 to-transparent rounded-3xl pointer-events-none"></div>
        </div>
      </div>
    </main>
  );
}
