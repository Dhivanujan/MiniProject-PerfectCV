import React from "react";

function About() {
  return (
    <section
      id="about"
      className="mt-20 px-6 sm:px-10 max-w-6xl mx-auto transition-colors duration-500"
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
          professional, ATS-friendly resumes with ease. Whether you are a
          student, fresher, or experienced professional, our platform provides
          personalized suggestions, modern templates, and smart formatting
          assistance to help your CV stand out to recruiters.
          <br />
          <br />
          Our{" "}
          <span className="font-semibold text-indigo-600 dark:text-indigo-400">
            AI Chatbot
          </span>{" "}
          feature offers real-time feedback, tips, and guidance, making the
          resume-building process simple, interactive, and effective.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-12">
        <AboutCard
          title="🎯 Tailored for You"
          desc="Receive personalized content suggestions based on your skills and goals."
        />
        <AboutCard
          title="⚡ Easy & Fast"
          desc="Create a professional CV within minutes — no design experience required."
        />
        <AboutCard
          title="🌍 Career-Ready"
          desc="Download and share your CV in recruiter-friendly PDF format instantly."
        />
        <AboutCard
          title="🤖 AI Chatbot Support"
          desc="Get real-time insights and advice from our integrated AI assistant."
        />
      </div>
    </section>
  );
}

function AboutCard({ title, desc }) {
  return (
    <div
      className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-transparent 
      shadow-sm hover:border-indigo-400 hover:shadow-md hover:shadow-indigo-200/40 
      transition-all duration-300"
    >
      <h3 className="font-semibold text-lg mb-3 text-indigo-600 dark:text-indigo-400">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{desc}</p>
    </div>
  );
}

export default About;
