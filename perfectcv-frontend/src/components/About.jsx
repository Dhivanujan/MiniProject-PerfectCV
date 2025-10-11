import React from "react";

function About() {
  return (
    <section
      id="about"
      className="fade-in mt-20 px-6 sm:px-10 max-w-6xl mx-auto transition-colors duration-500"
    >
      <div className="text-center">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-6">
          About <span className="text-indigo-600 dark:text-indigo-400">PerfectCV</span>
        </h2>
        <p className="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed text-base sm:text-lg">
          <span className="font-semibold text-indigo-600 dark:text-indigo-400">
            PerfectCV
          </span>{" "}
          is an AI-powered resume builder designed to help job seekers create
          professional, ATS-friendly resumes in just minutes. Whether you are a
          student, fresher, or experienced professional, our platform gives you
          personalized suggestions, modern templates, and instant formatting
          guidance to ensure your CV stands out to recruiters.
          <br />
          <br />
          Additionally, our{" "}
          <span className="font-semibold text-indigo-600 dark:text-indigo-400">
            AI Chatbot
          </span>{" "}
          feature allows users to get real-time guidance, tips, and feedback on
          their CVs, making the resume-building process interactive, intelligent,
          and highly personalized.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-12">
        <AboutCard
          title="🎯 Tailored for You"
          desc="Get content suggestions customized to your skills, experience, and career goals."
        />
        <AboutCard
          title="⚡ Easy & Fast"
          desc="Build a polished CV within minutes, no design skills required."
        />
        <AboutCard
          title="🌍 Career-Ready"
          desc="Download and share your CV in professional PDF format that recruiters love."
        />
        <AboutCard
          title="🤖 AI Chatbot Support"
          desc="Interact with our AI chatbot to get real-time feedback, resume tips, and personalized guidance."
        />
      </div>
    </section>
  );
}

function AboutCard({ title, desc }) {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow hover:shadow-lg transition-colors duration-500">
      <h3 className="font-semibold text-lg mb-3 text-indigo-600 dark:text-indigo-400">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-300 text-sm">{desc}</p>
    </div>
  );
}

export default About;
