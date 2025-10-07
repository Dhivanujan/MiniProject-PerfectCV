// src/components/Testimonials.jsx
import React from "react";
import { motion } from "framer-motion";

const testimonials = [
  { name: "Ayesha Fernando", role: "Software Engineer", text: "PerfectCV helped me create a professional resume that landed me interviews at top companies!" },
  { name: "Tharindu Perera", role: "Marketing Specialist", text: "The AI feedback was so accurate—it made my CV concise and impactful." },
  { name: "Ishara Silva", role: "Fresh Graduate", text: "As a fresher, I had no idea where to start. PerfectCV made the process stress-free!" },
];

export default function Testimonials() {
  return (
    <section id="testimonials" className="fade-in mt-20 px-6 sm:px-10 max-w-6xl mx-auto text-center">
      <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-10">
        What Our <span className="text-indigo-600">Users Say</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {testimonials.map((t, i) => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.05 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow p-6"
          >
            <p className="text-gray-600 dark:text-gray-300 italic mb-4">“{t.text}”</p>
            <h4 className="font-semibold text-indigo-600">{t.name}</h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">{t.role}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
