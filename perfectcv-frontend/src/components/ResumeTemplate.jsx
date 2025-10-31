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

  return (
    <div className="max-w-3xl mx-auto p-6 text-gray-900 font-sans text-sm leading-relaxed bg-white">
      {/* Header */}
      <header className="border-b-2 border-gray-800 pb-2 mb-4">
        <h1 className="text-2xl font-bold">{name}</h1>
        <p className="text-xs text-gray-600">{contact}</p>
      </header>

      {/* Summary */}
      <section className="mb-3">
        <h2 className="font-semibold text-base border-b border-gray-300 pb-1 mb-1">
          Professional Summary
        </h2>
        <p>{summary}</p>
      </section>

      {/* Experience */}
      <section className="mb-3">
        <h2 className="font-semibold text-base border-b border-gray-300 pb-1 mb-1">
          Experience
        </h2>
        {experience.map((job, i) => (
          <div key={i} className="mb-2">
            <div className="flex justify-between font-semibold">
              <span>{job.title}</span>
              <span className="text-xs text-gray-600">{job.dates}</span>
            </div>
            <div className="text-xs text-gray-500 mb-1">{job.company}</div>
            <ul className="list-disc list-inside space-y-1">
              {job.points.map((p, j) => (
                <li key={j}>{p}</li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* Projects */}
      <section className="mb-3">
        <h2 className="font-semibold text-base border-b border-gray-300 pb-1 mb-1">
          Projects
        </h2>
        <ul className="list-disc list-inside space-y-1">
          {projects.map((p, i) => (
            <li key={i}>
              <strong>{p.name}</strong> — {p.desc}
            </li>
          ))}
        </ul>
      </section>

      {/* Skills */}
      <section className="mb-3">
        <h2 className="font-semibold text-base border-b border-gray-300 pb-1 mb-1">
          Skills
        </h2>
        <p>{skills.join(", ")}</p>
      </section>

      {/* Education */}
      <section className="mb-3">
        <h2 className="font-semibold text-base border-b border-gray-300 pb-1 mb-1">
          Education
        </h2>
        <ul>
          {education.map((e, i) => (
            <li key={i}>
              <strong>{e.degree}</strong> — {e.school} ({e.year})
            </li>
          ))}
        </ul>
      </section>

      {/* Certifications */}
      {certifications && certifications.length > 0 && (
        <section className="mb-3">
          <h2 className="font-semibold text-base border-b border-gray-300 pb-1 mb-1">
            Certifications & Awards
          </h2>
          <ul>
            {certifications.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
