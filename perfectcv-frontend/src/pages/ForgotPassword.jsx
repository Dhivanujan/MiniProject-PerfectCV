import React, { useState } from "react";
import forgotIllustration from "../assets/forgot-illustration.jpeg"; // Replace with your SVG

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [flashMessage, setFlashMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:5000/forgot_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          frontend_url: "http://localhost:3000/reset-password",
        }),
      });

      const data = await res.json();

      if (data.success) {
        setFlashMessage({ type: "success", message: data.message });
      } else {
        setFlashMessage({
          type: "danger",
          message: data.message || "Failed to send reset link.",
        });
      }
    } catch (error) {
      setFlashMessage({ type: "danger", message: "Server error." });
    }

    setTimeout(() => setFlashMessage(null), 4000);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-gray-900 dark:to-gray-800 p-4 overflow-hidden">
      {/* Animated Floating Circles with hover glow */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute w-32 h-32 bg-indigo-300/30 rounded-full animate-float hover:scale-110 hover:bg-indigo-400/50 hover:shadow-lg transition-all duration-500"></div>
        <div className="absolute w-48 h-48 bg-purple-300/30 rounded-full animate-float2 hover:scale-105 hover:bg-purple-400/50 hover:shadow-xl transition-all duration-500"></div>
        <div className="absolute w-24 h-24 bg-indigo-400/20 rounded-full animate-float3 hover:scale-125 hover:bg-indigo-500/40 hover:shadow-md transition-all duration-500"></div>
      </div>

      <div className="flex flex-col md:flex-row items-center md:justify-center w-full max-w-5xl gap-10 relative z-10">
        {/* Illustration */}
        <div className="w-full md:w-1/2 flex justify-center mb-8 md:mb-0">
          <img
            src={forgotIllustration}
            alt="Forgot password illustration"
            className="w-72 md:w-full animate-fadeIn"
          />
        </div>

        {/* Glassmorphism Form Card */}
        <form
          onSubmit={handleSubmit}
          className="w-full md:w-1/2 bg-white/30 dark:bg-gray-800/30 backdrop-blur-md rounded-3xl p-8 md:p-10 shadow-2xl flex flex-col transition-all duration-500 hover:scale-105"
        >
          <h2 className="text-3xl md:text-4xl font-extrabold text-indigo-600 dark:text-indigo-400 mb-3 text-center">
            Forgot Password
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-6 text-center text-sm md:text-base">
            Enter your email address and we’ll send you a secure reset link.
          </p>

          {/* Flash Message */}
          {flashMessage && (
            <div
              className={`mb-6 p-3 rounded text-sm font-medium transition-colors duration-300 text-center ${
                flashMessage.type === "success"
                  ? "text-blue-800 bg-blue-100 dark:text-blue-300 dark:bg-blue-900"
                  : "text-red-800 bg-red-100 dark:text-red-300 dark:bg-red-900"
              }`}
            >
              {flashMessage.message}
            </div>
          )}

          <div className="mb-6 text-left">
            <label
              htmlFor="email"
              className="block mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              placeholder="you@example.com"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/70 dark:bg-gray-700/70 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white font-semibold shadow-lg transition-all duration-300"
          >
            Send Reset Link
          </button>

          <div className="mt-6 text-sm md:text-base text-gray-500 dark:text-gray-400 text-center">
            Remembered your password?{" "}
            <a
              href="/login"
              className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline"
            >
              Login
            </a>
          </div>
        </form>
      </div>

      {/* Animations using Tailwind + Custom CSS */}
      <style>
        {`
          .animate-float {
            top: -10%;
            left: -10%;
            animation: float 15s ease-in-out infinite;
          }
          .animate-float2 {
            top: 20%;
            right: -20%;
            animation: float 20s ease-in-out infinite;
          }
          .animate-float3 {
            bottom: -10%;
            left: 30%;
            animation: float 18s ease-in-out infinite;
          }
          @keyframes float {
            0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.3; }
            50% { transform: translateY(-30px) translateX(30px); opacity: 0.5; }
          }
          .animate-fadeIn {
            animation: fadeIn 1s ease-in forwards;
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}
      </style>
    </div>
  );
}

export default ForgotPassword;
