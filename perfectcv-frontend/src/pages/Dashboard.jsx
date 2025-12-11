import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import Navbar from "../components/Navbar";
import {
  FaUpload,
  FaDownload,
  FaTrash,
  FaFileAlt,
  FaSearch,
  FaSpinner,
  FaBriefcase,
  FaChevronDown,
  FaCheckCircle,
  FaExclamationCircle,
  FaStar,
  FaChartLine,
  FaClock,
  FaClipboardCheck,
  FaRobot,
  FaComments,
} from "react-icons/fa";
import CvIllustration from "../assets/CV_Illustration.png";
import ResumeTemplate from "../components/ResumeTemplate";

const JOB_DOMAIN_OPTIONS = [
  { value: "", label: "🌐 General", shortLabel: "General" },
  { value: "software", label: "💻 Software / Engineering", shortLabel: "Software" },
  { value: "data_science", label: "📊 Data Science / ML", shortLabel: "Data Science" },
  { value: "product", label: "📈 Product Management", shortLabel: "Product" },
  { value: "design", label: "🎨 Design / UX", shortLabel: "Design" },
  { value: "marketing", label: "🚀 Marketing / Growth", shortLabel: "Marketing" },
];

const getJobDomainLabel = (value) => {
  const match = JOB_DOMAIN_OPTIONS.find((option) => option.value === value);
  return match ? match.shortLabel : "General";
};

const isValidDate = (value) => value instanceof Date && !Number.isNaN(value.getTime());

const formatAbsoluteDate = (date) => {
  if (!isValidDate(date)) return "Not available";
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
};

