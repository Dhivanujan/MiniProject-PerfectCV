import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [flashMessage, setFlashMessage] = useState(null);
  const [step, setStep] = useState("email"); // email -> verify -> reset
  const [resetToken, setResetToken] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      let res;
      
      if (step === "email") {
        // Step 1: Send OTP to email
        res = await api.post("/auth/forgot-password", { email });
        if (res.data.success) {
          setFlashMessage({
            type: "success",
            message: "A 6-digit code has been sent to your email",
          });
          setStep("verify");
        }
      } 
      else if (step === "verify") {
        // Step 2: Verify OTP
        res = await api.post("/auth/verify-reset-code", { email, code });
        if (res.data.success) {
          setResetToken(res.data.reset_token);
          setFlashMessage({
            type: "success",
            message: "Email verified successfully. Please enter your new password.",
          });
          setStep("reset");
        }
      } 
      else if (step === "reset") {
        // Step 3: Reset Password
        if (newPassword !== confirmPassword) {
          setFlashMessage({
            type: "danger",
            message: "Passwords do not match!",
          });
          return;
        }
        if (newPassword.length < 6) {
          setFlashMessage({
            type: "danger",
            message: "Password must be at least 6 characters long",
          });
          return;
        }

        res = await api.post("/auth/reset-password", { 
          reset_token: resetToken,
          password: newPassword
        });

        if (res.data.success) {
          setFlashMessage({
            type: "success",
            message: "Password reset successful! Redirecting to login...",
          });
          setTimeout(() => navigate("/login"), 2000);
        }
      }
    } catch (error) {
      const message = error.response?.data?.error || error.message || "An error occurred";
      setFlashMessage({ type: "danger", message });
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case "email":
        return (
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
              placeholder="Enter your email"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/70 dark:bg-gray-700/70 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        );

      case "verify":
        return (
          <div className="mb-6 text-left">
            <label
              htmlFor="code"
              className="block mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300"
            >
              Enter 6-Digit Code
            </label>
            <input
              type="text"
              id="code"
              placeholder="Enter the code sent to your email"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/70 dark:bg-gray-700/70 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ""))}
              maxLength={6}
              required
            />
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              A 6-digit code has been sent to {email}
            </p>
          </div>
        );

      case "reset":
        return (
          <>
            <div className="mb-6 text-left">
              <label
                htmlFor="newPassword"
                className="block mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300"
              >
                New Password
              </label>
              <input
                type="password"
                id="newPassword"
                placeholder="Enter new password"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/70 dark:bg-gray-700/70 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <div className="mb-6 text-left">
              <label
                htmlFor="confirmPassword"
                className="block mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300"
              >
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                placeholder="Confirm new password"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/70 dark:bg-gray-700/70 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="w-full max-w-md">
        <form
          onSubmit={handleSubmit}
          className="bg-white/30 dark:bg-gray-800/30 backdrop-blur-md rounded-3xl p-8 shadow-2xl"
        >
          <h2 className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 mb-6 text-center">
            {step === "email"
              ? "Forgot Password"
              : step === "verify"
              ? "Verify Email"
              : "Reset Password"}
          </h2>

          {/* Flash Message */}
          {flashMessage && (
            <div
              className={`mb-6 p-3 rounded text-sm font-medium transition-colors duration-300 text-center ${
                flashMessage.type === "success"
                  ? "text-green-800 bg-green-100 dark:text-green-300 dark:bg-green-900"
                  : "text-red-800 bg-red-100 dark:text-red-300 dark:bg-red-900"
              }`}
            >
              {flashMessage.message}
            </div>
          )}

          {renderStepContent()}

          <button
            type="submit"
            className="w-full py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white font-semibold shadow-lg transition-all duration-300"
          >
            {step === "email"
              ? "Send Code"
              : step === "verify"
              ? "Verify Code"
              : "Reset Password"}
          </button>

          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => navigate("/login")}
              className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ForgotPassword;
