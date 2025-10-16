import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import LeftImage from "../assets/CV.png";
import api from "../api"; // use your Axios instance

function Login({ setUser }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: false,
  });
  const [flashMessages, setFlashMessages] = useState([]);
  
  // Forgot password states
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotLoading, setForgotLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const res = await api.post("/api/login", formData, {
      // 👇 This ensures Axios won't throw for non-2xx responses
      validateStatus: () => true,
    });

    const data = res.data;

    if (res.status >= 200 && res.status < 300 && data.success) {
      // ✅ Login success
      setFlashMessages([{ type: "success", message: data.message }]);
      setUser(data.user);
      setTimeout(() => navigate("/dashboard"), 500);
    } else {
      // ⚠️ Backend returned an error (e.g., wrong password)
      setFlashMessages([
        { type: "danger", message: data.message || "Login failed" },
      ]);
    }
  } catch (error) {
    // 🚨 Network or server crash (no response)
    console.error("Login error:", error);
    const message =
      error.response?.data?.message ||
      "Unable to connect to the server. Please try again later.";
    setFlashMessages([{ type: "danger", message }]);
  } finally {
    // ⏳ Auto-hide flash messages after 3 seconds
    setTimeout(() => setFlashMessages([]), 3000);
  }
};

  // Forgot password handler
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setForgotLoading(true);

    try {
      const res = await api.post("/api/forgot-password", { email: forgotEmail }, {
        validateStatus: () => true,
      });

      const data = res.data;

      if (data.status === "success") {
        setFlashMessages([{ type: "success", message: data.message }]);
        setShowForgotModal(false);
        setForgotEmail("");
      } else {
        setFlashMessages([{ type: "danger", message: data.message }]);
      }
    } catch (error) {
      console.error("Forgot password error:", error);
      const message =
        error.response?.data?.message ||
        "Unable to connect to the server. Please try again later.";
      setFlashMessages([{ type: "danger", message }]);
    } finally {
      setForgotLoading(false);
      setTimeout(() => setFlashMessages([]), 3000);
    }
  };

  // Open forgot password modal and pre-fill with login email if available
  const openForgotModal = () => {
    setForgotEmail(formData.email);
    setShowForgotModal(true);
  };

  return (
    <div
      className="flex h-screen w-full 
      bg-gradient-to-b from-[#F5F7FF] via-[#FFFBEA] to-[#E6EFFF]
      dark:from-[#0D1117] dark:via-[#161B22] dark:to-[#1E2329]
      transition-colors duration-500"
    >
      {/* Left Side Image (Hidden on Mobile) */}
      <div className="w-full hidden md:inline-block">
        <img
          className="h-full w-full object-cover"
          src={LeftImage}
          alt="leftSideImage"
        />
      </div>

      {/* Right Side Form */}
      <div className="w-full flex flex-col items-center justify-center">
        <form
          onSubmit={handleSubmit}
          className="md:w-96 w-80 flex flex-col items-center justify-center
          bg-white dark:bg-[#1E1E2F] p-8 rounded-xl shadow-lg
          transition-all duration-500"
        >
          <h1 className="text-4xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">
            PerfectCV
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mb-6 text-center">
            Sign in to enhance your CV and unlock your potential
          </p>

          {/* Flash Messages */}
          {flashMessages.length > 0 &&
            flashMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`w-full mb-4 px-2 py-1 rounded text-sm ${
                  msg.type === "success"
                    ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100"
                    : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100"
                }`}
              >
                {msg.message}
              </div>
            ))}

          {/* Inputs */}
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email"
            required
            className="w-full h-12 px-4 mb-4 border border-gray-300 dark:border-gray-600
            rounded-full outline-none bg-white dark:bg-[#2A2A3D] 
            text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500
            focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-600 transition-all"
          />

          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Password"
            required
            className="w-full h-12 px-4 mb-4 border border-gray-300 dark:border-gray-600
            rounded-full outline-none bg-white dark:bg-[#2A2A3D]
            text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500
            focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-600 transition-all"
          />

          {/* Remember & Forgot */}
          <div className="w-full flex items-center justify-between mb-4 text-gray-600 dark:text-gray-400">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                name="remember"
                checked={formData.remember}
                onChange={handleChange}
              />
              Remember me
            </label>
            <button
              type="button"
              onClick={openForgotModal}
              className="text-sm underline hover:text-indigo-500 dark:hover:text-indigo-400 bg-transparent border-none"
            >
              Forgot password?
            </button>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="w-full h-12 bg-indigo-500 hover:bg-indigo-600 text-white 
            dark:bg-indigo-600 dark:hover:bg-indigo-700
            rounded-full font-semibold transition-all"
          >
            Login
          </button>

          <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            Don’t have an account?{" "}
            <a
              href="/register"
              className="text-indigo-500 dark:text-indigo-400 hover:underline"
            >
              Sign up
            </a>
          </p>
        </form>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Reset Password
              </h2>
              <button
                type="button"
                onClick={() => setShowForgotModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleForgotPassword}>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Enter your email address and we'll send you a link to reset your password.
              </p>
              
              <div className="mb-4">
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 
                    rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 
                    dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowForgotModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 
                    text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 
                    dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="flex-1 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 
                    text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {forgotLoading ? "Sending..." : "Send Reset Link"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Login;
