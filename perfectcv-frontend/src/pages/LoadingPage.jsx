// src/components/LoadingPage.jsx
import React from "react";
import { motion } from "framer-motion";
import { FaSpinner } from "react-icons/fa";

export default function LoadingPage() {
  return (
    <div className="relative flex flex-col items-center justify-center h-screen overflow-hidden bg-gradient-to-br from-indigo-100 via-white to-purple-100 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      
      {/* Floating Gradient Blobs */}
      <motion.div
        className="absolute w-96 h-96 bg-gradient-to-r from-indigo-400 via-purple-500 to-pink-500 rounded-full blur-3xl opacity-20"
        animate={{
          x: [0, 50, -50, 0],
          y: [0, 30, -30, 0],
          scale: [1, 1.1, 0.9, 1],
        }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-80 h-80 bg-gradient-to-br from-blue-300 via-indigo-400 to-purple-500 rounded-full blur-3xl opacity-10 top-10 right-10"
        animate={{
          x: [0, -30, 30, 0],
          y: [0, -20, 20, 0],
          scale: [1, 1.05, 0.95, 1],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Glassmorphism Card */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="relative z-10 backdrop-blur-xl bg-white/30 dark:bg-gray-800/40 border border-white/20 dark:border-gray-700/30 rounded-2xl shadow-2xl p-10 text-center max-w-md mx-auto"
      >
        {/* Animated Spinner */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
          className="inline-block mb-6"
        >
          <FaSpinner className="text-6xl text-indigo-600 dark:text-indigo-400 drop-shadow-lg" />
        </motion.div>

        {/* Text Content */}
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-3xl font-bold text-gray-900 dark:text-gray-100"
        >
          Setting Things Up
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-3 text-gray-600 dark:text-gray-400 text-lg"
        >
          We're preparing your personalized experience. Please hold on a moment.
        </motion.p>

        {/* Animated Progress Glow */}
        <motion.div
          className="mt-6 h-1.5 w-48 mx-auto rounded-full bg-indigo-200 dark:bg-indigo-800 overflow-hidden"
        >
          <motion.div
            className="h-full w-1/3 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"
            animate={{ x: ["-100%", "150%"] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
          />
        </motion.div>
      </motion.div>

      {/* Soft Bottom Glow */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.4 }}
        transition={{ duration: 2 }}
        className="absolute bottom-0 w-full h-40 bg-gradient-to-t from-indigo-400/30 to-transparent dark:from-indigo-700/30"
      />
    </div>
  );
}
