import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

function ResetPassword() {
  const { token } = useParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [flashMessage, setFlashMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch(`http://127.0.0.1:5000/reset_password/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password, confirm_password: confirmPassword }),
      });

      const data = await res.json();

      if (data.success) {
        setFlashMessage({ type: "success", message: data.message });
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setFlashMessage({
          type: "danger",
          message: data.message || "Invalid link or error.",
        });
      }
    } catch (error) {
      setFlashMessage({ type: "danger", message: "Server error." });
    }
  };

  return (
    <div className="bg-gray-100 dark:bg-gray-900 flex items-center justify-center min-h-screen transition-colors duration-300">
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md w-96 flex flex-col transition-colors duration-300"
      >
        <h2 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mb-4">
          Reset Password
        </h2>

        {flashMessage && (
          <div
            className={`mb-4 p-2 rounded text-sm ${
              flashMessage.type === "success"
                ? "text-blue-700 bg-blue-100 dark:text-blue-300 dark:bg-blue-900"
                : "text-red-700 bg-red-100 dark:text-red-300 dark:bg-red-900"
            }`}
          >
            {flashMessage.message}
          </div>
        )}

        <input
          type="password"
          placeholder="New Password"
          className="border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 w-full p-2 rounded mb-4 outline-none focus:ring-2 focus:ring-indigo-500 transition-colors duration-300"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Confirm Password"
          className="border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 w-full p-2 rounded mb-4 outline-none focus:ring-2 focus:ring-indigo-500 transition-colors duration-300"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-500 text-white w-full py-2 rounded transition-colors duration-300"
        >
          Reset Password
        </button>
      </form>
    </div>
  );
}

export default ResetPassword;
