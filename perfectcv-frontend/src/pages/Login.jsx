import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";
import LeftImage from "../assets/CV2.jpeg";
import api from "../api"; // Your Axios instance

function Login({ setUser }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: false,
  });
  const [flashMessages, setFlashMessages] = useState([]);
  const [showPassword, setShowPassword] = useState(false);

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
      const res = await api.post("/auth/login", formData, {
        validateStatus: () => true,
      });
      const data = res.data;

      if (res.status >= 200 && res.status < 300 && data.success) {
        setFlashMessages([{ type: "success", message: data.message }]);
        if (setUser) setUser(data.user);
        navigate("/dashboard");
      } else {
        setFlashMessages([
          { type: "danger", message: data.error || data.message || "Login failed" },
        ]);
      }
    } catch (error) {
      console.error("Login error:", error);
      const message =
        error.response?.data?.error ||
        error.response?.data?.message ||
        "Unable to connect to the server. Please try again later.";
      setFlashMessages([{ type: "danger", message }]);
    } finally {
      setTimeout(() => {
        setFlashMessages((msgs) => msgs.filter((m) => m.type !== "danger"));
      }, 3000);
    }
  };

  const handleForgotPassword = () => navigate("/forgot-password");

  return (
    <div
      className="flex h-screen w-full 
      bg-gradient-to-b from-[#F8FAFF] via-[#FDFCFB] to-[#EFF3FF]
      dark:from-[#0D1117] dark:via-[#161B22] dark:to-[#1E2329]
      transition-colors duration-500"
    >
      {/* Left Image Section */}
      <motion.div
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8 }}
        className="hidden md:block w-1/2"
      >
        <img
          src={LeftImage}
          alt="Login Illustration"
          className="h-full w-full object-cover"
        />
      </motion.div>

      {/* Right Side Form */}
      <div className="w-full md:w-1/2 flex items-center justify-center p-6 md:p-0">
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-11/12 max-w-md flex flex-col items-center justify-center
          bg-white/80 dark:bg-[#181824]/90 backdrop-blur-lg
          p-8 rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.08)]
          hover:shadow-[0_8px_40px_rgba(0,0,0,0.12)]
          transition-all duration-500"
        >
          <h1 className="text-4xl font-extrabold text-indigo-600 dark:text-indigo-400 mb-3 tracking-tight">
            PerfectCV
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6 text-center text-sm">
            Sign in to enhance your resume and unlock your full potential.
          </p>

          {/* Flash Messages */}
          {flashMessages.map((msg, idx) => (
            <div
              key={idx}
              className={`w-full mb-4 px-3 py-2 rounded-lg text-sm text-center font-medium ${
                msg.type === "success"
                  ? "bg-green-100 text-green-700 dark:bg-green-900/60 dark:text-green-100"
                  : "bg-red-100 text-red-700 dark:bg-red-900/60 dark:text-red-100"
              }`}
            >
              {msg.message}
            </div>
          ))}

          {/* Email Input */}
          <label htmlFor="email" className="sr-only">
            Email
          </label>
          <input
            id="email"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email"
            required
            className="w-full h-12 px-5 mb-4 border border-gray-300 dark:border-gray-700
            rounded-full outline-none bg-white/90 dark:bg-[#232338]
            text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500
            focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-600 transition-all"
          />

          {/* Password Input */}
          <div className="w-full relative mb-4">
            <label htmlFor="password" className="sr-only">
              Password
            </label>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Password"
              required
              className="w-full h-12 px-5 pr-10 border border-gray-300 dark:border-gray-700
              rounded-full outline-none bg-white/90 dark:bg-[#232338]
              text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500
              focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-600 transition-all"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-3 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400 transition"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          {/* Remember Me + Forgot Password */}
          <div className="w-full flex items-center justify-between mb-5 text-gray-600 dark:text-gray-400 text-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="remember"
                checked={formData.remember}
                onChange={handleChange}
                className="accent-indigo-500 w-4 h-4"
              />
              Remember me
            </label>
            <button
              type="button"
              onClick={handleForgotPassword}
              className="font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 underline-offset-2 hover:underline transition-colors"
            >
              Forgot password?
            </button>
          </div>

          {/* Login Button */}
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white 
            rounded-full font-semibold tracking-wide transition-all shadow-md hover:shadow-lg"
          >
            Login
          </motion.button>

          {/* Register Link */}
          <p className="mt-5 text-sm text-gray-600 dark:text-gray-400">
            Don’t have an account? {" "}
            <Link to="/register" className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium">
              Sign up
            </Link>
          </p>
        </motion.form>
      </div>
    </div>
  );
}

export default Login;
