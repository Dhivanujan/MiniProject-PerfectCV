// LoadingPage.jsx
import React from "react";
import { motion } from "framer-motion";
import { FaSpinner } from "react-icons/fa";

export default function LoadingPage() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-indigo-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 overflow-hidden">
      
      {/* Animated Gradient Orb */}
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 0.2, scale: [1, 1.1, 1] }}
        transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
        className="absolute w-96 h-96 bg-gradient-to-r from-indigo-400 to-purple-500 rounded-full blur-3xl opacity-30"
      ></motion.div>

      {/* Spinner + Text Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative z-10 text-center px-6"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
          className="inline-block"
        >
          <FaSpinner className="text-indigo-600 dark:text-indigo-400 text-6xl mb-6" />
        </motion.div>

        <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 tracking-tight">
          Preparing Your Experience
        </h2>
        <p className="text-gray-500 dark:text-gray-400 mt-3 text-lg max-w-md mx-auto">
          Sit tight while we set things up for you. This won’t take long!
        </p>
      </motion.div>

      {/* Soft Bottom Glow */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.3 }}
        transition={{ duration: 2, ease: "easeInOut" }}
        className="absolute bottom-0 w-full h-40 bg-gradient-to-t from-indigo-300/30 to-transparent dark:from-indigo-700/30"
      ></motion.div>
    </div>
  );
}
