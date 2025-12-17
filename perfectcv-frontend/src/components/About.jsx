import React from "react";
import { motion } from "framer-motion";

function About() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <section
      id="about"
      className="mt-20 px-6 sm:px-10 max-w-6xl mx-auto transition-colors duration-500"
    >
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-6">
          About <span className="text-sage-600 dark:text-sage-400">PerfectCV</span>
        </h2>
        <p className="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed text-base sm:text-lg">
          <span className="font-semibold text-sage-600 dark:text-sage-400">
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
          <span className="font-semibold text-sage-600 dark:text-sage-400">
            AI Chatbot
          </span>{" "}
          feature offers real-time feedback, tips, and guidance, making the
          resume-building process simple, interactive, and effective.
        </p>
      </motion.div>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-12"
      >
        <AboutCard
          variants={itemVariants}
          title="🎯 Tailored for You"
          desc="Receive personalized content suggestions based on your skills and goals."
        />
        <AboutCard
          variants={itemVariants}
          title="⚡ Easy & Fast"
          desc="Create a professional CV within minutes — no design experience required."
        />
        <AboutCard
          variants={itemVariants}
          title="🌍 Career-Ready"
          desc="Download and share your CV in recruiter-friendly PDF format instantly."
        />
        <AboutCard
          variants={itemVariants}
          title="🤖 AI Chatbot Support"
          desc="Get real-time insights and advice from our integrated AI assistant."
        />
      </motion.div>
    </section>
  );
}

function AboutCard({ title, desc, variants }) {
  return (
    <motion.div
      variants={variants}
      className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-transparent 
      shadow-sm hover:border-sage-400 hover:shadow-md hover:shadow-sage-200/40 
      transition-all duration-300"
    >
      <h3 className="font-semibold text-lg mb-3 text-sage-600 dark:text-sage-400">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{desc}</p>
    </motion.div>
  );
}

export default About;
