/**
 * Example Frontend Integration - React Component
 * Demonstrates how to use the CV Analysis API from a React application
 * 
 * CVAnalyzer.jsx - Complete React Component
 */

import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function CVAnalyzer() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');

  // Handle file selection
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.name.match(/\.(pdf|docx)$/i)) {
        setError('Please upload a PDF or DOCX file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  // Analyze CV
  const analyzeCV = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/cv/analyze-cv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAnalysis(response.data);
      setActiveTab('analysis');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze CV');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Score color based on value
  const getScoreColor = (score) => {
    if (score >= 71) return 'text-green-600';
    if (score >= 41) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Score interpretation
  const getScoreInterpretation = (score) => {
    if (score >= 71) return 'Excellent! Your resume is well-structured.';
    if (score >= 41) return 'Good, but there\'s room for improvement.';
    return 'Needs significant improvement.';
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">CV Analyzer</h1>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Upload Your CV</h2>
        <div className="flex items-center space-x-4">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
          <button
            onClick={analyzeCV}
            disabled={!file || loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md
              hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {analysis && (
        <div className="bg-white rounded-lg shadow-md">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {['analysis', 'recommendations', 'courses', 'videos'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Analysis Tab */}
            {activeTab === 'analysis' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">CV Analysis</h2>

                {/* Score Section */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-semibold">Resume Score</span>
                    <span className={`text-4xl font-bold ${getScoreColor(analysis.analysis.score)}`}>
                      {analysis.analysis.score}/100
                    </span>
                  </div>
                  <p className="text-gray-600">{getScoreInterpretation(analysis.analysis.score)}</p>
                  
                  {/* Progress Bar */}
                  <div className="mt-4 bg-gray-200 rounded-full h-4">
                    <div
                      className={`h-4 rounded-full ${
                        analysis.analysis.score >= 71
                          ? 'bg-green-500'
                          : analysis.analysis.score >= 41
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${analysis.analysis.score}%` }}
                    />
                  </div>
                </div>

                {/* Score Breakdown */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3">Score Breakdown</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(analysis.analysis.score_breakdown).map(([section, score]) => (
                      <div key={section} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                        <span className="capitalize">{section}</span>
                        <span className={`font-semibold ${score > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {score}/20
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key Information */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600">Career Field</p>
                    <p className="text-lg font-semibold text-blue-700">
                      {analysis.analysis.predicted_field}
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600">Experience Level</p>
                    <p className="text-lg font-semibold text-green-700">
                      {analysis.analysis.candidate_level}
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600">ATS Score</p>
                    <p className="text-lg font-semibold text-purple-700">
                      {analysis.ats.score}/100
                    </p>
                  </div>
                </div>

                {/* Sections Status */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-green-600">
                      ✓ Present Sections
                    </h3>
                    <ul className="space-y-2">
                      {analysis.analysis.present_sections.map((section, index) => (
                        <li key={index} className="flex items-center text-gray-700">
                          <span className="text-green-500 mr-2">✓</span>
                          {section}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-red-600">
                      ✗ Missing Sections
                    </h3>
                    {analysis.analysis.missing_sections.length > 0 ? (
                      <ul className="space-y-2">
                        {analysis.analysis.missing_sections.map((section, index) => (
                          <li key={index} className="flex items-center text-gray-700">
                            <span className="text-red-500 mr-2">✗</span>
                            {section}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-green-600">All sections present! 🎉</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations Tab */}
            {activeTab === 'recommendations' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Recommendations</h2>

                {/* Action Items */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3">Action Items</h3>
                  <div className="space-y-3">
                    {analysis.analysis.recommendations.map((rec, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border-l-4 ${
                          rec.type === 'critical'
                            ? 'bg-red-50 border-red-500'
                            : rec.type === 'warning'
                            ? 'bg-yellow-50 border-yellow-500'
                            : rec.type === 'success'
                            ? 'bg-green-50 border-green-500'
                            : 'bg-blue-50 border-blue-500'
                        }`}
                      >
                        <span className="font-semibold capitalize">{rec.type}: </span>
                        {rec.message}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended Skills */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3">
                    Recommended Skills to Add
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.analysis.recommended_skills.slice(0, 15).map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* ATS Tips */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">ATS Optimization Tips</h3>
                  <ul className="space-y-2">
                    {analysis.ats.optimization_tips.map((tip, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-500 mr-2 mt-1">💡</span>
                        <span className="text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Courses Tab */}
            {activeTab === 'courses' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Recommended Courses</h2>
                <p className="text-gray-600 mb-6">
                  Based on your skills and predicted field: {analysis.analysis.predicted_field}
                </p>

                <div className="grid grid-cols-1 gap-4">
                  {analysis.learning_resources.courses.map((course, index) => (
                    <div
                      key={index}
                      className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg mb-2">{course.name}</h3>
                          <a
                            href={course.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            View Course →
                          </a>
                        </div>
                        <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                          Course {index + 1}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Videos Tab */}
            {activeTab === 'videos' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Learning Videos</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Resume Tips */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-3">
                      📝 Resume Writing Tips
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {analysis.learning_resources.resume_tips_video.title}
                    </p>
                    <a
                      href={analysis.learning_resources.resume_tips_video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                      Watch on YouTube
                    </a>
                  </div>

                  {/* Interview Tips */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-3">
                      🎤 Interview Preparation
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {analysis.learning_resources.interview_tips_video.title}
                    </p>
                    <a
                      href={analysis.learning_resources.interview_tips_video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                      Watch on YouTube
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Additional Helper Component - Score Circle
export function ScoreCircle({ score, maxScore = 100, size = 120 }) {
  const percentage = (score / maxScore) * 100;
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  const getColor = () => {
    if (percentage >= 71) return '#10b981'; // green
    if (percentage >= 41) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  return (
    <svg width={size} height={size}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="#e5e7eb"
        strokeWidth="8"
        fill="none"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={getColor()}
        strokeWidth="8"
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dy=".3em"
        fontSize="24"
        fontWeight="bold"
        fill={getColor()}
      >
        {score}
      </text>
    </svg>
  );
}

// API Service Module
const API_SERVICE_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const cvAnalysisService = {
  // Analyze CV
  analyzeCV: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_SERVICE_BASE_URL}/cv/analyze-cv`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  },

  // Get recommendations
  getRecommendations: async (cvData) => {
    const response = await axios.post(`${API_SERVICE_BASE_URL}/cv/get-recommendations`, cvData);
    return response.data;
  },

  // Get courses by field
  getCoursesByField: async (field, numCourses = 5) => {
    const response = await axios.get(`${API_SERVICE_BASE_URL}/cv/courses/${field}`, {
      params: { num_courses: numCourses },
    });
    return response.data;
  },

  // Get learning videos
  getLearningVideos: async () => {
    const response = await axios.get(`${API_SERVICE_BASE_URL}/cv/learning-videos`);
    return response.data;
  },

  // Extract CV data
  extractCV: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_SERVICE_BASE_URL}/cv/extract-cv`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  },
};

// Default export
export default CVAnalyzer;
