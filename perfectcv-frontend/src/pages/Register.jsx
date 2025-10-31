// src/pages/Register.jsx
import React, { useState } from "react";
import LeftImage from "../assets/CV.png";

function Register() {
  const [formData, setFormData] = useState({
    full_name: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
  });

  const [flashMessages, setFlashMessages] = useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirm_password) {
      setFlashMessages([{ type: "danger", message: "Passwords do not match" }]);
      setTimeout(() => setFlashMessages([]), 3000);
      return;
    }

    try {
      const { confirm_password, ...payload } = formData;

      // Use axios instance so baseURL and credentials are handled consistently
      const res = await (await import("../api")).default.post("/auth/register", payload, {
        validateStatus: () => true,
      });

      const data = res.data || {};

      if (data.success) {
        setFlashMessages([{ type: "success", message: data.message }]);
        setTimeout(() => {
          window.location.href = "/login";
        }, 1500);
      } else {
        const details = data.details ? ` - ${data.details}` : "";
        setFlashMessages([{ type: "danger", message: (data.message || "Registration failed") + details }]);
      }

      setTimeout(() => setFlashMessages([]), 3000);
    } catch (error) {
      console.error("Register error:", error);
      setFlashMessages([{ type: "danger", message: "Server error" }]);
      setTimeout(() => setFlashMessages([]), 3000);
    }
  };

  return (
    <div
      className="flex h-screen w-full 
      bg-gradient-to-b from-[#F5F7FF] via-[#FFFBEA] to-[#E6EFFF]
      dark:from-[#0D1117] dark:via-[#161B22] dark:to-[#1E2329]
      transition-colors duration-500"
    >
      {/* Left Side Image (hidden on mobile) */}
      <div className="w-full hidden md:inline-block">
        <img className="h-full w-full object-cover" src={LeftImage} alt="leftSideImage" />
      </div>

      {/* Right Side Form */}
      <div className="w-full flex flex-col items-center justify-center">
        <form
          onSubmit={handleSubmit}
          className="md:w-96 w-80 flex flex-col items-center justify-center 
          bg-white dark:bg-[#1E1E2F] p-8 rounded-xl shadow-lg 
          transition-all duration-500"
        >
          <h2 className="text-4xl font-bold text-indigo-600 dark:text-indigo-400">Sign Up</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-3 mb-4">
            Create your account to get started
          </p>

          {/* Flash messages */}
          {flashMessages.length > 0 && (
            <div id="flash-messages" className="flex flex-col gap-2 w-full mb-4">
              {flashMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between w-full h-10 shadow rounded-sm px-2 text-sm
                    ${
                      msg.type === "success"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100"
                        : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100"
                    }`}
                >
                  <p>{msg.message}</p>
                  <button
                    type="button"
                    aria-label="close"
                    className="active:scale-90 transition-all"
                    onClick={() => setFlashMessages([])}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Input fields */}
          {[
            { name: "full_name", placeholder: "Full Name", type: "text" },
            { name: "username", placeholder: "Username", type: "text" },
            { name: "email", placeholder: "Email Address", type: "email" },
            { name: "phone", placeholder: "Phone Number", type: "text" },
            { name: "password", placeholder: "Password", type: "password" },
            { name: "confirm_password", placeholder: "Confirm Password", type: "password" },
          ].map((field) => (
            <div
              key={field.name}
              className="flex items-center w-full bg-transparent border border-gray-300 dark:border-gray-600
              h-12 rounded-full overflow-hidden pl-6 mt-4 transition-all"
            >
              <input
                placeholder={field.placeholder}
                className="bg-transparent text-gray-700 dark:text-gray-200 placeholder-gray-400 
                dark:placeholder-gray-500 outline-none text-sm w-full h-full"
                type={field.type}
                name={field.name}
                value={formData[field.name]}
                onChange={handleChange}
                required
              />
            </div>
          ))}

          <button
            type="submit"
            className="mt-8 w-full h-11 rounded-full text-white 
            bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-700 
            font-semibold transition-all"
          >
            Sign Up
          </button>

          <p className="text-gray-500 dark:text-gray-400 text-sm mt-4">
            Already have an account?{" "}
            <a className="text-indigo-500 dark:text-indigo-400 hover:underline" href="/login">
              Log In
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Register;
