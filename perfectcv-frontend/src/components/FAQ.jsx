import React, { useState } from "react";

const faqs = [
  { q: "Is PerfectCV free to use?", a: "Yes! You can create and download basic resumes for free. Premium features are optional." },
  { q: "Can I edit my CV after generating it?", a: "Absolutely. You can modify, re-upload, and improve your resume anytime." },
  { q: "Is my data safe?", a: "Your data is securely stored and never shared with third parties." },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <section id="faq" className="fade-in mt-20 px-6 sm:px-10 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 text-center mb-10">
        Frequently Asked <span className="text-indigo-600">Questions</span>
      </h2>

      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <div
            key={i}
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            className="cursor-pointer bg-white dark:bg-gray-800 rounded-lg shadow p-4"
          >
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex justify-between items-center">
              {faq.q}
              <span className="text-indigo-600">{openIndex === i ? "−" : "+"}</span>
            </h3>
            {openIndex === i && (
              <p className="text-gray-600 dark:text-gray-300 mt-2">{faq.a}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
