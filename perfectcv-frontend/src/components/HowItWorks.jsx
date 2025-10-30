// src/components/HowItWorks.jsx
import React from "react";
import { motion } from "framer-motion";
import { FaUpload, FaBrain, FaDownload } from "react-icons/fa";

const steps = [
  {
    icon: <FaUpload />,
    title: "Upload or Enter Details",
    desc: "Start by entering your experience or uploading an existing resume.",
  },
  {
    icon: <FaBrain />,
    title: "AI Improves Your Resume",
    desc: "Our AI analyzes your CV and provides intelligent content and format suggestions.",
  },
  {
    icon: <FaDownload />,
    title: "Download Your Perfect CV",
    desc: "Instantly download your ATS-optimized resume in PDF format.",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="fade-in mt-20 px-6 sm:px-10 max-w-6xl mx-auto text-center"
    >
      <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-10">
        How It <span className="text-indigo-600">Works</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{
              delay: i * 0.1,
              duration: 0.4,
              ease: "easeOut",
            }}
            whileHover={{
              scale: 1.05,
              y: -3,
              boxShadow: "0 8px 25px rgba(99, 102, 241, 0.25)",
              transition: { duration: 0.15, ease: "easeInOut" },
            }}
            className="group p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md cursor-pointer border border-transparent hover:border-indigo-500 transition-all duration-150"
          >
            <div className="text-4xl text-indigo-600 mb-4 flex justify-center transition-all duration-150 group-hover:text-indigo-500 group-hover:drop-shadow-[0_0_8px_rgba(99,102,241,0.6)]">
              {step.icon}
            </div>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-2 group-hover:text-indigo-600 transition-colors duration-150">
              {step.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors duration-150">
              {step.desc}
            </p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
