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
        How It <span className="text-sage-600 dark:text-sage-400">Works</span>
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
                       border border-transparent shadow-sm
                       hover:border-sage-400 hover:shadow-md hover:shadow-sage-200/40 
                       dark:hover:shadow-sage-900/40
                       transition-all duration-300"
          >
            <div className="mb-4 flex justify-center">
              <div
                className="text-4xl text-sage-600 p-4 rounded-full 
                           transition-all duration-300 
                           group-hover:bg-sage-50 dark:group-hover:bg-sage-900/30 
                           group-hover:shadow-md group-hover:shadow-sage-200/30"
              >
                {step.icon}
              </div>
            </div>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-2 transition-colors duration-300 group-hover:text-sage-600 dark:group-hover:text-sage-400">
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
