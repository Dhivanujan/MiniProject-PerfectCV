// ChatbotPage.jsx
import React, { useState, useRef, useEffect } from "react";
import { FaUpload, FaPaperPlane } from "react-icons/fa";

export default function ChatbotPage() {
  const [chatHistory, setChatHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [cvFiles, setCvFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isBotTyping]);

  // Handle PDF file selection
  const handleFileChange = (e) => setCvFiles(e.target.files);

  // Upload PDFs to Flask chatbot endpoint
  const handleUpload = async () => {
    if (!cvFiles.length) return;
    setIsUploading(true);

    const formData = new FormData();
    Array.from(cvFiles).forEach((file) => formData.append("files", file));

    try {
      const res = await fetch("http://localhost:5000/api/chatbot/upload", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await res.json();
      if (data.success) {
        setChatHistory([{ sender: "bot", text: data.message }]);
      } else {
        setChatHistory([{ sender: "bot", text: data.message || "Upload failed." }]);
      }
    } catch (err) {
      setChatHistory([{ sender: "bot", text: "Error uploading files." }]);
    } finally {
      setIsUploading(false);
    }
  };

  // Send question to Flask chatbot endpoint
  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = { sender: "user", text: message };
    setChatHistory((prev) => [...prev, userMessage]);
    setMessage("");
    setIsBotTyping(true);

    try {
      const res = await fetch("http://localhost:5000/api/chatbot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: message }),
        credentials: "include",
      });
      const data = await res.json();
      const botMessage = { sender: "bot", text: data.answer || data.message || "No answer available." };

      setTimeout(() => {
        setChatHistory((prev) => [...prev, botMessage]);
        setIsBotTyping(false);
      }, 800); // simulate typing delay
    } catch (err) {
      setChatHistory((prev) => [...prev, { sender: "bot", text: "Error getting response from server." }]);
      setIsBotTyping(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 p-6">
      <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-8 text-center animate-pulse">
        🤖 PerfectCV Chatbot
      </h1>

      {/* PDF Upload Section */}
      <div className="mb-6 w-full max-w-xl">
        <label className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-400 dark:border-gray-600 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-gray-700 transition-all duration-300">
          <input type="file" className="hidden" multiple onChange={handleFileChange} />
          <FaUpload className="text-5xl mb-3 text-blue-500" />
          <span className="text-gray-600 dark:text-gray-300">
            {cvFiles.length ? `${cvFiles.length} file(s) selected` : "Click to select your CV PDFs"}
          </span>
        </label>
        <button
          onClick={handleUpload}
          disabled={isUploading || !cvFiles.length}
          className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-xl transition-all duration-200 disabled:opacity-50"
        >
          {isUploading ? "Uploading..." : "Upload & Process"}
        </button>
      </div>

      {/* Chat Section */}
      {chatHistory.length > 0 && (
        <div className="w-full max-w-xl flex flex-col bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-4 h-[500px]">
          <div className="flex-1 overflow-y-auto mb-4 space-y-3">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`flex items-end ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                {/* Avatar */}
                {msg.sender === "bot" && (
                  <div className="w-8 h-8 bg-blue-500 text-white flex items-center justify-center rounded-full mr-2 font-bold">
                    🤖
                  </div>
                )}
                {msg.sender === "user" && (
                  <div className="w-8 h-8 bg-green-500 text-white flex items-center justify-center rounded-full ml-2 font-bold">
                    U
                  </div>
                )}

                {/* Message bubble */}
                <div
                  className={`p-3 rounded-2xl max-w-xs break-words shadow ${
                    msg.sender === "user"
                      ? "bg-blue-500 text-white animate-slideInRight"
                      : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white animate-slideInLeft"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isBotTyping && (
              <div className="flex items-center justify-start gap-2">
                <div className="w-8 h-8 bg-blue-500 text-white flex items-center justify-center rounded-full font-bold">
                  🤖
                </div>
                <div className="bg-gray-200 dark:bg-gray-700 p-3 rounded-2xl max-w-xs animate-pulse">
                  Typing...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Section */}
          <div className="flex items-center gap-3">
            <input
              type="text"
              className="flex-1 p-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400 transition-colors"
              placeholder="Type your question..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button
              onClick={handleSend}
              className="p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <FaPaperPlane />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
