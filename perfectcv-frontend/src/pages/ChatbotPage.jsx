// ChatbotPage.jsx
import React, { useState, useRef, useEffect } from "react";
import {
  FaUpload,
  FaPaperPlane,
  FaSpinner,
  FaExclamationCircle,
  FaDownload,
  FaLightbulb,
  FaCheckCircle,
  FaRobot,
  FaUserCircle,
  FaChevronDown,
  FaChevronUp,
  FaRegClock,
  FaClipboardList,
  FaMagic,
  FaTags
} from "react-icons/fa";

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

const QUICK_SUGGESTIONS = [
  { label: "Highlight strengths", query: "Can you summarize the strongest parts of my CV?" },
  { label: "Tailor for role", query: "How can I tailor this CV for a product manager position?" },
  { label: "Boost achievements", query: "Can you rewrite a few achievements to sound more impactful?" },
  { label: "Skill gaps", query: "What skills should I add to stand out for tech roles?" }
];

const toTitleCase = (value = "") =>
  value
    .split(" ")
    .map((word) => (word ? word.charAt(0).toUpperCase() + word.slice(1) : ""))
    .join(" ");

const formatTimestamp = (iso) => {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

const KeywordPills = ({ title, items = [] }) => {
  if (!items.length) return null;
  return (
    <div className="bg-white/70 dark:bg-gray-800/60 border border-blue-100 dark:border-blue-900/40 rounded-xl p-3 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-300 flex items-center gap-2"><FaTags />{title}</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {items.slice(0, 10).map((keyword, idx) => (
          <span
            key={`${keyword}-${idx}`}
            className="px-2.5 py-1 text-xs font-medium bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-200 rounded-full"
          >
            {keyword}
          </span>
        ))}
      </div>
    </div>
  );
};

const MetadataCards = ({ metadata }) => {
  if (!metadata) return null;
  const { ats_result: atsResult, keywords, improved_text: improvedText, generated_cv: generatedCv } = metadata;

  const improvedContent = typeof improvedText === "string" && improvedText.trim()
    ? improvedText.trim()
    : typeof generatedCv === "string" && generatedCv.trim()
      ? generatedCv.trim()
      : "";

  return (
    <div className="mt-4 space-y-4">
      {atsResult && (
        <div className="rounded-2xl border border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/80 dark:bg-emerald-900/20 p-4 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 font-semibold text-sm">
              <FaClipboardList />
              ATS Snapshot
            </div>
            <div className="text-right">
              <p className="text-xs uppercase text-emerald-500/80">Score</p>
              <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-300">
                {typeof atsResult.ats_score === "number" ? `${Math.round(atsResult.ats_score)} / 100` : atsResult.ats_score || "N/A"}
              </p>
            </div>
          </div>
          {Array.isArray(atsResult.issues) && atsResult.issues.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm text-emerald-800 dark:text-emerald-200">
              {atsResult.issues.slice(0, 3).map((issue, idx) => (
                <li key={`issue-${idx}`} className="flex gap-2">
                  <span className="text-emerald-500">•</span>
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          )}
          {atsResult.overall_recommendation && (
            <p className="mt-3 text-sm text-emerald-800 dark:text-emerald-200">
              {atsResult.overall_recommendation}
            </p>
          )}
        </div>
      )}

      {keywords && (
        <div className="rounded-2xl border border-blue-200 dark:border-blue-900/40 bg-blue-50/70 dark:bg-blue-900/10 p-4 shadow-sm space-y-3">
          <p className="text-sm font-semibold text-blue-700 dark:text-blue-200 flex items-center gap-2">
            <FaLightbulb className="text-amber-400" /> Suggested Keywords
          </p>
          {keywords.priority_additions && (
            <KeywordPills title="High Priority" items={keywords.priority_additions} />
          )}
          {keywords.suggested_keywords && (
            <KeywordPills title="Additional Ideas" items={keywords.suggested_keywords} />
          )}
          {keywords.existing_keywords && (
            <div className="bg-white/60 dark:bg-gray-800/60 border border-blue-100 dark:border-blue-900/30 rounded-xl p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-300">Already in your CV</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {keywords.existing_keywords.slice(0, 12).map((item, idx) => (
                  <span key={`existing-${idx}`} className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-full">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {improvedContent && (
        <div className="rounded-2xl border border-purple-200 dark:border-purple-900/40 bg-purple-50/70 dark:bg-purple-900/20 p-4 shadow-sm">
          <p className="text-sm font-semibold text-purple-700 dark:text-purple-200 flex items-center gap-2">
            <FaMagic /> Preview of improvements
          </p>
          <div className="mt-3 text-sm text-purple-900 dark:text-purple-100 bg-white/70 dark:bg-gray-900/50 border border-purple-100 dark:border-purple-800/40 rounded-xl p-3 max-h-56 overflow-y-auto">
            <FormattedText text={improvedContent.length > 1200 ? `${improvedContent.slice(0, 1200)}...` : improvedContent} />
          </div>
          <p className="mt-2 text-xs text-purple-600 dark:text-purple-200">Download the improved CV to see the full version.</p>
        </div>
      )}
    </div>
  );
};

const ChatMessage = ({ message }) => {
  const isUser = message.sender === "user";
  const timestamp = formatTimestamp(message.timestamp);
  const queryLabel = message.queryType ? toTitleCase(message.queryType.replace(/_/g, " ")) : null;

  return (
    <div className={`flex items-start gap-3 animate-slide-in ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div className={`${isUser ? "bg-gradient-to-br from-green-500 to-emerald-500" : "bg-gradient-to-br from-blue-500 to-purple-600"} w-11 h-11 text-white flex items-center justify-center rounded-2xl shadow-lg flex-shrink-0`}>
        {isUser ? <FaUserCircle className="text-xl" /> : <FaRobot className="text-xl" />}
      </div>

      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-2xl`}>
        <div
          className={`p-4 rounded-3xl shadow-lg border transition-all duration-200 hover:shadow-xl ${
            isUser
              ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white border-blue-400"
              : "bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.text}</p>
          ) : (
            <div className="text-sm leading-relaxed">
              <FormattedText text={message.text} />
              {queryLabel && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600 text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400 flex items-center gap-2">
                  <FaCheckCircle className="text-green-500" />
                  {queryLabel} insight
                </div>
              )}
              <MetadataCards metadata={message.metadata} />
            </div>
          )}
        </div>
        {timestamp && (
          <div className={`mt-2 flex items-center gap-1 text-xs text-gray-400 ${isUser ? "flex-row-reverse" : ""}`}>
            <FaRegClock />
            <span>{timestamp}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default function ChatbotPage() {
  const [chatHistory, setChatHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [cvFiles, setCvFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [error, setError] = useState(null);
  const [hasCv, setHasCv] = useState(false);
  const [hasGeneratedCv, setHasGeneratedCv] = useState(false);
  const [isQuickActionsOpen, setIsQuickActionsOpen] = useState(true);
  const chatEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const messageInputRef = useRef(null);

  const createMessage = (sender, text, extras = {}) => ({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    sender,
    text,
    timestamp: new Date().toISOString(),
    ...extras,
  });

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

  useEffect(() => {
    if (messageInputRef.current) {
      const el = messageInputRef.current;
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
    }
  }, [message]);

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
        setChatHistory([createMessage("bot", data.message)]);
        setHasCv(true);
        setCvFiles([]);
        setIsQuickActionsOpen(true);
      } else {
        setError(data.message || "Upload failed. Please try again.");
        setChatHistory([
          createMessage(
            "bot",
            "I encountered an error processing your CV. Please try uploading again."
          ),
        ]);
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

    const userMessage = createMessage("user", queryText);
    setChatHistory(prev => [...prev, userMessage]);
    setMessage("");
    setIsBotTyping(true);
    setError(null);
    setIsQuickActionsOpen(false);

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
        const botMessage = createMessage("bot", data.answer, {
          queryType: data.query_type,
          metadata: {
            ats_result: data.ats_result,
            keywords: data.keywords,
            improved_text: data.improved_text,
            generated_cv: data.generated_cv,
          },
        });

        const generatedContent = data.generated_cv;
        const hasGeneratedContent = typeof generatedContent === "string"
          ? generatedContent.trim().length > 0
          : Boolean(generatedContent);
        if (hasGeneratedContent) {
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
      setChatHistory(prev => [
        ...prev,
        createMessage(
          "bot",
          "I'm having trouble processing your question. Please try again."
        ),
      ]);
      setIsBotTyping(false);
    }
  };

  const handleQuickAction = (query) => {
    if (isBotTyping) return;
    setIsQuickActionsOpen(false);
    handleSend(query);
  };

  const handleSuggestionClick = (query) => {
    if (!hasCv || isBotTyping) return;
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

  const isSendDisabled = !hasCv || isBotTyping || !message.trim();

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 overflow-hidden">
      {/* Header with animated gradient */}
      <div className="flex-shrink-0 backdrop-blur-md bg-white/70 dark:bg-gray-900/70 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  PerfectCV AI Assistant
                </h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">Your intelligent CV enhancement partner</p>
              </div>
            </div>
            {hasGeneratedCv && (
              <button
                onClick={handleDownloadCV}
                className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg flex items-center gap-2 transition-all duration-300 shadow-md hover:shadow-lg text-sm font-semibold"
              >
                <FaDownload />
                <span className="hidden md:inline">Download CV</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="flex-shrink-0 mx-4 mt-3 animate-slide-in-down p-3 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 text-red-700 dark:text-red-400 rounded-r-xl flex items-center gap-3 shadow-md">
          <FaExclamationCircle className="flex-shrink-0" />
          <span className="font-medium text-sm">{error}</span>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col md:flex-row gap-2 p-2 overflow-hidden">
          {/* Left Column - Upload Section */}
          <div className="md:w-64 flex-shrink-0">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-3 border border-gray-200 dark:border-gray-700 h-full overflow-y-auto">
              <h2 className="text-sm font-bold text-gray-800 dark:text-white mb-2 flex items-center gap-1.5">
                <FaUpload className="text-blue-500 text-xs" />
                Upload CV
              </h2>
              
              <label 
                className={`flex flex-col items-center justify-center p-3 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-300 ${
                  isUploading 
                    ? 'border-gray-400 bg-gray-50 dark:bg-gray-700/50' 
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
                  <FaSpinner className="text-2xl mb-1 text-gray-500 animate-spin" />
                ) : hasCv ? (
                  <div className="text-2xl mb-1">✅</div>
                ) : (
                  <FaUpload className="text-2xl mb-1 text-blue-500" />
                )}
                <span className="text-center text-xs font-medium text-gray-600 dark:text-gray-300">
                  {isUploading 
                    ? "Processing..."
                    : hasCv 
                      ? "CV uploaded"
                      : cvFiles.length 
                        ? cvFiles[0].name.substring(0, 15) + '...'
                        : "Upload CV"}
                </span>
                <span className="text-xs text-gray-400 dark:text-gray-500">PDF/DOC/DOCX</span>
              </label>
              
              {cvFiles.length > 0 && !hasCv && (
                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className={`mt-2 w-full p-2 rounded-lg transition-all duration-300 flex items-center justify-center gap-2 text-sm font-semibold
                    ${isUploading 
                      ? 'bg-gray-400 cursor-wait' 
                      : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'} text-white`}
                >
                  {isUploading ? <FaSpinner className="animate-spin text-xs" /> : <FaUpload className="text-xs" />}
                  <span>{isUploading ? "Processing..." : "Analyze"}</span>
                </button>
              )}

              {hasCv && (
                <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">✨ Ready to assist!</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Your CV has been analyzed. Ask me anything or use quick actions.</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Chat Section */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 flex flex-col h-full overflow-hidden">
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
                <h2 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                  <span className="text-2xl">💬</span>
                  Chat Assistant
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {hasCv ? "Ask me anything about your CV or use quick actions" : "Upload a CV to start chatting"}
                </p>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                      hasCv
                        ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                        : "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300"
                    }`}
                  >
                    <FaCheckCircle className={hasCv ? "text-emerald-500" : "text-gray-500"} />
                    CV Uploaded
                  </span>
                  <span
                    className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                      chatHistory.length
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-200"
                        : "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300"
                    }`}
                  >
                    <FaRobot className={chatHistory.length ? "text-blue-500" : "text-gray-500"} />
                    Conversation {chatHistory.length ? "active" : "pending"}
                  </span>
                  {hasGeneratedCv && (
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-200">
                      <FaMagic className="text-purple-500" />
                      Improved CV ready
                    </span>
                  )}
                </div>
              </div>

              {/* Quick Actions */}
              {hasCv && chatHistory.length === 0 && (
                <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20">
                  <div className="flex flex-wrap gap-1.5">
                    {QUICK_ACTIONS.slice(0, 4).map((action, idx) => (
                      <button
                        key={action.label}
                        onClick={() => handleQuickAction(action.query)}
                        className="px-2 py-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg text-xs font-medium transition-all hover:bg-blue-500 hover:text-white"
                        disabled={isBotTyping}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Chat Messages */}
              <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-3 space-y-2 bg-gradient-to-b from-transparent to-gray-50/50 dark:to-gray-900/50">
                {chatHistory.length === 0 && hasCv && (
                  <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-center p-3">
                    <div className="animate-fade-in">
                      <div className="text-4xl mb-3">👋</div>
                      <p className="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-300">Hi! I'm your CV Assistant</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Ask me anything about your CV</p>
                    </div>
                  </div>
                )}
                
                {chatHistory.length === 0 && !hasCv && (
                  <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-center p-3">
                    <div className="animate-fade-in">
                      <div className="text-4xl mb-3">📄</div>
                      <p className="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-300">Upload Your CV to Get Started</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">I'll analyze it and help you improve it!</p>
                    </div>
                  </div>
                )}
                
                {chatHistory.map((msg, idx) => (
                  <ChatMessage key={msg.id || idx} message={msg} />
                ))}

                {isBotTyping && (
                  <div className="flex items-start gap-3 animate-slide-in">
                    <div className="w-11 h-11 bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center rounded-2xl shadow-lg">
                      <FaRobot className="text-xl" />
                    </div>
                    <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 px-5 py-4 rounded-3xl flex gap-2 shadow-lg">
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input Section */}
              <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0">
                <div className="flex items-end gap-2">
                  <textarea
                    ref={messageInputRef}
                    rows={1}
                    className="flex-1 resize-none p-2.5 rounded-xl border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 transition-all text-sm leading-relaxed max-h-32"
                    placeholder={hasCv ? "Ask about your CV..." : "Upload your CV to start chatting"}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    disabled={!hasCv || isBotTyping}
                  />
                  <button
                    onClick={() => handleSend()}
                    disabled={isSendDisabled}
                    className={`p-2.5 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed ${
                      isSendDisabled
                        ? "bg-gray-400"
                        : "bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                    } text-white`}
                  >
                    {isBotTyping ? <FaSpinner className="animate-spin text-lg" /> : <FaPaperPlane className="text-lg" />}
                  </button>
                </div>
                <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
                  Press <span className="font-semibold">Enter</span> to send or <span className="font-semibold">Shift + Enter</span> for a new line.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
