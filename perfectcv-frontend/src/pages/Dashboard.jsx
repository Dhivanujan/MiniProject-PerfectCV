import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import Navbar from "../components/Navbar";
import CVAnalysisPanel from "../components/CVAnalysisPanel";
import ConfirmationModal from "../components/ConfirmationModal";
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
  FaUser,
  FaEnvelope,
  FaPhone,
  FaMapMarkerAlt,
  FaGraduationCap,
  FaCode,
  FaCertificate,
  FaTrophy,
  FaLanguage,
  FaProjectDiagram,
  FaHeart,
  FaHandsHelping,
  FaBook,
  FaWrench,
  FaUsers,
  FaLink,
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

// Helper function to safely parse JSON-like strings
const parseContentSafely = (content) => {
  if (!content) return null;
  if (typeof content !== 'string') return content;
  
  // If it doesn't look like JSON, return as-is
  const trimmed = content.trim();
  if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) {
    return content;
  }
  
  try {
    // Try multiple parsing strategies
    
    // Strategy 1: Replace single quotes with double quotes
    let jsonStr = content.replace(/'/g, '"');
    
    // Strategy 2: Handle Python None, True, False
    jsonStr = jsonStr.replace(/\bNone\b/g, 'null');
    jsonStr = jsonStr.replace(/\bTrue\b/g, 'true');
    jsonStr = jsonStr.replace(/\bFalse\b/g, 'false');
    
    // Strategy 3: Fix trailing commas
    jsonStr = jsonStr.replace(/,(\s*[}\]])/g, '$1');
    
    return JSON.parse(jsonStr);
  } catch (e) {
    // If parsing fails, return original content
    return content;
  }
};

