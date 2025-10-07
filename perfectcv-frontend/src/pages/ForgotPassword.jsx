// src/pages/ForgotPassword.jsx
import React, { useState } from "react";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [flashMessage, setFlashMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:5000/api/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      if (data.status === "success") {
        setFlashMessage({ type: "success", message: data.message });
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
        <h2 className="text-2xl font-bold text-indigo-600 mb-4">Forgot Password</h2>
        <p className="text-gray-500 mb-4">
          Enter your email and we’ll send you a reset link.
        </p>

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
          type="email"
          placeholder="Email"
          className="border w-full p-2 rounded mb-4 outline-none focus:ring-2 focus:ring-indigo-500"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <button
          type="submit"
          className="bg-indigo-500 text-white w-full py-2 rounded hover:opacity-90 transition-opacity"
        >
          Send Reset Link
        </button>
      </form>
    </div>
  );
}

export default ForgotPassword;
