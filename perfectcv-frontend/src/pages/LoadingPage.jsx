// LoadingPage.jsx
import React from "react";
import { motion } from "framer-motion";
import { FaSpinner } from "react-icons/fa";

export default function LoadingPage() {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-900 dark:to-gray-800">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="text-center"
      >
        <FaSpinner className="animate-spin text-indigo-600 dark:text-indigo-400 text-6xl mx-auto mb-6" />
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
          Preparing your experience...
        </h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Please wait while we load everything for you.
        </p>
      </motion.div>
    </div>
  );
}
