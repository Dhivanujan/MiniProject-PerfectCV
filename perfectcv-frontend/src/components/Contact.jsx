// src/components/Contact.jsx
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaEnvelope, FaPhoneAlt, FaMapMarkerAlt } from "react-icons/fa";
import api from "../api";

export default function Contact() {
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  // alert: { type: 'success' | 'danger', message: string }
  const [alert, setAlert] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAlert(null);
    try {
      const response = await api.post("/api/contact", formData);
      
      if (response.data.status === 'ok' || response.data.saved) {
        setAlert({ type: "success", message: "✅ Message sent successfully!" });
        setFormData({ name: "", email: "", message: "" });
      } else {
        setAlert({ type: "danger", message: response.data.message || "❌ Error sending message." });
      }
    } catch (error) {
      console.error("Contact form error:", error);
      const msg = error.response?.data?.message || "❌ Error sending message. Please try again.";
      setAlert({ type: "danger", message: msg });
    }
  };

  // auto-close alert after 4s and cleanup
  useEffect(() => {
    if (!alert) return;
    const t = setTimeout(() => setAlert(null), 4000);
    return () => clearTimeout(t);
  }, [alert]);

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
              className="w-full border border-gray-300 dark:border-gray-600 bg-transparent rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-sage-500"
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
              className="w-full border border-gray-300 dark:border-gray-600 bg-transparent rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-sage-500"
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
              className="w-full border border-gray-300 dark:border-gray-600 bg-transparent rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-sage-500"
            ></textarea>
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-sage-600 to-sage-800 text-white py-2 px-4 rounded-lg font-medium hover:from-sage-700 hover:to-sage-900 transition-all duration-300 shadow-md"
          >
            Send Message
          </button>

          {alert && (
            <div
              role="alert"
              className={`mt-3 p-3 rounded text-sm text-center font-medium transition-colors duration-300 ${
                alert.type === "success"
                  ? "text-sage-800 bg-sage-100 dark:text-sage-300 dark:bg-sage-900"
                  : "text-red-800 bg-red-100 dark:text-red-300 dark:bg-red-900"
              } relative`}
            >
              <span>{alert.message}</span>
              <button
                type="button"
                aria-label="close"
                onClick={() => setAlert(null)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-sm font-semibold opacity-80 hover:opacity-100"
              >
                ✕
              </button>
            </div>
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
            icon={<FaEnvelope className="text-sage-500 text-2xl" />}
            title="Email"
            info="support@perfectcv.com"
          />
          <ContactInfo
            icon={<FaPhoneAlt className="text-sage-500 text-2xl" />}
            title="Phone"
            info="+94 77 123 4567"
          />
          <ContactInfo
            icon={<FaMapMarkerAlt className="text-sage-500 text-2xl" />}
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
