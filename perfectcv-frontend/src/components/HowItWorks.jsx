// src/components/HowItWorks.jsx
import React from "react";
import { motion } from "framer-motion";
import { FaUpload, FaBrain, FaDownload } from "react-icons/fa";

const steps = [
  {
    icon: <FaUpload />,
    title: "Upload or Enter Details",
    desc: "Begin by entering your professional details or uploading your existing resume for analysis.",
  },
  {
    icon: <FaBrain />,
    title: "AI Enhances Your Resume",
    desc: "Our advanced AI refines your content and structure, ensuring it’s impactful and ATS-friendly.",
  },
  {
    icon: <FaDownload />,
    title: "Download Your Perfect CV",
    desc: "Instantly export your professionally optimized resume in a clean, ready-to-use PDF format.",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="mt-20 px-6 sm:px-10 max-w-6xl mx-auto text-center"
    >
      <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-12">
        How It <span className="text-indigo-600">Works</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{
              delay: i * 0.1,
              duration: 0.4,
              ease: "easeOut",
            }}
            className="group p-6 bg-white dark:bg-gray-800 rounded-xl 
                       border border-gray-100 dark:border-gray-700 shadow-sm
                       transition-all duration-300 ease-in-out
                       hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-300/40 
                       dark:hover:shadow-indigo-900/40"
          >
            <div className="text-4xl text-indigo-600 mb-4 flex justify-center transition-transform duration-300 group-hover:scale-110">
              {step.icon}
            </div>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-2 group-hover:text-indigo-600 transition-colors duration-300">
              {step.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              {step.desc}
            </p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
