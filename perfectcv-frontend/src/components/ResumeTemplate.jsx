// src/components/ResumeTemplate.jsx
import React from "react";

export default function ResumeTemplate({ data }) {
  const {
    name,
    contact,
    summary,
    experience,
    projects,
    skills,
    education,
    certifications,
  } = data;

  // Safely handle arrays and objects
  const experienceList = Array.isArray(experience) ? experience : [];
  const projectList = Array.isArray(projects) ? projects : [];
  const skillsList = Array.isArray(skills) ? skills : [];
  const educationList = Array.isArray(education) ? education : [];
  const certificationList = Array.isArray(certifications) ? certifications : [];

  return (
    <div className="max-w-4xl mx-auto p-8 text-gray-900 font-sans bg-white shadow-lg">
      {/* Header */}
      <header className="border-b-2 border-blue-700 pb-4 mb-6">
        <h1 className="text-3xl font-bold text-blue-900">{name || "Your Name"}</h1>
        <p className="text-sm text-gray-700 mt-2">{contact || "email@example.com"}</p>
      </header>

      {/* Professional Summary */}
      {summary && summary.trim() && (
        <section className="mb-5">
          <h2 className="font-bold text-lg text-blue-900 border-b-2 border-blue-500 pb-2 mb-2">
            Professional Summary
          </h2>
          <p className="text-sm text-gray-800 leading-relaxed">{summary}</p>
        </section>
      )}

      {/* Key Skills */}
      {skillsList.length > 0 && (
        <section className="mb-5">
          <h2 className="font-bold text-lg text-blue-900 border-b-2 border-blue-500 pb-2 mb-2">
            Key Skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {skillsList.map((skill, i) => (
              <span
                key={i}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Work Experience */}
      {experienceList.length > 0 && (
        <section className="mb-5">
          <h2 className="font-bold text-lg text-blue-900 border-b-2 border-blue-500 pb-2 mb-3">
            Work Experience
          </h2>
          {experienceList.map((job, i) => (
            <div key={i} className="mb-4 pb-3 border-b border-gray-300 last:border-0">
              <div className="flex justify-between items-baseline">
                <h3 className="font-semibold text-base text-gray-900">{job.title || "Position"}</h3>
                <span className="text-xs text-gray-600 font-medium">{job.dates || "Present"}</span>
              </div>
              <p className="text-sm text-gray-700 font-medium">{job.company || "Company"}</p>
              {job.points && job.points.length > 0 && (
                <ul className="list-disc list-inside mt-2 space-y-1">
                  {job.points.map((point, j) => (
                    <li key={j} className="text-sm text-gray-800">
                      {point}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Projects */}
      {projectList.length > 0 && (
        <section className="mb-5">
          <h2 className="font-bold text-lg text-blue-900 border-b-2 border-blue-500 pb-2 mb-3">
            Projects
          </h2>
          {projectList.map((project, i) => (
            <div key={i} className="mb-3 pb-2 border-b border-gray-300 last:border-0">
              <h3 className="font-semibold text-base text-gray-900">{project.name || "Project"}</h3>
              {project.desc && <p className="text-sm text-gray-800 mt-1">{project.desc}</p>}
              {project.technologies && project.technologies.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {project.technologies.map((tech, j) => (
                    <span
                      key={j}
                      className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-xs"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Education */}
      {educationList.length > 0 && (
        <section className="mb-5">
          <h2 className="font-bold text-lg text-blue-900 border-b-2 border-blue-500 pb-2 mb-3">
            Education
          </h2>
          {educationList.map((edu, i) => (
            <div key={i} className="mb-3 pb-2 border-b border-gray-300 last:border-0">
              <div className="flex justify-between items-baseline">
                <h3 className="font-semibold text-base text-gray-900">
                  {edu.degree || "Degree"}
                </h3>
                <span className="text-xs text-gray-600">{edu.year || "Present"}</span>
              </div>
              <p className="text-sm text-gray-700">{edu.school || "Institution"}</p>
            </div>
          ))}
        </section>
      )}

      {/* Certifications & Awards */}
      {certificationList.length > 0 && (
        <section className="mb-5">
          <h2 className="font-bold text-lg text-blue-900 border-b-2 border-blue-500 pb-2 mb-3">
            Certifications & Awards
          </h2>
          <ul className="list-disc list-inside space-y-2">
            {certificationList.map((cert, i) => (
              <li key={i} className="text-sm text-gray-800">
                {cert}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
