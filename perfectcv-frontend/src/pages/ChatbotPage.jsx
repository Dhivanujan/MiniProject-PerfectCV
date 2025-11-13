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
  const chatContainerRef = useRef(null);

  // Only scroll when there's actual chat content
  useEffect(() => {
    if (chatHistory.length > 0 || isBotTyping) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header with animated gradient */}
      <div className="sticky top-0 z-10 backdrop-blur-md bg-white/70 dark:bg-gray-900/70 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform">
                <span className="text-2xl">🤖</span>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  PerfectCV AI Assistant
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Your intelligent CV enhancement partner</p>
              </div>
            </div>
            {hasCv && (
              <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700 dark:text-green-400">CV Loaded</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6 flex flex-col gap-6">
        {/* Error Alert */}
        {error && (
          <div className="animate-slide-in-down p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 text-red-700 dark:text-red-400 rounded-r-xl flex items-center gap-3 shadow-md">
            <FaExclamationCircle className="flex-shrink-0 text-xl" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Download Button */}
        {hasGeneratedCv && (
          <div className="animate-slide-in-up">
            <button
              onClick={handleDownloadCV}
              className="w-full p-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-xl flex items-center justify-center gap-3 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            >
              <FaDownload className="text-xl" />
              <span className="font-semibold text-lg">Download Improved CV</span>
            </button>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6">
          {/* Left Column - Upload Section */}
          <div className="md:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                <FaUpload className="text-blue-500" />
                Upload CV
              </h2>
              
              <label 
                className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 ${
                  isUploading 
                    ? 'border-gray-400 bg-gray-50 dark:bg-gray-700/50' 
                    : hasCv
                      ? 'border-green-400 bg-green-50 dark:border-green-600 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30'
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
                  <div className="text-5xl mb-3 animate-bounce">✅</div>
                ) : (
                  <FaUpload className="text-5xl mb-3 text-blue-500 group-hover:scale-110 transition-transform" />
                )}
                <span className="text-center text-sm font-medium text-gray-600 dark:text-gray-300">
                  {isUploading 
                    ? "Processing your CV..."
                    : hasCv 
                      ? "✓ CV uploaded successfully!"
                      : cvFiles.length 
                        ? `Selected: ${cvFiles[0].name}`
                        : "Click to upload CV"}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 mt-2">PDF, DOC, or DOCX</span>
              </label>
              
              {cvFiles.length > 0 && !hasCv && (
                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className={`mt-4 w-full p-3 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 font-semibold
                    ${isUploading 
                      ? 'bg-gray-400 cursor-wait' 
                      : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 hover:shadow-lg transform hover:scale-[1.02]'} text-white`}
                >
                  {isUploading ? <FaSpinner className="animate-spin" /> : <FaUpload />}
                  <span>{isUploading ? "Processing..." : "Upload & Analyze"}</span>
                </button>
              )}

              {hasCv && (
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">✨ Ready to assist!</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Your CV has been analyzed. Ask me anything or use quick actions below.</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Chat Section */}
          <div className="md:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 flex flex-col h-[calc(100vh-16rem)]">
              {/* Chat Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                  <span className="text-2xl">💬</span>
                  Chat Assistant
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {hasCv ? "Ask me anything about your CV or use quick actions" : "Upload a CV to start chatting"}
                </p>
              </div>

              {/* Quick Actions */}
              {hasCv && showQuickActions && chatHistory.length === 0 && (
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/10 dark:to-purple-900/10 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2 mb-3">
                    <FaLightbulb className="text-amber-500 animate-pulse" />
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Quick Actions:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {QUICK_ACTIONS.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleQuickAction(action.query)}
                        className="px-3 py-2 bg-white dark:bg-gray-700 hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-600 hover:text-white border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm transition-all duration-200 hover:shadow-md hover:scale-105 font-medium"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Chat Messages */}
              <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-transparent to-gray-50/50 dark:to-gray-900/50">
                {chatHistory.length === 0 && hasCv && (
                  <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-center p-4">
                    <div className="animate-fade-in">
                      <div className="text-6xl mb-4">👋</div>
                      <p className="text-xl font-semibold mb-2 text-gray-700 dark:text-gray-300">Hi! I'm your CV Assistant</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Try the quick actions above or ask me anything about your CV!</p>
                    </div>
                  </div>
                )}
                
                {chatHistory.length === 0 && !hasCv && (
                  <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-center p-4">
                    <div className="animate-fade-in">
                      <div className="text-6xl mb-4">📄</div>
                      <p className="text-xl font-semibold mb-2 text-gray-700 dark:text-gray-300">Upload Your CV to Get Started</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">I'll analyze it and help you improve it!</p>
                    </div>
                  </div>
                )}
                
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`flex items-start gap-3 animate-slide-in ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                    {msg.sender === "bot" && (
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center rounded-full shadow-lg flex-shrink-0">
                        <span className="text-lg">🤖</span>
                      </div>
                    )}
                    
                    <div className={`p-4 rounded-2xl max-w-xl break-words shadow-lg transition-all hover:shadow-xl ${
                      msg.sender === "user"
                        ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white"
                        : "bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600"
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
                        <p className="whitespace-pre-wrap font-medium">{msg.text}</p>
                      )}
                    </div>

                    {msg.sender === "user" && (
                      <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 text-white flex items-center justify-center rounded-full shadow-lg flex-shrink-0">
                        <span className="text-lg">👤</span>
                      </div>
                    )}
                  </div>
                ))}

                {isBotTyping && (
                  <div className="flex items-start gap-3 animate-slide-in">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center rounded-full shadow-lg">
                      <span className="text-lg">🤖</span>
                    </div>
                    <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 p-4 rounded-2xl flex gap-2 shadow-lg">
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input Section */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    className="flex-1 p-4 rounded-xl border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 transition-all text-sm"
                    placeholder={hasCv ? "Type your question here..." : "Upload your CV to start chatting..."}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                    disabled={!hasCv || isBotTyping}
                  />
                  <button
                    onClick={() => handleSend()}
                    disabled={!hasCv || !message.trim() || isBotTyping}
                    className={`p-4 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 ${
                      isBotTyping 
                        ? 'bg-gray-400' 
                        : message.trim() 
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700' 
                          : 'bg-gray-400'
                    } text-white`}
                  >
                    {isBotTyping ? <FaSpinner className="animate-spin text-xl" /> : <FaPaperPlane className="text-xl" />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
