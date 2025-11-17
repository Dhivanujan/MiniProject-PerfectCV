import React, { useState, useEffect } from "react";
import api from "../api";
import Navbar from "../components/Navbar";
import {
  FaUpload,
  FaDownload,
  FaTrash,
  FaFileAlt,
  FaSearch,
  FaCopy,
  FaSpinner,
  FaBriefcase,
  FaChevronDown,
  FaCheckCircle,
  FaExclamationCircle,
  FaStar,
} from "react-icons/fa";
import CvIllustration from "../assets/CV_Illustration.png";

export default function Dashboard({ user }) {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [jobDomain, setJobDomain] = useState("");
  const [optimizedCV, setOptimizedCV] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [sections, setSections] = useState({});
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

  // Utility: truncate long filenames
  const truncateFilename = (filename, maxLen = 30) => {
    if (filename.length > maxLen) {
      return filename.substring(0, maxLen - 3) + "...";
    }
    return filename;
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await api.get("/api/current-user");
      if (res.data.user) {
        setCurrentUser(res.data.user);
        const userFilesRes = await api.get("/api/user-files");
        const filesWithDate = userFilesRes.data.files.map((f) => ({
          ...f,
          uploadedAt: f.uploadedAt ? new Date(f.uploadedAt) : new Date(),
        }));
        setFiles(filesWithDate);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileChange = (e) => setSelectedFile(e.target.files[0]);
  const fileInputRef = React.useRef(null);
  const onFileSelected = (file) => {
    setSelectedFile(file);
    setOptimizedCV("");
    setSuggestions([]);
    setGroupedSuggestions({});
    setSections({});
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
      setSections(res.data.sections || {});
      setAtsScore(res.data.ats_score ?? null);
      setRecommendedKeywords(res.data.recommended_keywords || []);
      setFoundKeywords(res.data.found_keywords || []);
      setFiles([
        ...files,
        {
          _id: res.data.file_id,
          filename: selectedFile.name,
          uploadedAt: new Date(),
        },
      ]);
      setLastUploadedFileId(res.data.file_id);
      setLastUploadedFilename(selectedFile.name);
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
      setFiles(files.filter((f) => f._id !== fileId));
      alert("CV deleted successfully!");
    } catch (err) {
      console.error(err);
      alert("Delete failed!");
    }
  };

  // Filter & Sort logic
  const filteredFiles = files
    .filter((f) => f.filename.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      if (sortOption === "newest") return b.uploadedAt - a.uploadedAt;
      if (sortOption === "oldest") return a.uploadedAt - b.uploadedAt;
      if (sortOption === "alpha") return a.filename.localeCompare(b.filename);
      return 0;
    });

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
        {/* Upload Section */}
        <section
          className="bg-white dark:bg-[#1E1E2F] shadow-lg rounded-2xl p-8 mb-8
          transition-all duration-500 border border-gray-100 dark:border-gray-800"
        >
          <h2 className="text-2xl font-bold mb-6 text-indigo-600 dark:text-indigo-400 flex items-center gap-3">
            <FaUpload className="text-xl" /> Upload & Optimize CV
          </h2>
          <form
            onSubmit={handleUpload}
            className="flex flex-col md:flex-row gap-4 items-center justify-center"
          >
            <label
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`flex-1 border-dashed border-2 
              ${
                dragActive
                  ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/40"
                  : "border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500"
              } p-8 rounded-xl text-center 
              cursor-pointer transition-all duration-200`}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  fileInputRef.current?.click();
                }
              }}
            >
              <div className="text-gray-600 dark:text-gray-300">
                <FaUpload className="mx-auto mb-2 text-2xl text-indigo-500" />
                <div className="font-semibold text-sm mb-1">
                  {selectedFile
                    ? truncateFilename(selectedFile.name, 40)
                    : dragActive
                    ? "Drop your CV here"
                    : "Drag & drop your CV here"}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
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
            <div className="w-full md:w-72">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                <FaBriefcase className="w-4 h-4 text-indigo-500" />
                Target Job Domain
              </label>

              <div className="relative">
                <select
                  value={jobDomain}
                  onChange={(e) => setJobDomain(e.target.value)}
                  className="w-full appearance-none p-3 rounded-xl 
        border border-gray-300 dark:border-gray-600
        bg-white dark:bg-[#1f2937]
        text-gray-800 dark:text-gray-200
        focus:outline-none focus:ring-2 focus:ring-indigo-500 
        focus:border-transparent transition-all duration-200
        hover:border-indigo-400 dark:hover:border-indigo-500 cursor-pointer"
                >
                  <option value="">🌐 General</option>
                  <option value="software">💻 Software / Engineering</option>
                  <option value="data_science">📊 Data Science / ML</option>
                  <option value="product">📈 Product Management</option>
                  <option value="design">🎨 Design / UX</option>
                  <option value="marketing">🚀 Marketing / Growth</option>
                </select>

                {/* Custom dropdown arrow */}
                <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-400 dark:text-gray-500">
                  <FaChevronDown className="w-4 h-4" />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-700 dark:to-purple-800 text-white px-8 py-3 rounded-xl 
              hover:shadow-lg hover:from-indigo-700 hover:to-purple-700 dark:hover:from-indigo-800 dark:hover:to-purple-900
              transition-all duration-200 flex items-center gap-2 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <FaSpinner className="animate-spin" /> Uploading...
                </>
              ) : (
                <>
                  <FaUpload /> Upload & Optimize
                </>
              )}
            </button>
          </form>
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
                    <pre className="whitespace-pre-wrap max-h-96 overflow-auto font-mono text-sm leading-relaxed">
                      {optimizedCV}
                    </pre>
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
            {sections && Object.keys(sections).length > 0 && (
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {Object.entries(sections).map(([k, v]) =>
                  v ? (
                    <div
                      key={k}
                      className="bg-white dark:bg-gray-900/50 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all"
                    >
                      <h4 className="font-bold text-indigo-600 dark:text-indigo-400 mb-3 capitalize text-sm">
                        {k.replace("_", " ")}
                      </h4>
                      <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap line-clamp-4 overflow-hidden">
                        {v}
                      </div>
                    </div>
                  ) : null
                )}
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
        <section className="mb-16">
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
                  className="bg-white dark:bg-[#1E1E2F] p-6 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 
                  flex flex-col justify-between text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-800 group"
                >
                  <div className="mb-4">
                    <div className="flex items-start gap-3 mb-2">
                      <FaFileAlt className="text-indigo-500 text-xl flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-lg truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition" title={file.filename}>
                          {truncateFilename(file.filename, 28)}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {file.filename.split(".").pop()?.toUpperCase() || "FILE"} • {file.filename.length} chars
                        </p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      Uploaded by <span className="font-medium">{currentUser?.full_name ||
                        user?.full_name ||
                        currentUser?.username ||
                        user?.username ||
                        user?.email ||
                        "You"}</span>
                    </p>
                  </div>
                  <div className="flex gap-2 pt-4 border-t border-gray-100 dark:border-gray-700">
                    <button
                      onClick={() => handleDownload(file._id, file.filename)}
                      className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 dark:from-green-700 dark:to-emerald-700 dark:hover:from-green-800 dark:hover:to-emerald-800
                      text-white px-4 py-2 rounded-lg transition-all duration-200 flex-1 flex items-center justify-center gap-2 font-medium"
                    >
                      <FaDownload className="text-sm" /> Download
                    </button>
                    <button
                      onClick={() => handleDelete(file._id)}
                      className="bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 dark:from-red-700 dark:to-pink-700 dark:hover:from-red-800 dark:hover:to-pink-800
                      text-white px-4 py-2 rounded-lg transition-all duration-200 flex-1 flex items-center justify-center gap-2 font-medium"
                    >
                      <FaTrash className="text-sm" /> Delete
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
