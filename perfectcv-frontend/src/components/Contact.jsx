// src/components/Contact.jsx
import React, { useState } from "react";
import { motion } from "framer-motion";
import { FaEnvelope, FaPhoneAlt, FaMapMarkerAlt } from "react-icons/fa";

export default function Contact() {
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [status, setStatus] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setStatus(data.status || "✅ Message sent successfully!");
      setFormData({ name: "", email: "", message: "" });
    } catch (error) {
      setStatus("❌ Error sending message. Please try again.");
    }
  };

  return (
    <section
      id="contact"
      className="mt-24 px-6 sm:px-10 max-w-6xl mx-auto scroll-mt-20"
    >
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
        className="text-center mb-12"
      >
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100">
          Contact Us
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mt-4 max-w-2xl mx-auto">
          Have questions or need support? Our team at <span className="font-semibold">PerfectCV</span> is ready to help you build your perfect resume.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Contact Form */}
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="bg-white/80 dark:bg-gray-800/70 backdrop-blur-lg p-8 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 space-y-5"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Your Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Enter your name"
              className="w-full border border-gray-300 dark:border-gray-600 bg-transparent rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Your Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="example@domain.com"
              className="w-full border border-gray-300 dark:border-gray-600 bg-transparent rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Message
            </label>
            <textarea
              name="message"
              rows="4"
              value={formData.message}
              onChange={handleChange}
              required
              placeholder="Type your message here..."
              className="w-full border border-gray-300 dark:border-gray-600 bg-transparent rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            ></textarea>
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-md"
          >
            Send Message
          </button>

          {status && (
            <p className="text-center text-sm mt-3 text-gray-700 dark:text-gray-300">
              {status}
            </p>
          )}
        </motion.form>

        {/* Contact Info */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="flex flex-col justify-center space-y-6 md:pl-6"
        >
          <ContactInfo
            icon={<FaEnvelope className="text-indigo-500 text-2xl" />}
            title="Email"
            info="support@perfectcv.com"
          />
          <ContactInfo
            icon={<FaPhoneAlt className="text-indigo-500 text-2xl" />}
            title="Phone"
            info="+94 77 123 4567"
          />
          <ContactInfo
            icon={<FaMapMarkerAlt className="text-indigo-500 text-2xl" />}
            title="Address"
            info="Colombo, Sri Lanka"
          />

          <div className="mt-6">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg mb-2">
              Office Hours
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Monday – Friday: 9:00 AM – 6:00 PM
              <br />
              Saturday: 9:00 AM – 1:00 PM
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function ContactInfo({ icon, title, info }) {
  return (
    <div className="flex items-center space-x-4">
      <div>{icon}</div>
      <div>
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg">{title}</h3>
        <p className="text-gray-600 dark:text-gray-400">{info}</p>
      </div>
    </div>
  );
}
