import React from "react";
import { motion } from "framer-motion";

function CTA() {
  return (
    <motion.section 
      initial={{ opacity: 0, scale: 0.9 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="mt-20 mb-10 text-center px-6"
    >
      <div className="bg-gradient-to-r from-sage-600 to-sage-800 rounded-2xl p-10 sm:p-16 shadow-2xl max-w-5xl mx-auto text-white">
        <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-6">
          Ready to make your perfect CV?
        </h2>
        <p className="text-sage-100 mb-8 max-w-2xl mx-auto text-lg">
          Join thousands of job seekers who have successfully landed their dream jobs with PerfectCV.
        </p>
        <motion.a
          href="/register"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="inline-block bg-white text-sage-700 px-8 py-4 rounded-full text-base font-bold shadow-lg hover:shadow-xl transition-all"
        >
          Get Started Now
        </motion.a>
      </div>
    </motion.section>
  );
}

export default CTA;
