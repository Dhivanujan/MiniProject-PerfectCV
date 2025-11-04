import React, { useState, useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";

function ResetPassword() {
  const { token } = useParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [flashMessage, setFlashMessage] = useState(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    return () => clearTimeout(timeoutRef.current);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setFlashMessage({ type: "danger", message: "Passwords do not match." });
      return;
    }

    try {
      const res = await api.post(
        "/auth/reset-password",
        { reset_token: token, password, confirm_password: confirmPassword },
        { validateStatus: () => true }
      );

      const data = res.data || {};

      if (res.status >= 200 && res.status < 300 && data.success) {
        setFlashMessage({
          type: "success",
          message: data.message || "Password reset successful!",
        });
        timeoutRef.current = setTimeout(() => navigate("/login"), 2000);
      } else {
        setFlashMessage({
          type: "danger",
          message: data.message || data.error || "Invalid link or error.",
        });
      }
    } catch (error) {
      setFlashMessage({ type: "danger", message: "Server error." });
    }

    timeoutRef.current = setTimeout(() => setFlashMessage(null), 4000);
  };

  return (
    <div className="bg-gray-100 dark:bg-gray-900 flex items-center justify-center min-h-screen transition-colors duration-300">
      <form
        onSubmit={handleSubmit}
        className="bg-white/90 dark:bg-gray-800/80 backdrop-blur-md p-8 rounded-3xl shadow-lg w-96 flex flex-col"
      >
        <h2 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-4 text-center">
          Reset Password
        </h2>

        {flashMessage && (
          <div
            className={`mb-4 p-3 rounded text-sm text-center font-medium ${
              flashMessage.type === "success"
                ? "text-blue-800 bg-blue-100 dark:text-blue-300 dark:bg-blue-900"
                : "text-red-800 bg-red-100 dark:text-red-300 dark:bg-red-900"
            }`}
          >
            {flashMessage.message}
          </div>
        )}

        <label
          htmlFor="password"
          className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1"
        >
          New Password
        </label>
        <input
          type="password"
          id="password"
          placeholder="New Password"
          className="border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 w-full p-3 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <label
          htmlFor="confirmPassword"
          className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1"
        >
          Confirm Password
        </label>
        <input
          type="password"
          id="confirmPassword"
          placeholder="Confirm Password"
          className="border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 w-full p-3 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-500 text-white w-full py-2 rounded transition-all duration-300 font-semibold"
        >
          Reset Password
        </button>

        <div className="mt-4 text-sm text-gray-500 dark:text-gray-400 text-center">
          Remember your password?{" "}
          <a
            href="/login"
            className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline"
          >
            Login
          </a>
        </div>
      </form>
    </div>
  );
}

export default ResetPassword;
