import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const faqs = [
  { q: "Is PerfectCV free to use?", a: "Yes! You can create and download basic resumes for free. Premium features are optional." },
  { q: "Can I edit my CV after generating it?", a: "Absolutely. You can modify, re-upload, and improve your resume anytime." },
  { q: "Is my privacy protected?", a: "Your data is securely stored and never shared with third parties." },
  { q: "How long does it take to optimize my CV?", a: "Usually just a few minutes! Our AI helps you to process your resume instantly and provides you with an optimized version ready to download." },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <section id="faq" className="mt-20 px-6 sm:px-10 max-w-4xl mx-auto">
      <motion.h2 
        initial={{ opacity: 0, y: -20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="text-3xl font-bold text-gray-900 dark:text-gray-100 text-center mb-10"
      >
        Frequently Asked <span className="text-sage-600">Questions</span>
      </motion.h2>

      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.4 }}
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            className="cursor-pointer bg-white dark:bg-gray-800 rounded-lg shadow p-4 overflow-hidden"
          >
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex justify-between items-center">
              {faq.q}
              <motion.span 
                animate={{ rotate: openIndex === i ? 180 : 0 }}
                transition={{ duration: 0.3 }}
                className="text-sage-600"
              >
                {openIndex === i ? "−" : "+"}
              </motion.span>
            </h3>
            <AnimatePresence>
              {openIndex === i && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <p className="text-gray-600 dark:text-gray-300 mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">{faq.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