const formatRelativeTime = (date) => {
  if (!isValidDate(date)) return "—";
  const diffMs = Date.now() - date.getTime();
  const diffMinutes = Math.round(diffMs / 60000);
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.round(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
};

const parseFilePayload = (payload) => {
  if (!payload) return null;
  const uploadedAtSource = payload.uploadedAt || payload.upload_date || payload.uploadDate;
  const uploadedDate = uploadedAtSource ? new Date(uploadedAtSource) : null;
  return {
    ...payload,
    uploadedAt: isValidDate(uploadedDate) ? uploadedDate : null,
  };
};

const CARD_SURFACE =
  "bg-white dark:bg-[#1E1E2F] border border-gray-100 dark:border-gray-800 rounded-2xl hover:shadow-md transition-all duration-300";
const PANEL_SURFACE = `${CARD_SURFACE} shadow-lg transition-all duration-500`;

export default function Dashboard({ user }) {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [jobDomain, setJobDomain] = useState("");
  const [optimizedCV, setOptimizedCV] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [orderedSections, setOrderedSections] = useState([]);
  const [templateData, setTemplateData] = useState(null);
  const [atsScore, setAtsScore] = useState(null);
  const [recommendedKeywords, setRecommendedKeywords] = useState([]);
  const [foundKeywords, setFoundKeywords] = useState([]);
  const [groupedSuggestions, setGroupedSuggestions] = useState({});
  const [lastUploadedFileId, setLastUploadedFileId] = useState(null);
  const [lastUploadedFilename, setLastUploadedFilename] = useState(null);
  const [expandedPreview, setExpandedPreview] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("newest");
  const [chatbotCV, setChatbotCV] = useState(null);

  // Utility: truncate long filenames
  const truncateFilename = (filename = "", maxLen = 30) => {
    if (filename.length > maxLen) {
      return filename.substring(0, maxLen - 3) + "...";
    }
    return filename;
  };

  useEffect(() => {
    fetchFiles();
    fetchChatbotCV();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await api.get("/api/current-user");
      if (res.data.user) {
        setCurrentUser(res.data.user);
        const userFilesRes = await api.get("/api/user-files");
        const filesWithDate = (userFilesRes.data.files || [])
          .map((file) => parseFilePayload(file))
          .filter(Boolean);
        setFiles(filesWithDate);
      } else {
        setFiles([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchChatbotCV = async () => {
    try {
      const res = await api.get("/api/chatbot/cv-info");
      if (res.data.success && res.data.hasCV) {
        setChatbotCV(res.data.cv);
      } else {
        setChatbotCV(null);
      }
    } catch (err) {
      console.error("Error fetching chatbot CV:", err);
      setChatbotCV(null);
    }
  };

  const handleFileChange = (e) => setSelectedFile(e.target.files[0]);
  const fileInputRef = React.useRef(null);
  const onFileSelected = (file) => {
    setSelectedFile(file);
    setOptimizedCV("");
    setSuggestions([]);
    setGroupedSuggestions({});
    setOrderedSections([]);
    setAtsScore(null);
    setRecommendedKeywords([]);
    setFoundKeywords([]);
    setLastUploadedFileId(null);
    setLastUploadedFilename(null);
  };

  const accessibleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) onFileSelected(f);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // indicate drop is allowed
    e.dataTransfer.dropEffect = "copy";
    setDragActive(true);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (
      e.dataTransfer &&
      e.dataTransfer.files &&
      e.dataTransfer.files.length > 0
    ) {
      onFileSelected(e.dataTransfer.files[0]);
      e.dataTransfer.clearData();
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return alert("Select a file first!");
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("cv_file", selectedFile);
      if (jobDomain) {
        formData.append("job_domain", jobDomain);
      }
      // Let axios set the Content-Type including the boundary for multipart
      const res = await api.post("/api/upload-cv", formData);
      // backend now returns structured fields
      setOptimizedCV(res.data.optimized_text || res.data.optimized_cv || "");
      setSuggestions(res.data.suggestions || []);
      // prefer grouped suggestions if provided
      setGroupedSuggestions(res.data.grouped_suggestions || {});
      setOrderedSections(res.data.ordered_sections || []);
      setTemplateData(res.data.template_data || null);
      setAtsScore(res.data.ats_score ?? null);
      setRecommendedKeywords(res.data.recommended_keywords || []);
      setFoundKeywords(res.data.found_keywords || []);
      const parsedFile =
        parseFilePayload(res.data.file) ||
        parseFilePayload({
          _id: res.data.file_id,
          filename: selectedFile?.name || "Optimized CV.pdf",
          uploadedAt: new Date(),
          atsScore: res.data.ats_score ?? null,
          jobDomain,
        });
      if (parsedFile) {
        setFiles((prev) => {
          const withoutDuplicate = prev.filter((f) => f._id !== parsedFile._id);
          return [parsedFile, ...withoutDuplicate];
        });
      }
      setLastUploadedFileId(res.data.file_id);
      setLastUploadedFilename(parsedFile?.filename || selectedFile?.name || "optimized_cv.pdf");
      setSelectedFile(null);
      alert("CV uploaded and optimized successfully!");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || "Upload failed!");
    }
    setLoading(false);
  };

  const copyOptimized = async () => {
    try {
      await navigator.clipboard.writeText(optimizedCV);
      alert("Optimized CV copied to clipboard");
    } catch (e) {
      console.error(e);
      alert("Copy failed");
    }
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const res = await api.get(`/api/download/${fileId}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      alert("Download failed!");
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm("Are you sure you want to delete this CV?")) return;
    try {
      await api.delete(`/api/delete-cv/${fileId}`);
      setFiles((prev) => prev.filter((f) => f._id !== fileId));
      alert("CV deleted successfully!");
    } catch (err) {
      console.error(err);
      alert("Delete failed!");
    }
  };

  // Filter & Sort logic
  const getTimestamp = (file) =>
    file?.uploadedAt instanceof Date && !Number.isNaN(file.uploadedAt.getTime())
      ? file.uploadedAt.getTime()
      : 0;

  const filteredFiles = files
    .filter((f) => (f?.filename || "").toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      if (sortOption === "newest") return getTimestamp(b) - getTimestamp(a);
      if (sortOption === "oldest") return getTimestamp(a) - getTimestamp(b);
      if (sortOption === "alpha") return (a?.filename || "").localeCompare(b?.filename || "");
      return 0;
    });

  const dashboardStats = useMemo(() => {
    if (!files.length) {
      return {
        totalUploads: 0,
        bestScore: typeof atsScore === "number" ? atsScore : null,
        avgScore: typeof atsScore === "number" ? atsScore : null,
        lastUpload: null,
      };
    }
    const sortedByDate = [...files].sort((a, b) => getTimestamp(b) - getTimestamp(a));
    const lastUpload = sortedByDate[0] || null;
    const scoredFiles = files.filter((file) => typeof file.atsScore === "number");
    const bestScore = scoredFiles.reduce(
      (max, file) => Math.max(max, file.atsScore ?? 0),
      typeof atsScore === "number" ? atsScore : 0
    );
    const avgScore = scoredFiles.length
      ? Math.round(
          scoredFiles.reduce((sum, file) => sum + (file.atsScore || 0), 0) / scoredFiles.length
        )
      : typeof atsScore === "number"
      ? atsScore
      : null;
    return {
      totalUploads: files.length,
      bestScore: bestScore || null,
      avgScore: avgScore || null,
      lastUpload,
    };
  }, [files, atsScore]);

  const recentUploads = useMemo(() => {
    if (!files.length) return [];
    return [...files].sort((a, b) => getTimestamp(b) - getTimestamp(a)).slice(0, 4);
  }, [files]);

  const keywordInsight = useMemo(() => {
    const recommendedSet = new Set((recommendedKeywords || []).map((kw) => kw?.trim()).filter(Boolean));
    const foundSet = new Set((foundKeywords || []).map((kw) => kw?.trim()).filter(Boolean));
    if (!recommendedSet.size) {
      return { coverage: 0, matched: 0, missing: [], total: 0 };
    }
    const missing = [];
    let matched = 0;
    recommendedSet.forEach((kw) => {
      if (foundSet.has(kw)) {
        matched += 1;
      } else {
        missing.push(kw);
      }
    });
    const coverage = Math.round((matched / recommendedSet.size) * 100);
    return { coverage, matched, missing, total: recommendedSet.size };
  }, [recommendedKeywords, foundKeywords]);

  const totalSuggestions = useMemo(() => {
    if (groupedSuggestions && Object.keys(groupedSuggestions).length > 0) {
      return Object.values(groupedSuggestions).reduce(
        (sum, entries) => sum + (entries?.length || 0),
        0
      );
    }
    return suggestions?.length || 0;
  }, [groupedSuggestions, suggestions]);

  const readinessChecklist = [
    {
      label: "Optimized CV",
      done: Boolean(optimizedCV),
      detail: Boolean(optimizedCV) ? "Ready" : "Generate",
    },
    {
      label: "ATS score visibility",
      done: typeof atsScore === "number",
      detail: typeof atsScore === "number" ? `${atsScore}/100` : "Awaiting",
    },
    {
      label: "Keyword alignment",
      done: keywordInsight.total ? keywordInsight.coverage >= 70 : false,
      detail: keywordInsight.total
        ? `${keywordInsight.coverage}% match`
        : "Add target domain",
    },
    {
      label: "Suggestions addressed",
      done: totalSuggestions === 0,
      detail: totalSuggestions ? `${totalSuggestions} open` : "All set",
    },
  ];

  return (
    <div
      className="min-h-screen 
      bg-gradient-to-b from-[#F5F7FF] via-[#FFFBEA] to-[#E6EFFF]
      dark:from-[#0D1117] dark:via-[#161B22] dark:to-[#1E2329]
      transition-colors duration-500"
    >
      {/* <Navbar user={user} /> */}

      {/* Spacer for navbar */}
      <div className="h-16"></div>

      {/* Header with professional styling */}
      <header
        className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 dark:from-indigo-900 dark:via-purple-900 dark:to-pink-900
        text-white pt-12 pb-16 relative z-0 transition-colors duration-500"
      >
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1">
              <h1 className="text-4xl md:text-5xl font-bold mb-3">
                CV Dashboard
              </h1>
              <p className="text-lg md:text-xl mb-2 text-white/95">
                Upload, optimize, and manage your professional resume
              </p>
              <p className="text-md text-white/80">
                Welcome back, <span className="font-semibold">{user?.full_name || user?.username || user?.email || "User"}</span>
              </p>
            </div>
            <div className="hidden md:block flex-shrink-0">
              <img
                src={CvIllustration}
                alt="CV illustration"
                className="w-48 h-48 rounded-lg shadow-xl object-cover"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 md:px-6 py-8 relative z-10">
        {/* KPI Cards */}
        <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4 mb-10">
          <div className={`${CARD_SURFACE} p-6 shadow-sm h-full flex flex-col justify-between`}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl">
                <FaFileAlt className="text-indigo-500 text-xl" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">Total Uploads</span>
            </div>
            <div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{dashboardStats.totalUploads}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Your personal resume library</p>
            </div>
          </div>
          <div className={`${CARD_SURFACE} p-6 shadow-sm h-full flex flex-col justify-between`}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/30 rounded-xl">
                <FaStar className="text-yellow-500 text-xl" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">Best Score</span>
            </div>
            <div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {dashboardStats.bestScore ?? "—"}
                {dashboardStats.bestScore != null && <span className="text-lg text-gray-400 font-normal">/100</span>}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Highest performing optimized CV</p>
            </div>
          </div>
          <div className={`${CARD_SURFACE} p-6 shadow-sm h-full flex flex-col justify-between`}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-xl">
                <FaChartLine className="text-emerald-500 text-xl" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">Avg Score</span>
            </div>
            <div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {dashboardStats.avgScore ?? "—"}
                {dashboardStats.avgScore != null && <span className="text-lg text-gray-400 font-normal">/100</span>}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Across all uploaded resumes</p>
            </div>
          </div>
          <div className={`${CARD_SURFACE} p-6 shadow-sm h-full flex flex-col justify-between`}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-sky-50 dark:bg-sky-900/30 rounded-xl">
                <FaClock className="text-sky-500 text-xl" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">Last Activity</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1" title={formatAbsoluteDate(dashboardStats.lastUpload?.uploadedAt)}>
                {dashboardStats.lastUpload?.uploadedAt ? formatRelativeTime(dashboardStats.lastUpload.uploadedAt) : "Pending"}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {dashboardStats.lastUpload?.filename
                  ? truncateFilename(dashboardStats.lastUpload.filename, 20)
                  : "Upload a CV to get started"}
              </p>
            </div>
          </div>
        </section>

        {/* Chatbot CV Link */}
        {chatbotCV && (
          <section className="mb-8">
            <div className={`${CARD_SURFACE} p-6 shadow-md border-2 border-blue-200 dark:border-blue-800`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
                    <FaRobot className="text-white text-2xl" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                      <FaComments className="text-blue-500" />
                      Chatbot CV Analysis
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      <strong>{truncateFilename(chatbotCV.filename, 40)}</strong>
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Uploaded {chatbotCV.uploadedAt ? formatRelativeTime(new Date(chatbotCV.uploadedAt)) : 'recently'} • Ready for interactive chat
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => navigate('/chatbot')}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
                >
                  <FaComments />
                  Open Chat
                </button>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
                  <FaCheckCircle className="text-green-500" />
                  Your CV is loaded and ready for AI-powered conversations, improvements, and analysis
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Upload & Activity */}
        <section className="grid gap-6 lg:grid-cols-3 mb-8">
          <div className={`${PANEL_SURFACE} p-8 lg:col-span-2`}>
            <h2 className="text-2xl font-bold mb-6 text-indigo-600 dark:text-indigo-400 flex items-center gap-3">
              <FaUpload className="text-xl" /> Upload & Optimize CV
            </h2>
            <form onSubmit={handleUpload} className="space-y-6">
              <div className="grid gap-6 w-full lg:grid-cols-12 items-stretch">
                <label
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`lg:col-span-7 border-dashed border-2 
                  ${
                    dragActive
                      ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/40"
                      : "border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500"
                  } p-8 rounded-xl text-center cursor-pointer transition-all duration-200 flex flex-col justify-center min-h-[240px]`}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      fileInputRef.current?.click();
                    }
                  }}
                >
                  <div className="text-gray-600 dark:text-gray-300">
                    <div className="w-16 h-16 mx-auto mb-4 bg-indigo-100 dark:bg-indigo-900/50 rounded-full flex items-center justify-center">
                      <FaUpload className="text-2xl text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div className="font-semibold text-lg mb-2">
                      {selectedFile
                        ? truncateFilename(selectedFile.name, 40)
                        : dragActive
                        ? "Drop your CV here"
                        : "Drag & drop your CV here"}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      or click to select (.pdf, .doc, .docx)
                    </div>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={accessibleFileChange}
                    className="hidden"
                    accept=".pdf,.doc,.docx"
                    aria-label="Select CV file"
                  />
                </label>

                <div className="lg:col-span-5 w-full flex flex-col gap-4 justify-center">
                  <div className="bg-gray-50 dark:bg-gray-800/50 p-5 rounded-xl border border-gray-100 dark:border-gray-700">
                    <label className="flex items-center gap-2 text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
                      <FaBriefcase className="w-4 h-4 text-indigo-500" />
                      Target Job Domain
                    </label>
                    <div className="relative">
                      <select
                        value={jobDomain}
                        onChange={(e) => setJobDomain(e.target.value)}
                        className="w-full appearance-none p-3 pl-4 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#1f2937]
          text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 
          focus:border-transparent transition-all duration-200 hover:border-indigo-400 dark:hover:border-indigo-500 cursor-pointer font-medium"
                      >
                        {JOB_DOMAIN_OPTIONS.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-400 dark:text-gray-500">
                        <FaChevronDown className="w-4 h-4" />
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 leading-relaxed">
                      Selecting a focus helps our AI tailor your ATS score and keyword suggestions specifically for your industry.
                    </p>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-700 dark:to-purple-800 text-white px-6 py-4 rounded-xl 
                    hover:shadow-lg hover:from-indigo-700 hover:to-purple-700 dark:hover:from-indigo-800 dark:hover:to-purple-900
                    transition-all duration-200 flex items-center justify-center gap-3 font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:-translate-y-0.5"
                  >
                    {loading ? (
                      <>
                        <FaSpinner className="animate-spin" /> Processing...
                      </>
                    ) : (
                      <>
                        <FaUpload /> Upload & Optimize
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>

          <div className={`${PANEL_SURFACE} p-6 flex flex-col h-full`}>
            <div className="flex items-center justify-between gap-4 mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100">Recent Activity</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Track your last uploads and their ATS health.</p>
              </div>
              <button
                type="button"
                onClick={() =>
                  typeof window !== "undefined" &&
                  document.getElementById("user-cv-library")?.scrollIntoView({ behavior: "smooth" })
                }
                className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:underline shrink-0 transition-colors"
              >
                View library
              </button>
            </div>
            <div className="space-y-4 flex-1 overflow-y-auto max-h-[400px] pr-2 custom-scrollbar">
              {recentUploads.length > 0 ? (
                recentUploads.map((file) => (
                  <div
                    key={file._id}
                    className="flex items-start justify-between gap-4 rounded-xl border border-gray-100 dark:border-gray-800 p-4 bg-white/50 dark:bg-gray-900/30 hover:bg-white dark:hover:bg-gray-900/50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <FaFileAlt className="text-indigo-400 text-sm shrink-0" />
                        <p className="font-semibold text-gray-800 dark:text-gray-100 text-sm truncate" title={file.filename}>
                          {truncateFilename(file.filename, 28)}
                        </p>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 mt-1.5">
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700">
                          {getJobDomainLabel(file.jobDomain)}
                        </span>
                        {typeof file.atsScore === "number" && (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                            file.atsScore >= 70 
                              ? "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800" 
                              : file.atsScore >= 50
                              ? "bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800"
                              : "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800"
                          }`}>
                            {file.atsScore}/100
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap pt-0.5">
                      {formatRelativeTime(file.uploadedAt)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-xl">
                  <div className="w-12 h-12 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mb-3">
                    <FaFileAlt className="text-gray-300 dark:text-gray-600 text-xl" />
                  </div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">No uploads yet</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Your recent files will appear here</p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Optimized CV & Suggestions */}
        {optimizedCV && (
          <section className="mb-10">
            <div
              className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 
              border border-green-200 dark:border-green-700/50 p-6 
              rounded-2xl shadow-md mb-6 text-gray-800 dark:text-gray-200"
            >
              <div className="flex items-start justify-between gap-6">
                <div className="flex-1">
                  <h3 className="text-2xl font-bold mb-4 text-green-800 dark:text-green-400 flex items-center gap-2">
                    <FaCheckCircle className="text-xl" /> Optimized CV
                  </h3>
                  <div className="bg-white dark:bg-gray-900/50 p-4 rounded-lg border border-green-100 dark:border-green-800/50">
                    {/* Toggle between raw optimized text and organized preview */}
                    <div className="flex items-center justify-end mb-2">
                      <button
                        onClick={() => setExpandedPreview(!expandedPreview)}
                        className="text-xs px-3 py-1 rounded-md bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-200"
                      >
                        {expandedPreview ? "Show Raw" : "Show Preview"}
                      </button>
                    </div>

                    {!expandedPreview ? (
                      <pre className="whitespace-pre-wrap max-h-96 overflow-auto font-mono text-sm leading-relaxed">
                        {optimizedCV}
                      </pre>
                    ) : (
                      <div className="max-h-96 overflow-auto">
                        {templateData ? (
                          <ResumeTemplate data={templateData} />
                        ) : orderedSections && orderedSections.length > 0 ? (
                          <div className="space-y-4 text-sm text-gray-800 dark:text-gray-200">
                            {orderedSections.map((section) => (
                              <div key={section.key} className="border-l-4 border-indigo-400 pl-3">
                                <p className="text-xs font-semibold uppercase tracking-wide text-indigo-600 dark:text-indigo-300">
                                  <span>&mdash; {section.label} &mdash;</span>
                                </p>
                                <div className="mt-1 whitespace-pre-wrap leading-relaxed">
                                  {section.content}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-500">No structured preview available.</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div className="bg-white dark:bg-gray-900/50 rounded-xl p-5 border border-green-100 dark:border-green-800/50 min-w-max">
                  <div className="flex items-center justify-center gap-2 mb-3">
                    <FaStar className="text-yellow-500" />
                    <span className="text-sm font-semibold text-gray-600 dark:text-gray-300">
                      ATS Score
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-3">
                    <div
                      className={`bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full transition-all duration-300`}
                      style={{
                        width: `${Math.min(100, Math.max(0, atsScore || 0))}%`,
                      }}
                    />
                  </div>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400 text-center">{atsScore ?? "N/A"}<span className="text-sm">/100</span></p>
                  {recommendedKeywords.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-green-100 dark:border-green-800/50">
                      <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Key Words</p>
                      <div className="flex flex-wrap gap-1">
                        {recommendedKeywords.slice(0, 5).map((kw, i) => (
                          <span key={i} className="bg-green-100 dark:bg-green-800/40 text-green-700 dark:text-green-300 text-xs px-2 py-1 rounded-full">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {foundKeywords && foundKeywords.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-green-50 dark:border-green-900/20">
                      <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Found Keywords</p>
                      <div className="flex flex-wrap gap-1">
                        {foundKeywords.slice(0, 8).map((kw, i) => (
                          <span key={i} className="bg-gray-100 dark:bg-gray-800/30 text-gray-700 dark:text-gray-200 text-xs px-2 py-1 rounded-full">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {lastUploadedFileId && (
                    <button
                      onClick={() =>
                        handleDownload(
                          lastUploadedFileId,
                          lastUploadedFilename || "optimized_cv.pdf"
                        )
                      }
                      className="mt-4 w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-3 py-2 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2"
                    >
                      <FaDownload className="text-sm" /> Download PDF
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Structured sections preview */}
            {orderedSections && orderedSections.length > 0 && (
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {orderedSections.map(({ key, label, content }) => (
                  content ? (
                    <div
                      key={key}
                      className="bg-white dark:bg-gray-900/50 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all"
                    >
                      <h4 className="font-bold text-indigo-600 dark:text-indigo-400 mb-3 capitalize text-sm">
                        {label}
                      </h4>
                      <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap line-clamp-4 overflow-hidden">
                        {content}
                      </div>
                    </div>
                  ) : null
                ))}
              </div>
            )}

            {/* Suggestions list (grouped) */}
            {(Object.keys(groupedSuggestions).length > 0 ||
              (suggestions && suggestions.length > 0)) && (
              <div
                className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 
                border border-blue-200 dark:border-blue-700/50 p-6 
                rounded-2xl shadow-md text-gray-800 dark:text-gray-200"
              >
                <h3 className="text-xl font-bold mb-4 text-blue-800 dark:text-blue-400 flex items-center gap-2">
                  <FaExclamationCircle className="text-lg" /> Improvement Suggestions
                </h3>
                {/* Prefer groupedSuggestions if provided by backend */}
                {Object.keys(groupedSuggestions).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(groupedSuggestions).map(([cat, msgs]) => (
                      <div key={cat}>
                        <h4 className="font-semibold capitalize text-indigo-600">
                          {cat.replace("_", " ")}
                        </h4>
                        <ul className="list-disc pl-6 mt-1">
                          {msgs.map((m, i) => (
                            <li key={i} className="text-sm">
                              {m}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ul className="list-disc pl-6">
                    {suggestions.map((s, idx) => (
                      <li key={idx} className="mb-2">
                        <strong className="capitalize">
                          {s.category || "General"}:
                        </strong>{" "}
                        {s.message || s}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </section>
        )}

        {(keywordInsight.total > 0 || optimizedCV || typeof atsScore === "number" || totalSuggestions > 0) && (
          <section className="grid gap-6 lg:grid-cols-2 mb-10">
            {keywordInsight.total > 0 && (
              <div className={`${CARD_SURFACE} p-6 shadow-md h-full flex flex-col`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2 text-gray-800 dark:text-gray-100">
                    <FaChartLine className="text-indigo-500" />
                    <h3 className="text-lg font-bold">Keyword Coverage</h3>
                  </div>
                  <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-300">
                    {keywordInsight.coverage}% match
                  </span>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full"
                        style={{ width: `${keywordInsight.coverage}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      {keywordInsight.matched} of {keywordInsight.total} target keywords detected.
                    </p>
                  </div>
                  {keywordInsight.missing.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wide">
                        Suggested additions
                      </p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {keywordInsight.missing.slice(0, 6).map((kw) => (
                          <span
                            key={kw}
                            className="text-xs px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200"
                          >
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
            <div className={`${CARD_SURFACE} p-6 shadow-md h-full flex flex-col`}>
              <div className="flex items-center gap-2 text-gray-800 dark:text-gray-100 mb-4">
                <FaClipboardCheck className="text-emerald-500" />
                <h3 className="text-lg font-bold">Readiness Checklist</h3>
              </div>
              <ul className="space-y-3">
                {readinessChecklist.map((item) => (
                  <li
                    key={item.label}
                    className="flex items-center justify-between rounded-xl border border-gray-100 dark:border-gray-800 px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`w-2.5 h-2.5 rounded-full ${item.done ? "bg-emerald-400" : "bg-amber-400"}`}
                      ></span>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                        {item.label}
                      </span>
                    </div>
                    <span
                      className={`text-xs font-semibold ${item.done ? "text-emerald-500" : "text-amber-500"}`}
                    >
                      {item.detail}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}

        {/* Search & Sort */}
        <section className="mb-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div
            className="flex items-center gap-3 flex-1 border border-gray-300 dark:border-gray-600 
            rounded-lg px-4 py-3 bg-white dark:bg-[#1E1E2F] shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 transition-all"
          >
            <FaSearch className="text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search CVs by filename..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="outline-none w-full bg-transparent text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500"
            />
          </div>
          <div className="flex gap-3 w-full md:w-auto">
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
              className="flex-1 md:flex-none border border-gray-300 dark:border-gray-600 px-4 py-3 rounded-lg 
              bg-white dark:bg-[#1E1E2F] text-gray-700 dark:text-gray-200 font-medium focus:ring-2 focus:ring-indigo-500 transition-all"
            >
              <option value="newest">📅 Newest First</option>
              <option value="oldest">📅 Oldest First</option>
              <option value="alpha">🔤 A → Z</option>
            </select>
          </div>
        </section>

        {/* Uploaded CV Cards */}
        <section id="user-cv-library" className="mb-16">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-3">
              <FaFileAlt className="text-2xl" /> Your Uploaded CVs
              <span className="text-lg bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 px-3 py-1 rounded-full font-semibold">
                {filteredFiles.length}
              </span>
            </h2>
          </div>
          {filteredFiles.length === 0 ? (
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/30 dark:to-gray-800/30 rounded-2xl p-12 text-center border border-gray-200 dark:border-gray-700">
              <FaFileAlt className="mx-auto text-5xl text-gray-300 dark:text-gray-600 mb-4" />
              <p className="text-gray-500 dark:text-gray-400 text-lg font-medium">No CVs uploaded yet</p>
              <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Upload your first CV above to get started</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredFiles.map((file) => (
                <div
                  key={file._id}
                  className="bg-white dark:bg-[#1E1E2F] p-6 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 
                  flex flex-col justify-between text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-800 group h-full"
                >
                  <div className="mb-5">
                    <div className="flex items-start gap-4 mb-3">
                      <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl shrink-0 group-hover:scale-105 transition-transform">
                        <FaFileAlt className="text-indigo-500 text-xl" />
                      </div>
                      <div className="flex-1 min-w-0 pt-1">
                        <h3 className="font-bold text-lg truncate text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" title={file.filename}>
                          {truncateFilename(file.filename, 24)}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-2">
                          <span>{formatAbsoluteDate(file.uploadedAt)}</span>
                          <span>•</span>
                          <span>{(file.size / 1024).toFixed(0)} KB</span>
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mt-4">
                      <span className="text-xs font-medium px-2.5 py-1 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
                        {getJobDomainLabel(file.jobDomain)}
                      </span>
                      {typeof file.atsScore === "number" && (
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${
                          file.atsScore >= 70 
                            ? "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800" 
                            : file.atsScore >= 50
                            ? "bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800"
                            : "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800"
                        }`}>
                          ATS: {file.atsScore}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-3 pt-5 border-t border-gray-100 dark:border-gray-800 mt-auto">
                    <button
                      onClick={() => handleDownload(file._id, file.filename)}
                      className="flex-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 text-gray-700 dark:text-gray-200 px-4 py-2.5 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 font-semibold text-sm group/btn"
                    >
                      <FaDownload className="text-gray-400 group-hover/btn:text-indigo-500 transition-colors" /> Download
                    </button>
                    <button
                      onClick={() => handleDelete(file._id)}
                      className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-red-300 dark:hover:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-700 dark:text-gray-200 px-4 py-2.5 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 font-semibold text-sm group/btn"
                      aria-label="Delete file"
                    >
                      <FaTrash className="text-gray-400 group-hover/btn:text-red-500 transition-colors" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-gray-900 to-gray-950 dark:from-[#0D1117] dark:to-[#010409] text-gray-300 py-8 text-center transition-colors duration-500 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-4">
          <p className="text-sm">&copy; {new Date().getFullYear()} <span className="font-semibold text-indigo-400">PerfectCV</span>. All rights reserved.</p>
          <p className="text-xs text-gray-500 mt-2">Craft your perfect resume with AI-powered insights</p>
        </div>
      </footer>
    </div>
  );
}
