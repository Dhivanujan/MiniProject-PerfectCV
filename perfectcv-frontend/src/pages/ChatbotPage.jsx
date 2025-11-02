// ChatbotPage.jsx
import React, { useState, useRef, useEffect } from "react";
import { FaUpload, FaPaperPlane, FaSpinner, FaExclamationCircle } from "react-icons/fa";

// API config
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";
const API_ENDPOINTS = {
  upload: `${API_BASE}/api/chatbot/upload`,
  ask: `${API_BASE}/api/chatbot/ask`,
};

export default function ChatbotPage() {
  const [chatHistory, setChatHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [cvFiles, setCvFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [error, setError] = useState(null);
  const [hasCv, setHasCv] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isBotTyping]);

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    // Validate file types
    const invalidFiles = files.filter(file => 
      !file.name.toLowerCase().match(/\.(pdf|doc|docx)$/)
    );
    
    if (invalidFiles.length) {
      setError("Please upload only PDF, DOC, or DOCX files.");
      return;
    }
    setCvFiles(files);
    setError(null);
  };

  const handleUpload = async () => {
    if (!cvFiles.length) {
      setError("Please select a CV file first.");
      return;
    }
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("files", cvFiles[0]); // Upload first file only for now

    try {
      const res = await fetch(API_ENDPOINTS.upload, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await res.json();
      
      if (data.success) {
        setChatHistory([{ sender: "bot", text: data.message }]);
        setHasCv(true);
        setCvFiles([]);
      } else {
        setError(data.message || "Upload failed. Please try again.");
        setChatHistory([{ 
          sender: "bot", 
          text: "I encountered an error processing your CV. Please try uploading again." 
        }]);
      }
    } catch (err) {
      setError("Network error. Please check your connection and try again.");
      console.error("Upload error:", err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSend = async () => {
    if (!message.trim()) return;
    
    if (!hasCv) {
      setError("Please upload your CV first so I can answer questions about it.");
      return;
    }

    const userMessage = { sender: "user", text: message.trim() };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage("");
    setIsBotTyping(true);
    setError(null);

    try {
      const res = await fetch(API_ENDPOINTS.ask, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text }),
        credentials: "include",
      });
      
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      
      if (data.success) {
        const botMessage = { 
          sender: "bot", 
          text: data.answer
        };
        setTimeout(() => {
          setChatHistory(prev => [...prev, botMessage]);
          setIsBotTyping(false);
        }, 500);
      } else {
        throw new Error(data.message || "Failed to get response");
      }
    } catch (err) {
      console.error("Chat error:", err);
      setError(err.message || "Failed to get response. Please try again.");
      setChatHistory(prev => [...prev, { 
        sender: "bot", 
        text: "I'm having trouble processing your question. Please try again." 
      }]);
      setIsBotTyping(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 p-6">
      <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-8 text-center">
        🤖 PerfectCV Chatbot
      </h1>

      {/* Error Alert */}
      {error && (
        <div className="w-full max-w-xl mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-xl flex items-center gap-2">
          <FaExclamationCircle className="flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* PDF Upload Section */}
      <div className="mb-6 w-full max-w-xl">
        <label 
          className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 ${
            isUploading 
              ? 'border-gray-400 bg-gray-50' 
              : hasCv
                ? 'border-green-400 bg-green-50 dark:border-green-600 dark:bg-green-900/20'
                : 'border-blue-400 hover:border-blue-500 hover:bg-blue-50 dark:border-blue-600 dark:hover:bg-blue-900/20'
          }`}
        >
          <input 
            type="file" 
            className="hidden" 
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx"
            disabled={isUploading} 
          />
          {isUploading ? (
            <FaSpinner className="text-5xl mb-3 text-gray-500 animate-spin" />
          ) : hasCv ? (
            <div className="text-5xl mb-3">✅</div>
          ) : (
            <FaUpload className="text-5xl mb-3 text-blue-500" />
          )}
          <span className="text-center text-gray-600 dark:text-gray-300">
            {isUploading 
              ? "Processing your CV..."
              : hasCv 
                ? "CV uploaded! Ask me anything about it."
                : cvFiles.length 
                  ? `Selected: ${cvFiles[0].name}`
                  : "Click to upload your CV (PDF, DOC, or DOCX)"}
          </span>
        </label>
        {cvFiles.length > 0 && !hasCv && (
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className={`mt-4 w-full p-3 rounded-xl transition-all duration-200 flex items-center justify-center gap-2
              ${isUploading 
                ? 'bg-gray-400 cursor-wait' 
                : 'bg-blue-500 hover:bg-blue-600 hover:shadow-lg'} text-white`}
          >
            {isUploading ? <FaSpinner className="animate-spin" /> : <FaUpload />}
            <span>{isUploading ? "Processing..." : "Upload & Process CV"}</span>
          </button>
        )}
      </div>

      {/* Chat Section */}
      <div className={`w-full max-w-xl flex flex-col bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-4 h-[500px] transition-opacity duration-300 ${chatHistory.length ? 'opacity-100' : 'opacity-0'}`}>
        <div className="flex-1 overflow-y-auto mb-4 space-y-3 relative">
          {chatHistory.length === 0 && hasCv && (
            <div className="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400">
              Ask me anything about your CV!
            </div>
          )}
          
          {chatHistory.map((msg, idx) => (
            <div key={idx} className={`flex items-end ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              {msg.sender === "bot" && (
                <div className="w-8 h-8 bg-blue-500 text-white flex items-center justify-center rounded-full mr-2 font-bold">
                  🤖
                </div>
              )}
              
              <div className={`p-3 rounded-2xl max-w-md break-words shadow-md ${
                msg.sender === "user"
                  ? "bg-blue-500 text-white ml-12"
                  : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white mr-12"
              }`}>
                {msg.text}
              </div>

              {msg.sender === "user" && (
                <div className="w-8 h-8 bg-green-500 text-white flex items-center justify-center rounded-full ml-2 font-bold">
                  U
                </div>
              )}
            </div>
          ))}

          {isBotTyping && (
            <div className="flex items-center justify-start gap-2">
              <div className="w-8 h-8 bg-blue-500 text-white flex items-center justify-center rounded-full font-bold">
                🤖
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-2xl flex gap-2">
                <span className="animate-bounce">•</span>
                <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>•</span>
                <span className="animate-bounce" style={{ animationDelay: "0.4s" }}>•</span>
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
            placeholder={hasCv ? "Ask anything about your CV..." : "Upload your CV to start chatting..."}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            disabled={!hasCv || isBotTyping}
          />
          <button
            onClick={handleSend}
            disabled={!hasCv || !message.trim() || isBotTyping}
            className={`p-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed
              ${isBotTyping 
                ? 'bg-gray-400' 
                : message.trim() 
                  ? 'bg-blue-500 hover:bg-blue-600' 
                  : 'bg-gray-400'} text-white`}
          >
            {isBotTyping ? <FaSpinner className="animate-spin" /> : <FaPaperPlane />}
          </button>
        </div>
      </div>
    </div>
  );
}
