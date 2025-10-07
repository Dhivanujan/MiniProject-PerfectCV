// src/components/HowItWorks.jsx
import React from "react";
import { motion } from "framer-motion";
import { FaUpload, FaBrain, FaDownload } from "react-icons/fa";

const steps = [
  { icon: <FaUpload />, title: "Upload or Enter Details", desc: "Start by entering your experience or uploading an existing resume." },
  { icon: <FaBrain />, title: "AI Improves Your Resume", desc: "Our AI analyzes your CV and provides intelligent content and format suggestions." },
  { icon: <FaDownload />, title: "Download Your Perfect CV", desc: "Instantly download your ATS-optimized resume in PDF format." },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="fade-in mt-20 px-6 sm:px-10 max-w-6xl mx-auto text-center">
      <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-10">
        How It <span className="text-indigo-600">Works</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.2 }}
            className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow hover:shadow-lg"
          >
            <div className="text-4xl text-indigo-600 mb-4 flex justify-center">{step.icon}</div>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-2">{step.title}</h3>
            <p className="text-gray-600 dark:text-gray-400">{step.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
