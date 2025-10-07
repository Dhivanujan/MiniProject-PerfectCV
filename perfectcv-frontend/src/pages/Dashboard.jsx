import React, { useState, useEffect } from "react";
import api from "../api";
import Navbar from "../components/Navbar";
import { FaUpload, FaDownload, FaTrash, FaFileAlt, FaSearch } from "react-icons/fa";
import CvIllustration from "../assets/CV_Illustration.png";

export default function Dashboard({ user }) {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [optimizedCV, setOptimizedCV] = useState("");
  const [suggestions, setSuggestions] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("newest");

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await api.get("/api/current-user");
      if (res.data.user) {
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

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return alert("Select a file first!");
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("cv_file", selectedFile);
      const res = await api.post("/api/upload-cv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setOptimizedCV(res.data.optimized_cv);
      setSuggestions(res.data.suggestions);
      setFiles([
        ...files,
        { _id: res.data.file_id, filename: selectedFile.name, uploadedAt: new Date() },
      ]);
      setSelectedFile(null);
      alert("CV uploaded and optimized successfully!");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || "Upload failed!");
    }
    setLoading(false);
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const res = await api.get(`/api/download/${fileId}`, { responseType: "blob" });
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

      {/* Header */}
      <header
        className="bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-800 dark:to-purple-900 
        text-white pt-24 pb-32 relative z-0 -mt-16 transition-colors duration-500"
      >
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">PerfectCV Dashboard</h1>
          <p className="text-lg md:text-xl mb-6">
            Upload, optimize, and enhance your CV to impress recruiters!
          </p>
          <img
            src={CvIllustration}
            alt="CV illustration"
            className="mx-auto w-64 md:w-96 rounded-lg shadow-lg"
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 md:px-6 -mt-32 relative z-10">
        {/* Upload Section */}
        <section
          className="bg-white dark:bg-[#1E1E2F] shadow-lg rounded-xl p-6 mb-8
          transition-all duration-500"
        >
          <h2 className="text-2xl font-bold mb-4 text-indigo-600 dark:text-indigo-400 flex items-center gap-2">
            <FaUpload /> Upload & Optimize CV
          </h2>
          <form
            onSubmit={handleUpload}
            className="flex flex-col md:flex-row gap-4 items-center justify-center"
          >
            <label
              className="w-full md:w-auto border-dashed border-2 
              border-gray-300 dark:border-gray-600 p-6 rounded-lg text-center 
              cursor-pointer hover:border-indigo-500 dark:hover:border-indigo-400 
              text-gray-600 dark:text-gray-300 transition-all"
            >
              {selectedFile
                ? selectedFile.name
                : "Drag & drop or click to select a CV (.pdf, .doc, .docx)"}
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                accept=".pdf,.doc,.docx"
              />
            </label>
            <button
              type="submit"
              disabled={loading}
              className="bg-indigo-600 dark:bg-indigo-700 text-white px-6 py-3 rounded-xl 
              hover:bg-indigo-700 dark:hover:bg-indigo-800 transition flex items-center gap-2"
            >
              {loading ? "Uploading..." : "Upload & Optimize"}
            </button>
          </form>
        </section>

        {/* Optimized CV & Suggestions */}
        {optimizedCV && (
          <section className="mb-6">
            <div
              className="bg-green-50 dark:bg-green-900/30 border-l-4 border-green-600 p-4 
              rounded-xl shadow-md mb-4 text-gray-800 dark:text-gray-200"
            >
              <h3 className="text-xl font-semibold mb-2 text-green-800 dark:text-green-400 flex items-center gap-2">
                <FaFileAlt /> Optimized CV
              </h3>
              <pre className="whitespace-pre-wrap">{optimizedCV}</pre>
            </div>
            {suggestions && (
              <div
                className="bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-600 p-4 
                rounded-xl shadow-md text-gray-800 dark:text-gray-200"
              >
                <h3 className="text-xl font-semibold mb-2 text-blue-800 dark:text-blue-400 flex items-center gap-2">
                  Suggestions for Improvement
                </h3>
                <pre className="whitespace-pre-wrap">{suggestions}</pre>
              </div>
            )}
          </section>
        )}

        {/* Search & Sort */}
        <section className="mb-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div
            className="flex items-center gap-2 w-full md:w-1/2 border border-gray-300 dark:border-gray-600 
            rounded px-2 py-1 bg-white dark:bg-[#1E1E2F] shadow text-gray-700 dark:text-gray-200"
          >
            <FaSearch className="text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search by filename..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="outline-none w-full bg-transparent text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500"
            />
          </div>
          <select
            value={sortOption}
            onChange={(e) => setSortOption(e.target.value)}
            className="border border-gray-300 dark:border-gray-600 p-2 rounded 
            w-full md:w-1/4 bg-white dark:bg-[#1E1E2F] text-gray-700 dark:text-gray-200"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="alpha">A → Z</option>
          </select>
        </section>

        {/* Uploaded CV Cards */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-indigo-600 dark:text-indigo-400 flex items-center gap-2">
            <FaFileAlt /> Your Uploaded CVs
          </h2>
          {filteredFiles.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">No CVs found.</p>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredFiles.map((file) => (
                <div
                  key={file._id}
                  className="bg-white dark:bg-[#1E1E2F] p-4 rounded-xl shadow hover:shadow-lg transition 
                  flex flex-col justify-between text-gray-800 dark:text-gray-200"
                >
                  <div>
                    <h3 className="text-lg font-semibold mb-1">{file.filename}</h3>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      Uploaded by {user.full_name}
                    </p>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleDownload(file._id, file.filename)}
                      className="bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800
                      text-white px-3 py-2 rounded-lg transition flex-1 flex items-center justify-center gap-2"
                    >
                      <FaDownload /> Download
                    </button>
                    <button
                      onClick={() => handleDelete(file._id)}
                      className="bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800
                      text-white px-3 py-2 rounded-lg transition flex-1 flex items-center justify-center gap-2"
                    >
                      <FaTrash /> Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 dark:bg-[#111827] text-white py-6 text-center transition-colors duration-500">
        <p>&copy; {new Date().getFullYear()} PerfectCV. All rights reserved.</p>
      </footer>
    </div>
  );
}
