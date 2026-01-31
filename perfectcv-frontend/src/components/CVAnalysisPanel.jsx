import React, { useState } from 'react';
import { 
  FaChartLine, FaBriefcase, FaStar, FaBookOpen, FaGraduationCap, 
  FaCheckCircle, FaExclamationTriangle, FaTrophy, FaLightbulb,
  FaRobot, FaSpinner, FaTimes
} from 'react-icons/fa';
import api from '../api';

const CVAnalysisPanel = ({ file, onClose }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const analyzeCV = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      const response = await fetch(file);
      const blob = await response.blob();
      formData.append('file', blob, file.name || 'cv.pdf');

      const res = await api.post('/api/cv/analyze-cv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAnalysis(res.data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze CV');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (file) {
      analyzeCV();
    }
  }, [file]);

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-emerald-600 dark:text-emerald-400';
    if (score >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getScoreBgColor = (score) => {
    if (score >= 70) return 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-700';
    if (score >= 50) return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700';
    return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700';
  };

  const getCandidateLevelBadge = (level) => {
    const badges = {
      'Junior': { color: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400', icon: '🌱' },
      'Mid-Level': { color: 'bg-sage-100 text-sage-700 dark:bg-sage-900/30 dark:text-sage-400', icon: '🚀' },
      'Senior': { color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400', icon: '⭐' },
      'Expert': { color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', icon: '🏆' }
    };
    
    const badge = badges[level] || badges['Junior'];
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}>
        {badge.icon} {level}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
          <div className="text-center">
            <FaSpinner className="animate-spin text-sage-600 dark:text-sage-400 text-5xl mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-2">
              Analyzing Your CV
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Using AI to evaluate your resume...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
          <div className="text-center">
            <FaExclamationTriangle className="text-red-500 text-5xl mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-2">
              Analysis Failed
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-sage-600 hover:bg-sage-700 text-white rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FaChartLine },
    { id: 'ats', label: 'ATS Score', icon: FaRobot },
    { id: 'courses', label: 'Learning', icon: FaBookOpen },
    { id: 'recommendations', label: 'Tips', icon: FaLightbulb }
  ];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-6xl w-full my-8 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 flex items-center gap-3">
              <FaChartLine className="text-sage-600 dark:text-sage-400" />
              CV Analysis Report
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Comprehensive analysis of your resume
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <FaTimes className="text-gray-600 dark:text-gray-400 text-xl" />
          </button>
        </div>

        {/* Score Overview - Always Visible */}
        <div className="p-6 bg-gradient-to-br from-sage-50 to-green-50 dark:from-sage-900/20 dark:to-green-900/20 border-b border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Overall Score */}
            <div className={`${getScoreBgColor(analysis.analysis?.score || 0)} rounded-xl p-6 border`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Overall Score</span>
                <FaStar className={getScoreColor(analysis.analysis?.score || 0)} />
              </div>
              <div className={`text-4xl font-bold ${getScoreColor(analysis.analysis?.score || 0)}`}>
                {analysis.analysis?.score || 0}/{analysis.analysis?.max_score || 100}
              </div>
              <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                {analysis.analysis?.candidate_level || 'Not Available'}
              </div>
            </div>

            {/* ATS Score */}
            <div className={`${getScoreBgColor(analysis.ats?.percentage || 0)} rounded-xl p-6 border`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">ATS Compatibility</span>
                <FaRobot className={getScoreColor(analysis.ats?.percentage || 0)} />
              </div>
              <div className={`text-4xl font-bold ${getScoreColor(analysis.ats?.percentage || 0)}`}>
                {analysis.ats?.percentage || 0}%
              </div>
              <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                {analysis.ats?.score || 0} points
              </div>
            </div>

            {/* Predicted Field */}
            <div className="bg-white dark:bg-gray-700/50 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Career Field</span>
                <FaBriefcase className="text-sage-600 dark:text-sage-400" />
              </div>
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-2">
                {analysis.analysis?.predicted_field || 'General'}
              </div>
              <div className="mt-2">
                {getCandidateLevelBadge(analysis.analysis?.candidate_level || 'Junior')}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 px-6 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 font-semibold text-sm transition-colors border-b-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-sage-600 text-sage-600 dark:text-sage-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                <Icon />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6 max-h-[500px] overflow-y-auto">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Score Breakdown */}
              <div>
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <FaTrophy className="text-yellow-500" />
                  Score Breakdown
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(analysis.analysis?.score_breakdown || {}).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="text-sm font-bold text-sage-600 dark:text-sage-400">
                          {value} pts
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-sage-600 dark:bg-sage-500 h-2 rounded-full transition-all"
                          style={{ width: `${(value / 20) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sections Status */}
              <div className="grid md:grid-cols-2 gap-4">
                {/* Present Sections */}
                <div>
                  <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                    <FaCheckCircle className="text-emerald-500" />
                    Present Sections
                  </h3>
                  <div className="space-y-2">
                    {analysis.analysis?.present_sections?.map((section, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 bg-emerald-50 dark:bg-emerald-900/20 p-2 rounded-lg">
                        <FaCheckCircle className="text-emerald-500 text-xs" />
                        {section}
                      </div>
                    )) || <p className="text-sm text-gray-500 dark:text-gray-400">No data available</p>}
                  </div>
                </div>

                {/* Missing Sections */}
                <div>
                  <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                    <FaExclamationTriangle className="text-amber-500" />
                    Missing Sections
                  </h3>
                  <div className="space-y-2">
                    {analysis.analysis?.missing_sections?.map((section, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 bg-amber-50 dark:bg-amber-900/20 p-2 rounded-lg">
                        <FaExclamationTriangle className="text-amber-500 text-xs" />
                        {section}
                      </div>
                    )) || <p className="text-sm text-emerald-600 dark:text-emerald-400">All sections present!</p>}
                  </div>
                </div>
              </div>

              {/* Recommended Skills */}
              {analysis.analysis?.recommended_skills && analysis.analysis.recommended_skills.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                    <FaLightbulb className="text-yellow-500" />
                    Recommended Skills to Add
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.analysis.recommended_skills.slice(0, 20).map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-sage-50 dark:bg-sage-900/30 text-sage-700 dark:text-sage-300 rounded-lg text-sm font-medium border border-sage-200 dark:border-sage-700"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ATS Tab */}
          {activeTab === 'ats' && (
            <div className="space-y-6">
              {/* ATS Suggestions */}
              <div>
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <FaRobot className="text-sage-600 dark:text-sage-400" />
                  ATS Optimization Suggestions
                </h3>
                <div className="space-y-3">
                  {analysis.ats?.suggestions?.map((suggestion, idx) => (
                    <div key={idx} className="bg-sage-50 dark:bg-sage-900/20 border border-sage-200 dark:border-sage-700 rounded-lg p-4">
                      <p className="text-sm text-gray-700 dark:text-gray-300">{suggestion}</p>
                    </div>
                  )) || <p className="text-sm text-gray-500 dark:text-gray-400">No suggestions available</p>}
                </div>
              </div>

              {/* ATS Tips */}
              {analysis.ats?.optimization_tips && (
                <div>
                  <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                    <FaLightbulb className="text-yellow-500" />
                    Optimization Tips
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(analysis.ats.optimization_tips).map(([key, tips]) => (
                      <div key={key} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-800 dark:text-gray-100 mb-2 capitalize">
                          {key.replace(/_/g, ' ')}
                        </h4>
                        <ul className="space-y-1">
                          {(Array.isArray(tips) ? tips : [tips]).map((tip, idx) => (
                            <li key={idx} className="text-sm text-gray-700 dark:text-gray-300 flex gap-2">
                              <span className="text-sage-500">•</span>
                              <span>{tip}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Courses Tab */}
          {activeTab === 'courses' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <FaGraduationCap className="text-sage-600 dark:text-sage-400" />
                  Recommended Learning Resources
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Based on your {analysis.analysis?.predicted_field || 'career'} field
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.learning_resources?.map((course, idx) => (
                    <div key={idx} className="bg-gradient-to-br from-sage-50 to-green-50 dark:from-sage-900/20 dark:to-green-900/20 border border-sage-200 dark:border-sage-700 rounded-xl p-4 hover:shadow-lg transition-all">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-sage-100 dark:bg-sage-800 rounded-lg">
                          <FaBookOpen className="text-sage-600 dark:text-sage-400" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-bold text-gray-800 dark:text-gray-100 mb-1">
                            {course.title || course.name || 'Course'}
                          </h4>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                            {course.provider || course.platform || 'Online Course'}
                          </p>
                          {course.url && (
                            <a
                              href={course.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-sage-600 dark:text-sage-400 hover:underline font-medium"
                            >
                              View Course →
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  )) || <p className="text-sm text-gray-500 dark:text-gray-400">No courses available</p>}
                </div>
              </div>
            </div>
          )}

          {/* Recommendations Tab */}
          {activeTab === 'recommendations' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <FaLightbulb className="text-yellow-500" />
                  Personalized Recommendations
                </h3>
                <div className="space-y-3">
                  {analysis.analysis?.recommendations?.map((rec, idx) => (
                    <div key={idx} className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
                      <div className="flex gap-3">
                        <FaLightbulb className="text-yellow-500 mt-1 flex-shrink-0" />
                        <p className="text-sm text-gray-700 dark:text-gray-300">{rec}</p>
                      </div>
                    </div>
                  )) || <p className="text-sm text-gray-500 dark:text-gray-400">No recommendations available</p>}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Analysis completed at {analysis.analysis?.timestamp || new Date().toLocaleString()}
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-sage-600 hover:bg-sage-700 dark:bg-sage-700 dark:hover:bg-sage-600 text-white rounded-lg transition-colors font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default CVAnalysisPanel;
