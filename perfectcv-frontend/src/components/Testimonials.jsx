// src/components/Testimonials.jsx
import React from "react";
import { motion } from "framer-motion";

const testimonials = [
  {
    name: "Supuni Perera",
    role: "Software Engineer",
    text: "PerfectCV helped me create a professional resume that landed me interviews at top companies!",
  },
  {
    name: "Tharindu Perera",
    role: "Marketing Specialist",
    text: "The AI feedback was so accurate—it made my CV concise and impactful.",
  },
  {
    name: "Ishara Silva",
    role: "Fresh Graduate",
    text: "As a fresher, I had no idea where to start. PerfectCV made the process stress-free!",
  },
];

export default function Testimonials() {
  return (
    <section
      id="testimonials"
      className="fade-in mt-20 px-6 sm:px-10 max-w-6xl mx-auto text-center"
    >
      <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-10">
        What Our <span className="text-indigo-600 dark:text-indigo-400">Users Say</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {testimonials.map((t, i) => (
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
            className="group bg-white dark:bg-gray-800 rounded-xl border border-transparent 
                       shadow-sm hover:border-indigo-400 hover:shadow-md hover:shadow-indigo-200/40 
                       dark:hover:shadow-indigo-900/40 p-6 transition-all duration-300"
          >
            <p className="text-gray-600 dark:text-gray-300 italic mb-4 leading-relaxed">
              “{t.text}”
            </p>
            <h4 className="font-semibold text-indigo-600 dark:text-indigo-400 transition-colors duration-300">
              {t.name}
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">{t.role}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