// Component to render Skills section
const SkillsRenderer = ({ content }) => {
  const skillsData = parseContentSafely(content);
  
  if (!skillsData || typeof skillsData !== 'object') {
    // If it's a plain string with skills, try to display it nicely
    if (typeof content === 'string' && content.trim()) {
      const skills = content.split(/[,\n]/).map(s => s.trim()).filter(s => s);
      if (skills.length > 0) {
        return (
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, idx) => (
              <span 
                key={idx}
                className="text-xs px-3 py-1.5 bg-sage-50 dark:bg-sage-900/30 text-sage-700 dark:text-sage-300 rounded-lg border border-sage-200 dark:border-sage-700"
              >
                {skill}
              </span>
            ))}
          </div>
        );
      }
    }
    return <div className="text-sm text-gray-600 dark:text-gray-400">{content}</div>;
  }

  const categories = Object.entries(skillsData).filter(([key, value]) => 
    Array.isArray(value) && value.length > 0
  );

  if (categories.length === 0) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No skills listed</div>;
  }

  return (
    <div className="space-y-4">
      {categories.map(([category, skills]) => (
        <div key={category}>
          <h5 className="text-sm font-semibold text-sage-700 dark:text-sage-300 capitalize mb-2">
            {category.replace('_', ' ')} Skills
          </h5>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, idx) => {
              // Remove bullet points from skill names
              const cleanSkill = skill.replace(/^[•\-]\s*/, '').trim();
              return (
                <span 
                  key={idx}
                  className="text-xs px-3 py-1.5 bg-sage-50 dark:bg-sage-900/30 text-sage-700 dark:text-sage-300 rounded-lg border border-sage-200 dark:border-sage-700"
                >
                  {cleanSkill}
                </span>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

// Component to render Work Experience section
const WorkExperienceRenderer = ({ content }) => {
  let experienceData = parseContentSafely(content);
  
  if (!experienceData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No work experience listed</div>;
  }

  // Ensure it's an array
  if (!Array.isArray(experienceData)) {
    experienceData = [experienceData];
  }

  // Filter out invalid entries
  experienceData = experienceData.filter(job => {
    if (typeof job === 'string') return false;
    if (!job || typeof job !== 'object') return false;
    // Must have at least title or company
    return job.title || job.position || job.company;
  });

  if (experienceData.length === 0) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No work experience listed</div>;
  }

  return (
    <div className="space-y-4">
      {experienceData.map((job, idx) => (
        <div key={idx} className="pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2 mb-2">
            <div>
              <h5 className="text-base font-bold text-gray-900 dark:text-gray-100">
                {job.title || job.position || 'Position'}
              </h5>
              <p className="text-sm font-medium text-sage-600 dark:text-sage-400">
                {job.company || 'Company'}
              </p>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
              {job.dates || job.start_date || job.date || ''}
              {job.is_current && ' - Present'}
            </div>
          </div>
          {job.location && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">📍 {job.location}</p>
          )}
          {job.description && (
            <div className="text-sm text-gray-700 dark:text-gray-300 mt-2">
              {typeof job.description === 'string' ? (
                job.description.split('\n').map((line, i) => {
                  const trimmed = line.trim();
                  if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
                    return (
                      <div key={i} className="flex gap-2 mb-1">
                        <span className="text-sage-500">•</span>
                        <span>{trimmed.replace(/^[-•]\s*/, '')}</span>
                      </div>
                    );
                  }
                  return trimmed ? <p key={i} className="mb-1">{trimmed}</p> : null;
                })
              ) : Array.isArray(job.description) ? (
                job.description.map((point, i) => (
                  <div key={i} className="flex gap-2 mb-1">
                    <span className="text-sage-500">•</span>
                    <span>{point}</span>
                  </div>
                ))
              ) : null}
            </div>
          )}
          {job.achievements && Array.isArray(job.achievements) && job.achievements.length > 0 && (
            <div className="text-sm text-gray-700 dark:text-gray-300 mt-2">
              {job.achievements.map((achievement, i) => (
                <div key={i} className="flex gap-2 mb-1">
                  <span className="text-sage-500">•</span>
                  <span>{achievement}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// Component to render Education section
const EducationRenderer = ({ content }) => {
  let educationData = parseContentSafely(content);
  
  if (!educationData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No education listed</div>;
  }

  // Ensure it's an array
  if (!Array.isArray(educationData)) {
    educationData = [educationData];
  }

  // Filter out invalid/incomplete entries (like standalone "GPA:", "3.8/", etc.)
  educationData = educationData.filter(edu => {
    if (typeof edu === 'string') return false; // Skip raw strings
    if (!edu || typeof edu !== 'object') return false;
    // Must have at least degree or institution
    return edu.degree || edu.institution || edu.school;
  });

  if (educationData.length === 0) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No education listed</div>;
  }

  return (
    <div className="space-y-4">
      {educationData.map((edu, idx) => (
        <div key={idx} className="pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
            <div>
              <h5 className="text-base font-bold text-gray-900 dark:text-gray-100">
                {edu.degree || 'Degree'}
                {edu.field && ` in ${edu.field}`}
              </h5>
              <p className="text-sm font-medium text-sage-600 dark:text-sage-400">
                {edu.institution || edu.school || 'Institution'}
              </p>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
              {edu.graduation_date || edu.year || edu.date || ''}
            </div>
          </div>
          {edu.location && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">📍 {edu.location}</p>
          )}
          {edu.gpa && (
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">GPA: {edu.gpa}</p>
          )}
          {edu.honors && edu.honors.length > 0 && (
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              🏆 {Array.isArray(edu.honors) ? edu.honors.join(', ') : edu.honors}
            </p>
          )}
        </div>
      ))}
    </div>
  );
};

// Component to render Certifications section
const CertificationsRenderer = ({ content }) => {
  let certData = parseContentSafely(content);
  
  if (!certData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No certifications listed</div>;
  }

  // Ensure it's an array
  if (!Array.isArray(certData)) {
    // If it's a plain string, try to split by newlines
    if (typeof certData === 'string') {
      const items = certData.split('\n').map(s => s.trim()).filter(s => s);
      if (items.length > 0) {
        certData = items.map(item => ({ name: item }));
      } else {
        certData = [certData];
      }
    } else {
      certData = [certData];
    }
  }

  // Filter out invalid entries
  certData = certData.filter(cert => {
    if (typeof cert === 'string') return cert.trim().length > 0;
    if (!cert || typeof cert !== 'object') return false;
    return cert.name || cert.title;
  });

  return (
    <div className="space-y-3">
      {certData.map((cert, idx) => {
        // Handle string items
        if (typeof cert === 'string') {
          return (
            <div key={idx} className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
              <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {cert}
              </h5>
            </div>
          );
        }
        
        // Handle object items
        return (
          <div key={idx} className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  {cert.name || cert.title || 'Certification'}
                </h5>
                {(cert.issuer || cert.organization) && (
                  <p className="text-xs text-sage-600 dark:text-sage-400 mt-0.5">
                    {cert.issuer || cert.organization}
                  </p>
                )}
              </div>
              {cert.date && (
                <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {cert.date}
                </span>
              )}
            </div>
            {cert.credential_id && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                ID: {cert.credential_id}
              </p>
            )}
            {cert.url && (
              <a 
                href={cert.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-sage-600 dark:text-sage-400 hover:underline mt-1 inline-block"
              >
                View credential →
              </a>
            )}
          </div>
        );
      })}
    </div>
  );
};

// Component to render Projects section
const ProjectsRenderer = ({ content }) => {
  let projectsData = parseContentSafely(content);
  
  if (!projectsData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No projects listed</div>;
  }

  // Ensure it's an array
  if (!Array.isArray(projectsData)) {
    // If it's a single project object
    if (typeof projectsData === 'object' && projectsData !== null) {
      projectsData = [projectsData];
    } else if (typeof projectsData === 'string') {
      // Split by newlines for plain text
      const items = projectsData.split('\n').map(s => s.trim()).filter(s => s);
      if (items.length > 0) {
        projectsData = items.map(item => ({ name: item }));
      } else {
        projectsData = [{ name: projectsData }];
      }
    } else {
      projectsData = [];
    }
  }

  // Filter out invalid entries
  projectsData = projectsData.filter(proj => {
    if (typeof proj === 'string') return proj.trim().length > 0;
    if (!proj || typeof proj !== 'object') return false;
    return proj.name || proj.title;
  });

  if (projectsData.length === 0) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No projects listed</div>;
  }

  return (
    <div className="space-y-4">
      {projectsData.map((proj, idx) => {
        // Handle string items
        if (typeof proj === 'string') {
          return (
            <div key={idx} className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
              <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {proj}
              </h5>
            </div>
          );
        }
        
        // Handle object items
        return (
          <div key={idx} className="pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <h5 className="text-sm font-bold text-gray-900 dark:text-gray-100">
                  {proj.name || proj.title || 'Project'}
                </h5>
                {proj.role && (
                  <p className="text-xs text-sage-600 dark:text-sage-400 mt-0.5">
                    {proj.role}
                  </p>
                )}
              </div>
              {(proj.date || proj.duration) && (
                <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {proj.date || proj.duration}
                </span>
              )}
            </div>
            {(proj.description || proj.desc) && (
              <p className="text-xs text-gray-600 dark:text-gray-300 mt-2 leading-relaxed">
                {proj.description || proj.desc}
              </p>
            )}
            {proj.technologies && (
              <div className="mt-2 flex flex-wrap gap-1">
                {(Array.isArray(proj.technologies) ? proj.technologies : proj.technologies.split(',').map(t => t.trim())).map((tech, techIdx) => (
                  <span 
                    key={techIdx}
                    className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-0.5 rounded"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            )}
            {proj.url && (
              <a 
                href={proj.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-sage-600 dark:text-sage-400 hover:underline mt-2 inline-block"
              >
                View project →
              </a>
            )}
          </div>
        );
      })}
    </div>
  );
};

// Component to render Achievements section
const AchievementsRenderer = ({ content }) => {
  let achievementData = parseContentSafely(content);
  
  if (!achievementData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No achievements listed</div>;
  }

  // Ensure it's an array
  if (!Array.isArray(achievementData)) {
    if (typeof achievementData === 'string') {
      const items = achievementData.split('\n').map(s => s.trim()).filter(s => s);
      achievementData = items.map(item => ({ title: item }));
    } else if (typeof achievementData === 'object') {
      achievementData = [achievementData];
    } else {
      achievementData = [];
    }
  }

  return (
    <div className="space-y-3">
      {achievementData.map((achievement, idx) => {
        if (typeof achievement === 'string') {
          return (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-yellow-500">🏆</span>
              <span className="text-sm text-gray-700 dark:text-gray-300">{achievement}</span>
            </div>
          );
        }
        return (
          <div key={idx} className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
            <div className="flex items-start gap-2">
              <span className="text-yellow-500">🏆</span>
              <div className="flex-1">
                <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  {achievement.title || achievement.name || 'Achievement'}
                </h5>
                {achievement.issuer && (
                  <p className="text-xs text-sage-600 dark:text-sage-400">{achievement.issuer}</p>
                )}
                {achievement.date && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">{achievement.date}</p>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Component to render Publications section
const PublicationsRenderer = ({ content }) => {
  let pubData = parseContentSafely(content);
  
  if (!pubData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No publications listed</div>;
  }

  if (!Array.isArray(pubData)) {
    if (typeof pubData === 'string') {
      const items = pubData.split('\n').map(s => s.trim()).filter(s => s);
      pubData = items.map(item => ({ title: item }));
    } else {
      pubData = [pubData];
    }
  }

  return (
    <div className="space-y-3">
      {pubData.map((pub, idx) => {
        if (typeof pub === 'string') {
          return (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-blue-500">📄</span>
              <span className="text-sm text-gray-700 dark:text-gray-300">{pub}</span>
            </div>
          );
        }
        return (
          <div key={idx} className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
            <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {pub.title || 'Publication'}
            </h5>
            {pub.authors && <p className="text-xs text-gray-600 dark:text-gray-400">{pub.authors}</p>}
            {pub.venue && <p className="text-xs text-sage-600 dark:text-sage-400">{pub.venue}</p>}
            {pub.date && <p className="text-xs text-gray-500 dark:text-gray-400">{pub.date}</p>}
            {pub.url && (
              <a href={pub.url} target="_blank" rel="noopener noreferrer" className="text-xs text-sage-600 dark:text-sage-400 hover:underline">
                View publication →
              </a>
            )}
          </div>
        );
      })}
    </div>
  );
};

// Component to render Languages section
const LanguagesRenderer = ({ content }) => {
  let langData = parseContentSafely(content);
  
  if (!langData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No languages listed</div>;
  }

  if (!Array.isArray(langData)) {
    if (typeof langData === 'string') {
      const items = langData.split(/[,\n]/).map(s => s.trim()).filter(s => s);
      langData = items.map(item => ({ language: item }));
    } else {
      langData = [langData];
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      {langData.map((lang, idx) => {
        const langName = typeof lang === 'string' ? lang : (lang.language || lang.name || 'Language');
        const proficiency = typeof lang === 'object' ? lang.proficiency : null;
        
        return (
          <div key={idx} className="bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded-lg">
            <span className="text-sm font-medium text-gray-800 dark:text-gray-200">🌐 {langName}</span>
            {proficiency && (
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">({proficiency})</span>
            )}
          </div>
        );
      })}
    </div>
  );
};

// Component to render Interests section
const InterestsRenderer = ({ content }) => {
  let interestData = parseContentSafely(content);
  
  if (!interestData) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No interests listed</div>;
  }

  if (!Array.isArray(interestData)) {
    if (typeof interestData === 'string') {
      interestData = interestData.split(/[,\n]/).map(s => s.trim()).filter(s => s);
    } else {
      interestData = [interestData];
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      {interestData.map((interest, idx) => {
        const text = typeof interest === 'string' ? interest : (interest.name || interest.title || 'Interest');
        return (
          <span key={idx} className="bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 text-xs px-3 py-1.5 rounded-lg">
            {text}
          </span>
        );
      })}
    </div>
  );
};

// Component to render References section
const ReferencesRenderer = ({ content }) => {
  if (!content) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No references provided</div>;
  }

  if (typeof content === 'string') {
    return (
      <div className="text-sm text-gray-700 dark:text-gray-300 italic">
        {content}
      </div>
    );
  }

  // If it's an array or object, render appropriately
  const refData = parseContentSafely(content);
  if (Array.isArray(refData)) {
    return (
      <div className="space-y-3">
        {refData.map((ref, idx) => (
          <div key={idx} className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
            {typeof ref === 'string' ? (
              <p className="text-sm text-gray-700 dark:text-gray-300">{ref}</p>
            ) : (
              <>
                <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{ref.name || 'Reference'}</h5>
                {ref.title && <p className="text-xs text-gray-600 dark:text-gray-400">{ref.title}</p>}
                {ref.company && <p className="text-xs text-sage-600 dark:text-sage-400">{ref.company}</p>}
                {ref.email && <p className="text-xs text-gray-500 dark:text-gray-400">{ref.email}</p>}
                {ref.phone && <p className="text-xs text-gray-500 dark:text-gray-400">{ref.phone}</p>}
              </>
            )}
          </div>
        ))}
      </div>
    );
  }

  return <div className="text-sm text-gray-700 dark:text-gray-300">{String(content)}</div>;
};

// Component to render Portfolio/Links section
const LinksRenderer = ({ content }) => {
  if (!content) {
    return <div className="text-sm text-gray-500 dark:text-gray-400 italic">No links provided</div>;
  }

  const linkData = parseContentSafely(content);
  
  const renderLink = (url, label, icon) => {
    if (!url) return null;
    const fullUrl = url.startsWith('http') ? url : `https://${url}`;
    return (
      <a
        href={fullUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 text-sm text-sage-600 dark:text-sage-400 hover:text-sage-800 dark:hover:text-sage-200 hover:underline transition-colors"
      >
        {icon}
        <span>{label || url}</span>
      </a>
    );
  };

  if (typeof linkData === 'object' && linkData !== null && !Array.isArray(linkData)) {
    return (
      <div className="space-y-2">
        {linkData.linkedin && renderLink(linkData.linkedin, 'LinkedIn', <FaLink className="text-blue-600" />)}
        {linkData.github && renderLink(linkData.github, 'GitHub', <FaLink className="text-gray-700 dark:text-gray-300" />)}
        {linkData.website && renderLink(linkData.website, 'Website', <FaLink className="text-green-600" />)}
        {linkData.portfolio && renderLink(linkData.portfolio, 'Portfolio', <FaLink className="text-purple-600" />)}
      </div>
    );
  }

  if (Array.isArray(linkData)) {
    return (
      <div className="space-y-2">
        {linkData.map((link, idx) => (
          <div key={idx}>
            {typeof link === 'string' 
              ? renderLink(link, link) 
              : renderLink(link.url || link.link, link.label || link.title || link.name)}
          </div>
        ))}
      </div>
    );
  }

  if (typeof linkData === 'string') {
    return renderLink(linkData, linkData);
  }

  return <div className="text-sm text-gray-700 dark:text-gray-300">{String(content)}</div>;
};

// Main render function for CV sections
const renderSectionContent = (key, content) => {
  if (!content) return null;

  // Debug logging
  console.log(`🔍 Rendering section "${key}":`, {
    contentType: typeof content,
    isArray: Array.isArray(content),
    contentPreview: typeof content === 'string' ? content.substring(0, 100) : JSON.stringify(content).substring(0, 100)
  });

  const lowerKey = key.toLowerCase();
  
  if (lowerKey.includes('skill') || lowerKey.includes('tools')) {
    return <SkillsRenderer content={content} />;
  } else if (lowerKey.includes('experience') || lowerKey.includes('work') || lowerKey.includes('internship') || lowerKey.includes('volunteer') || lowerKey.includes('leadership')) {
    return <WorkExperienceRenderer content={content} />;
  } else if (lowerKey.includes('education')) {
    return <EducationRenderer content={content} />;
  } else if (lowerKey.includes('certification')) {
    return <CertificationsRenderer content={content} />;
  } else if (lowerKey.includes('project')) {
    return <ProjectsRenderer content={content} />;
  } else if (lowerKey.includes('achievement') || lowerKey.includes('award')) {
    return <AchievementsRenderer content={content} />;
  } else if (lowerKey.includes('publication') || lowerKey.includes('research')) {
    return <PublicationsRenderer content={content} />;
  } else if (lowerKey.includes('language')) {
    return <LanguagesRenderer content={content} />;
  } else if (lowerKey.includes('interest') || lowerKey.includes('hobbi')) {
    return <InterestsRenderer content={content} />;
  } else if (lowerKey.includes('reference')) {
    return <ReferencesRenderer content={content} />;
  } else if (lowerKey.includes('link') || lowerKey.includes('portfolio') || lowerKey.includes('github')) {
    return <LinksRenderer content={content} />;
  } else if (lowerKey.includes('personal') || lowerKey.includes('contact')) {
    // For personal information, try to parse and display nicely
    const data = parseContentSafely(content);
    if (typeof data === 'object' && data !== null) {
      return (
        <div className="space-y-2 text-sm">
          {data.name && <p><span className="font-semibold">Name:</span> {data.name}</p>}
          {data.email && <p><span className="font-semibold">Email:</span> {data.email}</p>}
          {data.phone && <p><span className="font-semibold">Phone:</span> {data.phone}</p>}
          {data.location && <p><span className="font-semibold">Location:</span> {data.location}</p>}
          {data.website && (
            <p>
              <span className="font-semibold">Website:</span>{' '}
              <a href={data.website} target="_blank" rel="noopener noreferrer" className="text-sage-600 dark:text-sage-400 hover:underline">
                {data.website}
              </a>
            </p>
          )}
          {data.linkedin && (
            <p>
              <span className="font-semibold">LinkedIn:</span>{' '}
              <a href={data.linkedin} target="_blank" rel="noopener noreferrer" className="text-sage-600 dark:text-sage-400 hover:underline">
                {data.linkedin}
              </a>
            </p>
          )}
        </div>
      );
    }
  }
  
  // Default: handle different content types safely
  if (typeof content === 'string') {
    return <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{content}</div>;
  } else if (Array.isArray(content)) {
    // If it's an array of strings, join them
    const stringContent = content.map((item, idx) => {
      if (typeof item === 'string') return item;
      if (typeof item === 'object' && item !== null) {
        // Try to get a meaningful string from the object
        return item.name || item.title || item.text || JSON.stringify(item);
      }
      return String(item);
    });
    return (
      <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
        {stringContent.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    );
  } else if (typeof content === 'object' && content !== null) {
    // Render object properties
    return (
      <div className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
        {Object.entries(content).map(([key, value]) => (
          <p key={key}>
            <span className="font-semibold capitalize">{key}:</span>{' '}
            {typeof value === 'string' ? value : JSON.stringify(value)}
          </p>
        ))}
      </div>
    );
  }
  
  return <div className="text-sm text-gray-700 dark:text-gray-300">{String(content)}</div>;
};

// Enhanced CV Content Renderer with Icons and Better Formatting
const EnhancedCVRenderer = ({ content }) => {
  if (!content || !content.trim()) {
    return <p className="text-gray-500 dark:text-gray-400 italic">No content available</p>;
  }

  const lines = content.split('\n');
  const sections = [];
  let currentSection = null;
  let currentContent = [];

  // Parse content into sections
  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    
    // Detect section headers (ALL CAPS or starts with #, but not contact info)
    const isAllCaps = trimmed && trimmed === trimmed.toUpperCase();
    const hasContactMarkers = trimmed.includes('@') || trimmed.includes('+') || /\d{3}/.test(trimmed);
    const isMarkdownHeader = line.startsWith('##') || line.startsWith('###');
    const isLikelyHeader = (isAllCaps && trimmed.length > 3 && !hasContactMarkers) || isMarkdownHeader;
    
    if (isLikelyHeader) {
      // Save previous section
      if (currentSection) {
        sections.push({ title: currentSection, content: currentContent.join('\n') });
      }
      // Start new section
      currentSection = trimmed.replace(/^#+\s*/, '');
      currentContent = [];
    } else if (trimmed) {
      currentContent.push(line);
    }
  });
  
  // Add last section
  if (currentSection) {
    sections.push({ title: currentSection, content: currentContent.join('\n') });
  }

  // If no sections detected, treat first few lines as header and rest as content
  if (sections.length === 0) {
    const headerLines = lines.slice(0, 5).filter(l => l.trim());
    const bodyLines = lines.slice(5);
    sections.push({ title: 'HEADER', content: headerLines.join('\n'), isHeader: true });
    sections.push({ title: 'CONTENT', content: bodyLines.join('\n') });
  }

  const getSectionIcon = (title) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('education')) return <FaGraduationCap className="text-blue-500" />;
    if (titleLower.includes('internship')) return <FaBriefcase className="text-teal-500" />;
    if (titleLower.includes('experience') || titleLower.includes('work')) return <FaBriefcase className="text-purple-500" />;
    if (titleLower.includes('technical') && titleLower.includes('skill')) return <FaCode className="text-green-600" />;
    if (titleLower.includes('soft') && titleLower.includes('skill')) return <FaHeart className="text-pink-500" />;
    if (titleLower.includes('skill')) return <FaCode className="text-green-500" />;
    if (titleLower.includes('profile') || titleLower.includes('summary')) return <FaUser className="text-indigo-500" />;
    if (titleLower.includes('certification')) return <FaCertificate className="text-orange-500" />;
    if (titleLower.includes('project')) return <FaProjectDiagram className="text-cyan-500" />;
    if (titleLower.includes('achievement') || titleLower.includes('award')) return <FaTrophy className="text-yellow-500" />;
    if (titleLower.includes('volunteer') || titleLower.includes('leadership')) return <FaHandsHelping className="text-rose-500" />;
    if (titleLower.includes('publication') || titleLower.includes('research')) return <FaBook className="text-amber-600" />;
    if (titleLower.includes('language')) return <FaLanguage className="text-pink-500" />;
    if (titleLower.includes('tool') || titleLower.includes('technolog')) return <FaWrench className="text-slate-500" />;
    if (titleLower.includes('interest') || titleLower.includes('hobby')) return <FaHeart className="text-red-400" />;
    if (titleLower.includes('reference')) return <FaUsers className="text-gray-600" />;
    if (titleLower.includes('portfolio') || titleLower.includes('link') || titleLower.includes('github')) return <FaLink className="text-blue-400" />;
    return <FaFileAlt className="text-gray-500" />;
  };

  return (
    <div className="space-y-4">
      {sections.map((section, idx) => {
        if (section.isHeader) {
          // Render header section with contact info styling
          const headerLines = section.content.split('\n').filter(l => l.trim());
          let nameShown = false;
          let titleShown = false;
          
          return (
            <div key={idx} className="bg-gradient-to-r from-sage-50 to-emerald-50 dark:from-sage-900/20 dark:to-emerald-900/20 p-6 rounded-xl border-l-4 border-sage-500 shadow-sm">
              {headerLines.map((line, i) => {
                const trimmed = line.trim();
                
                // Skip empty
                if (!trimmed) return null;
                
                // Detect contact info
                const hasEmail = trimmed.includes('@');
                const hasPhone = trimmed.includes('+') || /\d{3}[\s\-]\d{3}[\s\-]\d{4}/.test(trimmed);
                
                // Name (first non-contact line)
                if (!nameShown && !hasEmail && !hasPhone && trimmed.length < 50) {
                  nameShown = true;
                  return (
                    <div key={i} className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg">
                        <FaUser className="text-indigo-600 dark:text-indigo-400 text-xl" />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{trimmed}</h2>
                    </div>
                  );
                }
                
                // Job Title (second non-contact line)
                if (nameShown && !titleShown && !hasEmail && !hasPhone && trimmed.length < 80) {
                  titleShown = true;
                  return (
                    <p key={i} className="text-lg text-sage-600 dark:text-sage-400 font-medium mb-3 ml-14">
                      {trimmed}
                    </p>
                  );
                }
                
                // Email
                if (hasEmail) {
                  return (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 mb-2">
                      <FaEnvelope className="text-sage-500" />
                      <span>{trimmed}</span>
                    </div>
                  );
                }
                
                // Phone
                if (hasPhone) {
                  return (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 mb-2">
                      <FaPhone className="text-sage-500" />
                      <span>{trimmed}</span>
                    </div>
                  );
                }
                
                // Location (non-contact line after name/title)
                if (nameShown && titleShown) {
                  return (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 mb-2">
                      <FaMapMarkerAlt className="text-sage-500" />
                      <span>{trimmed}</span>
                    </div>
                  );
                }
                
                return null;
              })}
            </div>
          );
        }

        // Special handling for Skills section
        const isSkillsSection = section.title.toLowerCase().includes('skill');
        
        // Regular section - group lines intelligently
        const contentLines = section.content.split('\n').filter(l => l.trim());
        
        // If it's skills section, render as tags
        if (isSkillsSection) {
          const skills = contentLines.map(line => line.trim().replace(/^[-•]\s*/, '')).filter(s => s);
          return (
            <div key={idx} className="bg-white dark:bg-gray-800/50 p-5 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-sage-300 dark:hover:border-sage-600 transition-all shadow-sm">
              <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
                <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                  {getSectionIcon(section.title)}
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wide">
                  {section.title}
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, i) => (
                  <span 
                    key={i}
                    className="text-xs px-3 py-1.5 bg-sage-50 dark:bg-sage-900/30 text-sage-700 dark:text-sage-300 rounded-lg border border-sage-200 dark:border-sage-700"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          );
        }
        
        const groupedContent = [];
        let currentParagraph = [];
        
        contentLines.forEach((line, i) => {
          const trimmed = line.trim();
          
          // Bullet point - flush paragraph and add bullet
          if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
            if (currentParagraph.length > 0) {
              groupedContent.push({ type: 'paragraph', text: currentParagraph.join(' ') });
              currentParagraph = [];
            }
            groupedContent.push({ type: 'bullet', text: trimmed.replace(/^[-•]\s*/, '') });
          }
          // Heading indicator (ends with : or all caps short line)
          else if ((trimmed.endsWith(':') && trimmed.length < 50) || 
                   (trimmed === trimmed.toUpperCase() && trimmed.length > 2 && trimmed.length < 50 && !/\d/.test(trimmed))) {
            if (currentParagraph.length > 0) {
              groupedContent.push({ type: 'paragraph', text: currentParagraph.join(' ') });
              currentParagraph = [];
            }
            groupedContent.push({ type: 'heading', text: trimmed });
          }
          // Date range
          else if (/\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*Present/i.test(trimmed)) {
            if (currentParagraph.length > 0) {
              groupedContent.push({ type: 'paragraph', text: currentParagraph.join(' ') });
              currentParagraph = [];
            }
            groupedContent.push({ type: 'date', text: trimmed });
          }
          // Regular text - accumulate into paragraph
          else {
            currentParagraph.push(trimmed);
          }
        });
        
        // Flush remaining paragraph
        if (currentParagraph.length > 0) {
          groupedContent.push({ type: 'paragraph', text: currentParagraph.join(' ') });
        }
        
        return (
          <div key={idx} className="bg-white dark:bg-gray-800/50 p-5 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all shadow-sm">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
              <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                {getSectionIcon(section.title)}
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wide">
                {section.title}
              </h3>
            </div>
            <div className="space-y-3">
              {groupedContent.map((item, i) => {
                if (item.type === 'bullet') {
                  return (
                    <div key={i} className="flex gap-3 items-start">
                      <span className="text-sage-500 mt-1">•</span>
                      <span className="text-gray-700 dark:text-gray-300 flex-1">{item.text}</span>
                    </div>
                  );
                }
                if (item.type === 'heading') {
                  return (
                    <p key={i} className="text-sm font-semibold text-gray-900 dark:text-white mt-4 mb-2">
                      {item.text}
                    </p>
                  );
                }
                if (item.type === 'date') {
                  return (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 font-medium">
                      <FaClock className="text-gray-400" />
                      <span>{item.text}</span>
                    </div>
                  );
                }
                // Regular paragraph
                return (
                  <p key={i} className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {item.text}
                  </p>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

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
  const [analysisFile, setAnalysisFile] = useState(null);
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(false);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  const [pendingUploadEvent, setPendingUploadEvent] = useState(null);

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

  const handleUploadConfirmation = (e) => {
    e.preventDefault();
    if (!selectedFile) return alert("Select a file first!");
    
    // Store the event and show confirmation modal
    setPendingUploadEvent(e);
    setShowConfirmationModal(true);
  };

  const proceedWithUpload = async () => {
    // Close modal
    setShowConfirmationModal(false);
    
    // Proceed with upload
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
      let optimizedContent = res.data.optimized_text || res.data.optimized_cv || "";
      
      // If optimized content is too short or missing, try to build from structured data
      if ((!optimizedContent || optimizedContent.trim().length < 100) && res.data.structured_cv) {
        const structured = res.data.structured_cv;
        const parts = [];
        
        // Build readable text from structured data
        if (structured.name) parts.push(`# ${structured.name}\n`);
        if (structured.contact) parts.push(`${structured.contact}\n`);
        if (structured.summary) parts.push(`\n## Professional Summary\n${structured.summary}\n`);
        if (structured.skills && Array.isArray(structured.skills) && structured.skills.length > 0) {
          parts.push(`\n## Skills\n${structured.skills.map(s => `- ${s}`).join('\n')}\n`);
        }
        if (structured.experience && Array.isArray(structured.experience) && structured.experience.length > 0) {
          parts.push(`\n## Work Experience\n`);
          structured.experience.forEach(exp => {
            parts.push(`\n### ${exp.title || exp.role || 'Position'}`);
            if (exp.company) parts.push(` at ${exp.company}`);
            if (exp.dates || exp.years) parts.push(` | ${exp.dates || exp.years}`);
            parts.push('\n');
            if (exp.description) parts.push(`${exp.description}\n`);
            if (exp.points && Array.isArray(exp.points)) {
              exp.points.forEach(point => parts.push(`- ${point}\n`));
            }
          });
        }
        if (structured.education && Array.isArray(structured.education) && structured.education.length > 0) {
          parts.push(`\n## Education\n`);
          structured.education.forEach(edu => {
            parts.push(`\n### ${edu.degree || 'Degree'}\n`);
            if (edu.school || edu.institution) parts.push(`${edu.school || edu.institution}\n`);
            if (edu.year) parts.push(`${edu.year}\n`);
          });
        }
        if (structured.projects && Array.isArray(structured.projects) && structured.projects.length > 0) {
          parts.push(`\n## Projects\n`);
          structured.projects.forEach(proj => {
            parts.push(`\n### ${proj.name || 'Project'}\n`);
            if (proj.desc || proj.description) parts.push(`${proj.desc || proj.description}\n`);
            if (proj.technologies && Array.isArray(proj.technologies)) {
              parts.push(`Technologies: ${proj.technologies.join(', ')}\n`);
            }
          });
        }
        
        if (parts.length > 0) {
          optimizedContent = parts.join('');
        }
      }
      
      setOptimizedCV(optimizedContent);
      setSuggestions(res.data.suggestions || []);
      // prefer grouped suggestions if provided
      setGroupedSuggestions(res.data.grouped_suggestions || {});
      
      // Debug: Log ordered sections data
      const orderedSectionsData = res.data.ordered_sections || [];
      console.log('📊 Received ordered_sections from backend:', orderedSectionsData);
      if (orderedSectionsData.length > 0) {
        console.log('📝 First section sample:', {
          key: orderedSectionsData[0].key,
          label: orderedSectionsData[0].label,
          contentType: typeof orderedSectionsData[0].content,
          contentPreview: JSON.stringify(orderedSectionsData[0].content).substring(0, 100)
        });
      }
      
      setOrderedSections(orderedSectionsData);
      
      // Debug: Log template_data received from backend
      console.log('📋 Received template_data from backend:', res.data.template_data);
      if (res.data.template_data) {
        console.log('  - name:', res.data.template_data.name);
        console.log('  - email:', res.data.template_data.email);
        console.log('  - skills:', res.data.template_data.skills?.length || 0, 'items');
        console.log('  - experience:', res.data.template_data.experience?.length || 0, 'items');
        console.log('  - education:', res.data.template_data.education?.length || 0, 'items');
      }
      
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
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || "CV_Download.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // Show success message
      console.log(`✅ Downloaded: ${filename}`);
    } catch (err) {
      console.error("Download error:", err);
      alert("Download failed! Please try again.");
    }
  };

  const handleDownloadOptimizedCV = async () => {
    console.log('🔄 handleDownloadOptimizedCV called');
    console.log('  - optimizedCV present:', !!optimizedCV);
    console.log('  - templateData present:', !!templateData);
    
    if (templateData) {
      console.log('  - templateData.name:', templateData.name);
      console.log('  - templateData.skills:', templateData.skills?.length || 0, 'items');
      console.log('  - templateData.experience:', templateData.experience?.length || 0, 'items');
    }
    
    if (!optimizedCV && !templateData) {
      alert("No optimized CV available to download.");
      return;
    }

    try {
      const payload = {
        structured_cv: templateData,
        optimized_text: optimizedCV,
        template_data: templateData,
        filename: lastUploadedFilename || "Optimized_CV.pdf",
      };

      console.log("Sending download request with payload:", {
        hasStructuredCV: !!templateData,
        hasOptimizedText: !!optimizedCV,
        filename: payload.filename
      });

      const res = await api.post("/api/download-optimized-cv", payload, {
        responseType: "blob",
      });

      // Check if we got an error response as JSON
      if (res.data.type === 'application/json') {
        const text = await res.data.text();
        const errorData = JSON.parse(text);
        throw new Error(errorData.message || "Download failed");
      }

      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement("a");
      link.href = url;
      const filename = lastUploadedFilename 
        ? `${lastUploadedFilename.replace(/\.[^/.]+$/, "")}_Optimized.pdf`
        : "Optimized_CV.pdf";
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      console.log(`✅ Downloaded optimized CV: ${filename}`);
    } catch (err) {
      console.error("Download optimized CV error:", err);
      const errorMsg = err.response?.data?.message || err.message || "Failed to download optimized CV";
      alert(`Download failed: ${errorMsg}\n\nPlease try again or use the 'Download from Library' button.`);
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
        className="bg-gradient-to-br from-sage-600 via-emerald-600 to-teal-600 dark:from-sage-900 dark:via-emerald-900 dark:to-teal-900
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
              <p className="text-md text-white/80 mb-4">
                Welcome back, <span className="font-semibold">{user?.full_name || user?.username || user?.email || "User"}</span>
              </p>
              <button
                onClick={() => navigate('/chatbot')}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white font-semibold rounded-xl border border-white/30 shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
              >
                <FaRobot className="text-lg" />
                Chatbot
              </button>
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
              <div className="p-3 bg-sage-50 dark:bg-sage-900/30 rounded-xl">
                <FaFileAlt className="text-sage-500 text-xl" />
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
                  <div className="p-4 bg-gradient-to-br from-blue-500 to-sage-600 rounded-xl">
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
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-sage-600 hover:from-blue-600 hover:to-sage-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
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
            <h2 className="text-2xl font-bold mb-6 text-sage-600 dark:text-sage-400 flex items-center gap-3">
              <FaUpload className="text-xl" /> Upload & Optimize CV
            </h2>
            <form onSubmit={handleUploadConfirmation} className="space-y-6">
              <div className="grid gap-6 w-full lg:grid-cols-12 items-stretch">
                <label
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`lg:col-span-7 border-dashed border-2 
                  ${
                    dragActive
                      ? "border-sage-500 bg-sage-50 dark:bg-sage-900/40"
                      : "border-gray-300 dark:border-gray-600 hover:border-sage-400 dark:hover:border-sage-500"
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
                    <div className="w-16 h-16 mx-auto mb-4 bg-sage-100 dark:bg-sage-900/50 rounded-full flex items-center justify-center">
                      <FaUpload className="text-2xl text-sage-600 dark:text-sage-400" />
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
                      <FaBriefcase className="w-4 h-4 text-sage-500" />
                      Target Job Domain
                    </label>
                    <div className="relative">
                      <select
                        value={jobDomain}
                        onChange={(e) => setJobDomain(e.target.value)}
                        className="w-full appearance-none p-3 pl-4 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#1f2937]
          text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-sage-500 
          focus:border-transparent transition-all duration-200 hover:border-sage-400 dark:hover:border-sage-500 cursor-pointer font-medium"
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
                    className="w-full bg-gradient-to-r from-sage-600 to-emerald-600 dark:from-sage-700 dark:to-emerald-800 text-white px-6 py-4 rounded-xl 
                    hover:shadow-lg hover:from-sage-700 hover:to-emerald-700 dark:hover:from-sage-800 dark:hover:to-emerald-900
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
                className="text-sm font-semibold text-sage-600 dark:text-sage-400 hover:text-sage-700 dark:hover:text-sage-300 hover:underline shrink-0 transition-colors"
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
                        <FaFileAlt className="text-sage-400 text-sm shrink-0" />
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
          <section className="mb-10 space-y-8">
            {/* STEP 1: ATS Score & Keywords Section */}
            <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/30 dark:via-indigo-900/30 dark:to-purple-900/30 border border-blue-200 dark:border-blue-700/50 p-6 rounded-2xl shadow-md">
              <h3 className="text-2xl font-bold mb-6 text-blue-800 dark:text-blue-400 flex items-center gap-3">
                <FaRobot className="text-xl" /> ATS Analysis Results
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* ATS Score Circle */}
                <div className="bg-white dark:bg-gray-900/50 rounded-xl p-6 border border-blue-100 dark:border-blue-800/50 shadow-sm text-center">
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <FaStar className="text-yellow-500 text-lg" />
                    <span className="text-sm font-bold uppercase tracking-wider text-gray-600 dark:text-gray-400">
                      ATS Compatibility Score
                    </span>
                  </div>
                  <div className="relative w-36 h-36 mx-auto mb-4">
                    <svg className="transform -rotate-90 w-36 h-36">
                      <circle
                        cx="72"
                        cy="72"
                        r="64"
                        stroke="currentColor"
                        strokeWidth="10"
                        fill="transparent"
                        className="text-gray-200 dark:text-gray-700"
                      />
                      <circle
                        cx="72"
                        cy="72"
                        r="64"
                        stroke="currentColor"
                        strokeWidth="10"
                        fill="transparent"
                        strokeDasharray={`${2 * Math.PI * 64}`}
                        strokeDashoffset={`${2 * Math.PI * 64 * (1 - (atsScore || 0) / 100)}`}
                        className={`transition-all duration-500 ${
                          (atsScore || 0) >= 70 
                            ? 'text-green-500' 
                            : (atsScore || 0) >= 50 
                            ? 'text-yellow-500' 
                            : 'text-red-500'
                        }`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className={`text-4xl font-bold ${
                        (atsScore || 0) >= 70 
                          ? 'text-green-600 dark:text-green-400' 
                          : (atsScore || 0) >= 50 
                          ? 'text-yellow-600 dark:text-yellow-400' 
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {atsScore ?? "--"}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">/100</span>
                    </div>
                  </div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {(atsScore || 0) >= 70 
                      ? '✅ Excellent! Your CV is ATS-friendly' 
                      : (atsScore || 0) >= 50 
                      ? '⚠️ Good, but can be improved' 
                      : '❌ Needs significant optimization'}
                  </p>
                </div>

                {/* Found Keywords */}
                <div className="bg-white dark:bg-gray-900/50 rounded-xl p-6 border border-blue-100 dark:border-blue-800/50 shadow-sm">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <h4 className="text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                      Found Keywords ({foundKeywords.length})
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2 max-h-[200px] overflow-y-auto custom-scrollbar">
                    {foundKeywords.length > 0 ? (
                      foundKeywords.map((kw, i) => (
                        <span key={i} className="bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 text-xs px-3 py-1.5 rounded-lg border border-green-200 dark:border-green-700 font-medium">
                          ✓ {kw}
                        </span>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 dark:text-gray-400 italic">No keywords detected</p>
                    )}
                  </div>
                </div>

                {/* Recommended Keywords */}
                <div className="bg-white dark:bg-gray-900/50 rounded-xl p-6 border border-blue-100 dark:border-blue-800/50 shadow-sm">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                    <h4 className="text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                      Recommended to Add ({recommendedKeywords.length})
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2 max-h-[200px] overflow-y-auto custom-scrollbar">
                    {recommendedKeywords.length > 0 ? (
                      recommendedKeywords.map((kw, i) => (
                        <span key={i} className="bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 text-xs px-3 py-1.5 rounded-lg border border-orange-200 dark:border-orange-700 font-medium">
                          + {kw}
                        </span>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 dark:text-gray-400 italic">All recommended keywords included!</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* STEP 2: CV Sections Overview */}
            {orderedSections && orderedSections.length > 0 && (
              <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 dark:from-purple-900/30 dark:via-pink-900/30 dark:to-rose-900/30 border border-purple-200 dark:border-purple-700/50 p-6 rounded-2xl shadow-md">
                <h3 className="text-2xl font-bold mb-6 text-purple-800 dark:text-purple-400 flex items-center gap-3">
                  <FaFileAlt className="text-xl" /> CV Sections Overview
                </h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {orderedSections.map(({ key, label, content }) => {
                    const getSectionIcon = (sectionKey) => {
                      const keyLower = sectionKey.toLowerCase();
                      if (keyLower.includes('education')) return <FaGraduationCap className="text-blue-500" />;
                      if (keyLower.includes('internship')) return <FaBriefcase className="text-teal-500" />;
                      if (keyLower.includes('experience') || keyLower.includes('work')) return <FaBriefcase className="text-purple-500" />;
                      if (keyLower.includes('technical') && keyLower.includes('skill')) return <FaCode className="text-green-600" />;
                      if (keyLower.includes('soft') && keyLower.includes('skill')) return <FaHeart className="text-pink-500" />;
                      if (keyLower.includes('skill')) return <FaCode className="text-green-500" />;
                      if (keyLower.includes('personal') || keyLower.includes('contact')) return <FaUser className="text-indigo-500" />;
                      if (keyLower.includes('certification')) return <FaCertificate className="text-orange-500" />;
                      if (keyLower.includes('project')) return <FaProjectDiagram className="text-cyan-500" />;
                      if (keyLower.includes('achievement') || keyLower.includes('award')) return <FaTrophy className="text-yellow-500" />;
                      if (keyLower.includes('volunteer') || keyLower.includes('leadership')) return <FaHandsHelping className="text-rose-500" />;
                      if (keyLower.includes('publication') || keyLower.includes('research')) return <FaBook className="text-amber-600" />;
                      if (keyLower.includes('language')) return <FaLanguage className="text-pink-500" />;
                      if (keyLower.includes('tool') || keyLower.includes('technolog')) return <FaWrench className="text-slate-500" />;
                      if (keyLower.includes('interest') || keyLower.includes('hobby')) return <FaHeart className="text-red-400" />;
                      if (keyLower.includes('reference')) return <FaUsers className="text-gray-600" />;
                      if (keyLower.includes('portfolio') || keyLower.includes('link') || keyLower.includes('github')) return <FaLink className="text-blue-400" />;
                      if (keyLower.includes('summary') || keyLower.includes('objective')) return <FaUser className="text-indigo-500" />;
                      return <FaFileAlt className="text-gray-500" />;
                    };

                    return content ? (
                      <div
                        key={key}
                        className="bg-white dark:bg-gray-900/50 p-5 rounded-xl shadow-sm border border-purple-100 dark:border-purple-700/50 hover:shadow-md hover:border-purple-300 dark:hover:border-purple-600 transition-all group"
                      >
                        <div className="flex items-center gap-3 mb-3">
                          <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
                            {getSectionIcon(key)}
                          </div>
                          <h4 className="font-bold text-purple-700 dark:text-purple-400 text-sm uppercase tracking-wide">
                            {label}
                          </h4>
                        </div>
                        <div className="text-sm text-gray-700 dark:text-gray-300 line-clamp-4 overflow-hidden leading-relaxed">
                          {renderSectionContent(key, content)}
                        </div>
                      </div>
                    ) : null;
                  })}
                </div>
              </div>
            )}

            {/* STEP 3: Optimized CV & Download */}
            <div
              className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 
              border border-green-200 dark:border-green-700/50 p-6 
              rounded-2xl shadow-md text-gray-800 dark:text-gray-200"
            >
              <div className="flex flex-col lg:flex-row items-start gap-6">
                <div className="flex-1 w-full">
                  <h3 className="text-2xl font-bold mb-4 text-green-800 dark:text-green-400 flex items-center gap-2">
                    <FaCheckCircle className="text-xl" /> Optimized CV Preview
                  </h3>
                  <div className="bg-white dark:bg-gray-900/50 p-5 rounded-lg border border-green-100 dark:border-green-800/50 shadow-sm">
                    {/* Toggle between raw optimized text and organized preview */}
                    <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
                      <span className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">CV Content</span>
                      <button
                        onClick={() => setExpandedPreview(!expandedPreview)}
                        className="text-xs px-4 py-1.5 rounded-lg bg-sage-100 dark:bg-sage-900/40 text-sage-700 dark:text-sage-300 hover:bg-sage-200 dark:hover:bg-sage-900/60 transition-colors font-medium"
                      >
                        {expandedPreview ? "📄 Raw Text" : "👁 Preview"}
                      </button>
                    </div>

                    {!expandedPreview ? (
                      <div className="max-h-[500px] overflow-auto custom-scrollbar">
                        <EnhancedCVRenderer content={optimizedCV} />
                      </div>
                    ) : (
                      <div className="max-h-[500px] overflow-auto custom-scrollbar">
                        {templateData ? (
                          <ResumeTemplate data={templateData} />
                        ) : orderedSections && orderedSections.length > 0 ? (
                          <div className="space-y-4">
                            {orderedSections.map((section) => {
                              const getSectionIcon = (sectionKey) => {
                                const keyLower = sectionKey.toLowerCase();
                                if (keyLower.includes('education')) return <FaGraduationCap className="text-blue-500 text-lg" />;
                                if (keyLower.includes('internship')) return <FaBriefcase className="text-teal-500 text-lg" />;
                                if (keyLower.includes('experience') || keyLower.includes('work')) return <FaBriefcase className="text-purple-500 text-lg" />;
                                if (keyLower.includes('technical') && keyLower.includes('skill')) return <FaCode className="text-green-600 text-lg" />;
                                if (keyLower.includes('soft') && keyLower.includes('skill')) return <FaHeart className="text-pink-500 text-lg" />;
                                if (keyLower.includes('skill')) return <FaCode className="text-green-500 text-lg" />;
                                if (keyLower.includes('personal') || keyLower.includes('contact')) return <FaUser className="text-indigo-500 text-lg" />;
                                if (keyLower.includes('certification')) return <FaCertificate className="text-orange-500 text-lg" />;
                                if (keyLower.includes('project')) return <FaProjectDiagram className="text-cyan-500 text-lg" />;
                                if (keyLower.includes('achievement') || keyLower.includes('award')) return <FaTrophy className="text-yellow-500 text-lg" />;
                                if (keyLower.includes('volunteer') || keyLower.includes('leadership')) return <FaHandsHelping className="text-rose-500 text-lg" />;
                                if (keyLower.includes('publication') || keyLower.includes('research')) return <FaBook className="text-amber-600 text-lg" />;
                                if (keyLower.includes('language')) return <FaLanguage className="text-pink-500 text-lg" />;
                                if (keyLower.includes('tool') || keyLower.includes('technolog')) return <FaWrench className="text-slate-500 text-lg" />;
                                if (keyLower.includes('interest') || keyLower.includes('hobby')) return <FaHeart className="text-red-400 text-lg" />;
                                if (keyLower.includes('reference')) return <FaUsers className="text-gray-600 text-lg" />;
                                if (keyLower.includes('portfolio') || keyLower.includes('link') || keyLower.includes('github')) return <FaLink className="text-blue-400 text-lg" />;
                                if (keyLower.includes('summary') || keyLower.includes('objective') || keyLower.includes('profile')) return <FaUser className="text-indigo-500 text-lg" />;
                                return <FaFileAlt className="text-gray-500 text-lg" />;
                              };

                              return (
                                <div key={section.key} className="bg-white dark:bg-gray-800/50 p-5 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all shadow-sm">
                                  <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
                                    <div className="p-2 bg-gradient-to-br from-sage-50 to-emerald-50 dark:from-sage-900/30 dark:to-emerald-900/30 rounded-lg">
                                      {getSectionIcon(section.key)}
                                    </div>
                                    <h4 className="text-base font-bold text-gray-900 dark:text-white uppercase tracking-wide">
                                      {section.label}
                                    </h4>
                                  </div>
                                  <div className="text-sm leading-relaxed">
                                    {renderSectionContent(section.key, parseContentSafely(section.content))}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center p-8 text-center">
                            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-3">
                              <FaFileAlt className="text-gray-400 text-2xl" />
                            </div>
                            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">No structured preview available</p>
                            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Use Raw Text view to see content</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Download Section */}
                <div className="bg-white dark:bg-gray-900/50 rounded-xl p-6 border border-green-100 dark:border-green-800/50 shadow-sm lg:min-w-[300px]">
                  <div className="text-center mb-6">
                    <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/40 dark:to-emerald-900/40 rounded-full flex items-center justify-center">
                      <FaDownload className="text-green-600 dark:text-green-400 text-3xl" />
                    </div>
                    <h4 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-2">
                      Download Your Optimized CV
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Get your ATS-friendly PDF ready for applications
                    </p>
                  </div>
                  
                  <button
                    onClick={handleDownloadOptimizedCV}
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 dark:from-green-700 dark:to-emerald-800 dark:hover:from-green-800 dark:hover:to-emerald-900 text-white px-6 py-4 rounded-xl font-bold transition-all duration-200 flex items-center justify-center gap-3 shadow-lg hover:shadow-xl hover:-translate-y-0.5 text-lg"
                  >
                    <FaDownload className="text-xl" /> Download Optimized PDF
                  </button>
                  
                  {lastUploadedFileId && (
                    <button
                      onClick={() =>
                        handleDownload(
                          lastUploadedFileId,
                          lastUploadedFilename?.replace(/\.[^/.]+$/, "_ATS_Optimized.pdf") || "CV_ATS_Optimized.pdf"
                        )
                      }
                      className="mt-3 w-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 border border-gray-300 dark:border-gray-600"
                    >
                      <FaDownload className="text-sm" /> Download from Library
                    </button>
                  )}
                  
                  <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-500 dark:text-gray-400 text-center flex items-center justify-center gap-2">
                      <FaCheckCircle className="text-green-500" />
                      Ready for job applications
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Improvement Suggestions */}
            {(Object.keys(groupedSuggestions).length > 0 ||
              (suggestions && suggestions.length > 0)) && (
              <div
                className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 
                border border-amber-200 dark:border-amber-700/50 p-6 
                rounded-2xl shadow-md text-gray-800 dark:text-gray-200"
              >
                <h3 className="text-xl font-bold mb-4 text-amber-800 dark:text-amber-400 flex items-center gap-2">
                  <FaExclamationCircle className="text-lg" /> Improvement Suggestions
                </h3>
                {Object.keys(groupedSuggestions).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(groupedSuggestions).map(([cat, msgs]) => (
                      <div key={cat} className="bg-white dark:bg-gray-900/50 p-4 rounded-lg border border-amber-100 dark:border-amber-800/50">
                        <h4 className="font-semibold capitalize text-amber-700 dark:text-amber-400 mb-2">
                          {cat.replace("_", " ")}
                        </h4>
                        <ul className="list-disc pl-6 space-y-1">
                          {msgs.map((m, i) => (
                            <li key={i} className="text-sm text-gray-700 dark:text-gray-300">
                              {m}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ul className="list-disc pl-6 space-y-2">
                    {suggestions.map((s, idx) => (
                      <li key={idx} className="text-sm">
                        <strong className="capitalize text-amber-700 dark:text-amber-400">
                          {s.category || "General"}:
                        </strong>{" "}
                        <span className="text-gray-700 dark:text-gray-300">{s.message || s}</span>
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
                    <FaChartLine className="text-sage-500" />
                    <h3 className="text-lg font-bold">Keyword Coverage</h3>
                  </div>
                  <span className="text-sm font-semibold text-sage-600 dark:text-sage-300">
                    {keywordInsight.coverage}% match
                  </span>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-sage-500 to-emerald-500 h-3 rounded-full"
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
            rounded-lg px-4 py-3 bg-white dark:bg-[#1E1E2F] shadow-sm focus-within:ring-2 focus-within:ring-sage-500 transition-all"
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
              bg-white dark:bg-[#1E1E2F] text-gray-700 dark:text-gray-200 font-medium focus:ring-2 focus:ring-sage-500 transition-all"
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
            <h2 className="text-3xl font-bold text-sage-600 dark:text-sage-400 flex items-center gap-3">
              <FaFileAlt className="text-2xl" /> Your Uploaded CVs
              <span className="text-lg bg-sage-100 dark:bg-sage-900/50 text-sage-600 dark:text-sage-400 px-3 py-1 rounded-full font-semibold">
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
                      <div className="p-3 bg-sage-50 dark:bg-sage-900/30 rounded-xl shrink-0 group-hover:scale-105 transition-transform">
                        <FaFileAlt className="text-sage-500 text-xl" />
                      </div>
                      <div className="flex-1 min-w-0 pt-1">
                        <h3 className="font-bold text-lg truncate text-gray-900 dark:text-white group-hover:text-sage-600 dark:group-hover:text-sage-400 transition-colors" title={file.filename}>
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

                  <div className="flex flex-col gap-2 pt-5 border-t border-gray-100 dark:border-gray-800 mt-auto">
                    <button
                      onClick={async () => {
                        try {
                          const res = await api.get(`/api/download/${file._id}`, {
                            responseType: "blob",
                          });
                          const fileUrl = window.URL.createObjectURL(new Blob([res.data]));
                          setAnalysisFile({ url: fileUrl, name: file.filename, _id: file._id });
                          setShowAnalysisPanel(true);
                        } catch (err) {
                          console.error("Error loading file for analysis:", err);
                          alert("Failed to load file for analysis");
                        }
                      }}
                      className="w-full bg-gradient-to-r from-sage-600 to-emerald-600 dark:from-sage-700 dark:to-emerald-800 hover:from-sage-700 hover:to-emerald-700 dark:hover:from-sage-800 dark:hover:to-emerald-900 text-white px-4 py-2.5 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 font-semibold text-sm shadow-sm hover:shadow-md"
                    >
                      <FaChartLine /> Analyze CV
                    </button>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDownload(file._id, file.filename)}
                        className="flex-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-sage-300 dark:hover:border-sage-700 hover:bg-sage-50 dark:hover:bg-sage-900/20 text-gray-700 dark:text-gray-200 px-4 py-2.5 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 font-semibold text-sm group/btn"
                      >
                        <FaDownload className="text-gray-400 group-hover/btn:text-sage-500 transition-colors" /> Download
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
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-gray-900 to-gray-950 dark:from-[#0D1117] dark:to-[#010409] text-gray-300 py-8 text-center transition-colors duration-500 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-4">
          <p className="text-sm">&copy; {new Date().getFullYear()} <span className="font-semibold text-sage-400">PerfectCV</span>. All rights reserved.</p>
          <p className="text-xs text-gray-500 mt-2">Craft your perfect resume with AI-powered insights</p>
        </div>
      </footer>

      {/* CV Analysis Panel */}
      {showAnalysisPanel && analysisFile && (
        <CVAnalysisPanel
          file={analysisFile.url}
          onClose={() => {
            setShowAnalysisPanel(false);
            setAnalysisFile(null);
            if (analysisFile.url) {
              window.URL.revokeObjectURL(analysisFile.url);
            }
          }}
        />
      )}

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={showConfirmationModal}
        onClose={() => {
          setShowConfirmationModal(false);
          setPendingUploadEvent(null);
        }}
        onConfirm={proceedWithUpload}
        title="Before We Proceed"
        message="We are about to provide you with personalized guidance to support your career growth based on the information you upload.

Please note that this analysis is intended as guidance only and should not be fully relied upon for career decisions. Use it as a reference alongside your own judgment and professional advice."
        confirmText="I Understood"
      />
    </div>
  );
}
