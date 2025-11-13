// ChatbotPage.jsx
import React, { useState, useRef, useEffect } from "react";
import { FaUpload, FaPaperPlane, FaSpinner, FaExclamationCircle, FaDownload, FaLightbulb, FaCheckCircle } from "react-icons/fa";

// Simple component to render formatted text
const FormattedText = ({ text }) => {
  const formatText = (text) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Check for headers (lines starting with **)
      if (line.startsWith('**') && line.endsWith('**')) {
        const headerText = line.slice(2, -2);
        return <div key={idx} className="font-bold text-lg mt-3 mb-2">{headerText}</div>;
      }
      
      // Check for bold text
      if (line.includes('**')) {
        const parts = line.split('**');
        return (
          <div key={idx} className="mb-1">
            {parts.map((part, i) => 
              i % 2 === 1 ? <strong key={i}>{part}</strong> : <span key={i}>{part}</span>
            )}
          </div>
        );
      }
      
      // Check for bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return <div key={idx} className="ml-4 mb-1">{line}</div>;
      }
      
      // Empty line
      if (line.trim() === '') {
        return <div key={idx} className="h-2"></div>;
      }
      
      // Regular line
      return <div key={idx} className="mb-1">{line}</div>;
    });
  };

  return <div className="whitespace-pre-wrap">{formatText(text)}</div>;
};

// API config
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";
const API_ENDPOINTS = {
  upload: `${API_BASE}/api/chatbot/upload`,
  ask: `${API_BASE}/api/chatbot/ask`,
  download: `${API_BASE}/api/chatbot/download-cv`,
  analysis: `${API_BASE}/api/chatbot/analysis`,
};

// Quick action buttons for common queries
const QUICK_ACTIONS = [
  { label: "What's missing?", query: "What important sections or information am I missing in my CV?" },
  { label: "ATS Check", query: "Is this CV ATS friendly? What can I improve?" },
  { label: "Improve Summary", query: "Can you improve my professional summary section?" },
  { label: "Add Keywords", query: "What keywords should I add for a software engineering role?" },
  { label: "Generate Updated CV", query: "Generate an improved version of my CV" },
];

export default function ChatbotPage() {
  const [chatHistory, setChatHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [cvFiles, setCvFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [error, setError] = useState(null);
  const [hasCv, setHasCv] = useState(false);
  const [hasGeneratedCv, setHasGeneratedCv] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
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

  const handleSend = async (customMessage = null) => {
    const queryText = customMessage || message.trim();
    if (!queryText) return;
    
    if (!hasCv) {
      setError("Please upload your CV first so I can answer questions about it.");
      return;
    }

    const userMessage = { sender: "user", text: queryText };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage("");
    setIsBotTyping(true);
    setError(null);
    setShowQuickActions(false);

    try {
      const res = await fetch(API_ENDPOINTS.ask, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: queryText }),
        credentials: "include",
      });
      
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      
      if (data.success) {
        const botMessage = { 
          sender: "bot", 
          text: data.answer,
          queryType: data.query_type,
          metadata: {
            ats_result: data.ats_result,
            keywords: data.keywords,
            improved_text: data.improved_text,
            generated_cv: data.generated_cv,
          }
        };
        
        // Check if CV was generated
        if (data.generated_cv) {
          setHasGeneratedCv(true);
        }
        
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

  const handleQuickAction = (query) => {
    handleSend(query);
  };

  const handleDownloadCV = async () => {
    try {
      const res = await fetch(API_ENDPOINTS.download, {
        method: "GET",
        credentials: "include",
      });
      
      if (!res.ok) throw new Error("Download failed");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'improved_cv.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError("Failed to download CV. Please generate it first.");
      console.error("Download error:", err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 p-6">
      <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-8 text-center">
        🤖 PerfectCV Chatbot
      </h1>

      {/* Error Alert */}
      {error && (
        <div className="w-full max-w-4xl mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-xl flex items-center gap-2">
          <FaExclamationCircle className="flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Download Button */}
      {hasGeneratedCv && (
        <div className="w-full max-w-4xl mb-4">
          <button
            onClick={handleDownloadCV}
            className="w-full p-4 bg-green-500 hover:bg-green-600 text-white rounded-xl flex items-center justify-center gap-2 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <FaDownload />
            <span className="font-semibold">Download Improved CV</span>
          </button>
        </div>
      )}

      {/* PDF Upload Section */}
      <div className="mb-6 w-full max-w-4xl">
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
      <div className={`w-full max-w-4xl flex flex-col bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6 h-[600px] transition-opacity duration-300 ${chatHistory.length ? 'opacity-100' : 'opacity-0'}`}>
        
        {/* Quick Actions */}
        {hasCv && showQuickActions && chatHistory.length === 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-3">
              <FaLightbulb className="text-yellow-500" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Quick Actions:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {QUICK_ACTIONS.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickAction(action.query)}
                  className="px-4 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-200 rounded-lg text-sm transition-all duration-200 hover:shadow-md"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto mb-4 space-y-4 relative">
          {chatHistory.length === 0 && hasCv && (
            <div className="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-center p-4">
              <div>
                <p className="text-lg font-semibold mb-2">👋 Hi! I'm your CV Assistant</p>
                <p className="text-sm">Try the quick actions above or ask me anything about your CV!</p>
              </div>
            </div>
          )}
          
          {chatHistory.map((msg, idx) => (
            <div key={idx} className={`flex items-start ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              {msg.sender === "bot" && (
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center rounded-full mr-3 font-bold text-lg flex-shrink-0">
                  🤖
                </div>
              )}
              
              <div className={`p-4 rounded-2xl max-w-2xl break-words shadow-md ${
                msg.sender === "user"
                  ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white"
                  : "bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600"
              }`}>
                {msg.sender === "bot" ? (
                  <div className="text-sm">
                    <FormattedText text={msg.text} />
                    {msg.queryType && (
                      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                        <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                          <FaCheckCircle className="text-green-500" />
                          Analysis: {msg.queryType.replace('_', ' ')}
                        </span>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                )}
              </div>

              {msg.sender === "user" && (
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 text-white flex items-center justify-center rounded-full ml-3 font-bold text-lg flex-shrink-0">
                  👤
                </div>
              )}
            </div>
          ))}

          {isBotTyping && (
            <div className="flex items-start justify-start gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center rounded-full font-bold text-lg">
                🤖
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 p-4 rounded-2xl flex gap-2">
                <span className="animate-bounce text-blue-500">●</span>
                <span className="animate-bounce text-blue-500" style={{ animationDelay: "0.2s" }}>●</span>
                <span className="animate-bounce text-blue-500" style={{ animationDelay: "0.4s" }}>●</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Section */}
        <div className="flex items-center gap-3">
          <input
            type="text"
            className="flex-1 p-4 rounded-xl border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 transition-all"
            placeholder={hasCv ? "Ask anything about your CV..." : "Upload your CV to start chatting..."}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            disabled={!hasCv || isBotTyping}
          />
          <button
            onClick={() => handleSend()}
            disabled={!hasCv || !message.trim() || isBotTyping}
            className={`p-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed
              ${isBotTyping 
                ? 'bg-gray-400' 
                : message.trim() 
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700' 
                  : 'bg-gray-400'} text-white`}
          >
            {isBotTyping ? <FaSpinner className="animate-spin text-xl" /> : <FaPaperPlane className="text-xl" />}
          </button>
        </div>
      </div>
    </div>
  );
}
