import React from "react";

function CTA() {
  return (
    <section className="fade-in mt-20 mb-10 text-center">
      <h2 className="text-xl font-semibold text-gray-900 mb-4 dark:text-gray-100">
        Ready to make your perfect CV?
      </h2>
      <a
        href="/register"
        className="bg-indigo-600 text-white px-8 py-3 rounded-full text-sm font-medium hover:bg-indigo-700 transition"
      >
        Get Started
      </a>
    </section>
  );
}

export default CTA;
