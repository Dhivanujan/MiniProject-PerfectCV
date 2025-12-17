import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import heroImage from "../assets/Hero.png"; // replace with your image path

export default function Hero() {
  return (
    <main id="hero" className="flex-grow flex flex-col-reverse lg:flex-row items-center justify-between max-w-7xl mx-auto w-full px-6 sm:px-10 gap-12 py-12 lg:py-20 overflow-hidden">
      
      {/* Left Content */}
      <motion.div 
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="flex flex-col items-center lg:items-start text-center lg:text-left space-y-6 mt-5"
      >
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="bg-gradient-to-r from-sage-600 to-sage-800 bg-clip-text text-transparent font-extrabold text-4xl sm:text-5xl lg:text-6xl leading-tight"
        >
          Create the <br className="hidden sm:block" /> Perfect CV in Minutes
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="text-gray-700 max-w-md text-base sm:text-lg leading-relaxed dark:text-gray-100"
        >
          Build <span className="font-semibold text-sage-600">professional, ATS-friendly</span> resumes in minutes. 
          Stand out, impress recruiters, and land your dream job effortlessly.
        </motion.p>
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="flex flex-wrap gap-4 mt-4 justify-center lg:justify-start"
        >
          <Link
            to="/register"
            className="bg-sage-600 text-white px-8 py-3 rounded-full text-sm sm:text-base font-medium shadow-lg hover:bg-sage-700 hover:shadow-xl transition transform hover:-translate-y-1"
          >
            🚀 Get Started
          </Link>
          <Link
            to="/login"
            className="bg-white border border-sage-600 text-sage-600 px-8 py-3 rounded-full text-sm sm:text-base font-medium shadow hover:shadow-md hover:bg-sage-50 transition transform hover:-translate-y-1"
          >
            🔑 Login
          </Link>
        </motion.div>
      </motion.div>

      {/* Right Image */}
      <motion.div 
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="w-full lg:w-1/2 flex justify-center mt-5"
      >
        <div className="relative">
          <motion.img
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.5 }}
            className="rounded-3xl shadow-2xl max-h-[450px] object-cover"
            src={heroImage}
            alt="PerfectCV Hero Image"
          />
          <div className="absolute inset-0 bg-gradient-to-tr from-sage-600/20 via-sage-400/20 to-transparent rounded-3xl pointer-events-none"></div>
        </div>
      </motion.div>
    </main>
  );
}
