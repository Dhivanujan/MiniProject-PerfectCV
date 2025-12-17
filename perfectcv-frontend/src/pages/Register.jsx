// src/pages/Register.jsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import LeftImage from "../assets/CV2.jpeg";
import { motion } from "framer-motion";

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
  });

  const [flashMessages, setFlashMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Display flash message
  const showMessage = (type, message) => {
    setFlashMessages([{ type, message }]);
    setTimeout(() => setFlashMessages([]), 3000);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirm_password) {
      showMessage("danger", "Passwords do not match");
      return;
    }

    setIsSubmitting(true);
    try {
      const { confirm_password, ...payload } = formData;
      const { default: api } = await import("../api");

      const res = await api.post("/auth/register", payload, {
        validateStatus: () => true,
      });

      const data = res.data || {};
      if (data.success) {
        showMessage("success", data.message);
        setTimeout(() => navigate("/login"), 1500);
      } else {
        const details = data.details ? ` - ${data.details}` : "";
        showMessage(
          "danger",
          (data.message || "Registration failed") + details
        );
      }
    } catch (err) {
      console.error("Register error:", err);
      showMessage("danger", "Server error. Please try again later.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputFields = [
    { name: "full_name", placeholder: "Full Name", type: "text" },
    { name: "username", placeholder: "Username", type: "text" },
    { name: "email", placeholder: "Email Address", type: "email" },
    { name: "phone", placeholder: "Phone Number", type: "text" },
    { name: "password", placeholder: "Password", type: "password" },
    { name: "confirm_password", placeholder: "Confirm Password", type: "password" },
  ];

  return (
    <div
      className="flex h-screen w-full
      bg-gradient-to-br from-[#F5F7FF] via-[#FFFBEA] to-[#E6EFFF]
      dark:from-[#0D1117] dark:via-[#161B22] dark:to-[#1E2329]
      transition-colors duration-500"
    >
      {/* Left Section - Form */}
      <div className="flex w-full md:w-1/2 justify-center items-center px-6 md:px-12">
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-full max-w-md bg-white dark:bg-[#1E1E2F]
          rounded-2xl shadow-lg hover:shadow-2xl transition-all
          p-8 flex flex-col items-center"
        >
          <h2 className="text-4xl font-extrabold text-sage-600 dark:text-sage-400">
            Create Account
          </h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-3 mb-6 text-center">
            Join <span className="font-semibold text-sage-500">PerfectCV</span> and start crafting your perfect resume.
          </p>

          {/* Flash Messages */}
          {flashMessages.length > 0 && (
            <div className="flex flex-col w-full mb-4 gap-2">
              {flashMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex justify-between items-center px-4 py-2 rounded-md text-sm
                    ${
                      msg.type === "success"
                        ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100"
                        : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100"
                    }`}
                >
                  <span>{msg.message}</span>
                  <button
                    type="button"
                    className="font-bold hover:scale-110 transition-transform"
                    onClick={() => setFlashMessages([])}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Input Fields */}
          {inputFields.map(({ name, placeholder, type }) => (
            <div
              key={name}
              className="w-full mt-3 h-12 border border-gray-300 dark:border-gray-600 
              rounded-full flex items-center px-5 transition-all 
              focus-within:ring-2 focus-within:ring-sage-400 dark:focus-within:ring-sage-500"
            >
              <input
                type={type}
                name={name}
                placeholder={placeholder}
                value={formData[name]}
                onChange={handleChange}
                required
                className="w-full bg-transparent outline-none text-gray-700 dark:text-gray-200 
                placeholder-gray-400 dark:placeholder-gray-500 text-sm"
              />
            </div>
          ))}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className={`mt-8 w-full h-11 rounded-full font-semibold text-white transition-all 
              ${
                isSubmitting
                  ? "bg-sage-300 cursor-not-allowed"
                  : "bg-sage-500 hover:bg-sage-600 dark:bg-sage-600 dark:hover:bg-sage-700"
              }`}
          >
            {isSubmitting ? "Creating Account..." : "Sign Up"}
          </button>

          {/* Footer Text */}
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-5">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-sage-500 dark:text-sage-400 hover:underline font-medium"
            >
              Log In
            </Link>
          </p>
        </motion.form>
      </div>

      {/* Right Section - Animated Image */}
      <motion.div
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="hidden md:block w-1/2"
            >
              <img
                src={LeftImage}
                alt="Registration Illustration"
                className="h-full w-full object-cover"
              />
            </motion.div>
    </div>
  );
}

export default Register;
