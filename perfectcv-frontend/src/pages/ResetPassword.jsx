// src/pages/ResetPassword.jsx
import React, { useState } from "react";
import { useSearchParams } from "react-router-dom"; // To get token from URL

function ResetPassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [flashMessage, setFlashMessage] = useState(null);

  // Get token from query params (e.g., ?token=xyz)
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setFlashMessage({ type: "danger", message: "Passwords do not match" });
      setTimeout(() => setFlashMessage(null), 3000);
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:5000/api/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });

      const data = await res.json();

      if (data.status === "success") {
        setFlashMessage({ type: "success", message: data.message });
        setTimeout(() => {
          window.location.href = "/login";
        }, 1500);
      } else {
        setFlashMessage({ type: "danger", message: data.message });
      }

      setTimeout(() => setFlashMessage(null), 3000);
    } catch (error) {
      setFlashMessage({ type: "danger", message: "Server error" });
      setTimeout(() => setFlashMessage(null), 3000);
    }
  };

  return (
    <div className="bg-gray-100 flex items-center justify-center h-screen">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-lg shadow-md w-96 flex flex-col"
      >
        <h2 className="text-2xl font-bold text-indigo-600 mb-4">Reset Password</h2>
        <p className="text-gray-500 mb-4">Enter your new password.</p>

        {/* Flash Message */}
        {flashMessage && (
          <div
            className={`mb-4 p-2 rounded text-sm ${
              flashMessage.type === "success" ? "text-blue-600 bg-blue-100" : "text-red-600 bg-red-100"
            }`}
          >
            {flashMessage.message}
          </div>
        )}

        <input
          type="password"
          placeholder="New Password"
          className="border w-full p-2 rounded mb-4 outline-none focus:ring-2 focus:ring-indigo-500"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Confirm New Password"
          className="border w-full p-2 rounded mb-4 outline-none focus:ring-2 focus:ring-indigo-500"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="bg-indigo-500 text-white w-full py-2 rounded hover:opacity-90 transition-opacity"
        >
          Reset Password
        </button>
      </form>
    </div>
  );
}

export default ResetPassword;
