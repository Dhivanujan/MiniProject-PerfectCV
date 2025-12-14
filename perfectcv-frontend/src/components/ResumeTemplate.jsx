// src/components/ResumeTemplate.jsx
import React from "react";

export default function ResumeTemplate({ data }) {
  // Handle both direct fields and nested contact_information structure
  const contactInfo = data?.contact_information || {};
  const name = data?.name || contactInfo?.name || "Professional Resume";
  const email = data?.email || contactInfo?.email || "";
  const phone = data?.phone || contactInfo?.phone || "";
  const location = data?.location || contactInfo?.location || "";
  const linkedin = data?.linkedin || contactInfo?.linkedin || "";
  const github = data?.github || contactInfo?.github || "";
  
  const summary = data?.summary || data?.professional_summary || data?.about || "";
  const experience = data?.experience || data?.work_experience || [];
  const projects = data?.projects || [];
  const skills = data?.skills || [];
  const education = data?.education || [];
  const certifications = data?.certifications || [];

  // Safely handle arrays and objects
  const experienceList = Array.isArray(experience) ? experience : [];
  const projectList = Array.isArray(projects) ? projects : [];
  
  // Handle skills - can be array of strings or object with categories
  let skillsList = [];
  if (Array.isArray(skills)) {
    skillsList = skills;
  } else if (typeof skills === 'object' && skills !== null) {
    // Flatten skill categories into single array
    Object.values(skills).forEach(category => {
      if (Array.isArray(category)) {
        skillsList.push(...category);
      }
    });
  }
  
  const educationList = Array.isArray(education) ? education : [];
  const certificationList = Array.isArray(certifications) ? certifications : [];

  // Build contact string
  const contactParts = [];
  if (email) contactParts.push(email);
  if (phone) contactParts.push(phone);
  if (location) contactParts.push(location);
  if (linkedin) contactParts.push(linkedin);
  if (github) contactParts.push(github);
  const contactString = contactParts.join(' | ');

  // Check if we have any actual data
  const hasData = name !== "Professional Resume" || summary || experienceList.length > 0 || 
                  skillsList.length > 0 || educationList.length > 0;

  if (!hasData) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center bg-gradient-to-br from-slate-50 to-gray-100 shadow-xl rounded-xl border border-gray-200">
        <div className="text-gray-400 mb-4">
          <svg className="w-20 h-20 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-lg font-semibold text-gray-700">No CV Data Available</p>
        <p className="text-sm text-gray-500 mt-2">Upload a CV to see the formatted preview</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white shadow-2xl rounded-xl overflow-hidden border border-gray-200">
      {/* Header - Modern gradient design */}
      <header className="bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 text-white p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-5 rounded-full -ml-24 -mb-24"></div>
        <div className="relative z-10">
          <h1 className="text-4xl font-bold mb-3 tracking-tight">
            {name}
          </h1>
          {contactString && (
            <div className="flex flex-wrap items-center gap-4 mt-4">
              {email && (
                <div className="flex items-center gap-2 text-sm bg-white/10 px-3 py-1.5 rounded-lg backdrop-blur-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span>{email}</span>
                </div>
              )}
              {phone && (
                <div className="flex items-center gap-2 text-sm bg-white/10 px-3 py-1.5 rounded-lg backdrop-blur-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span>{phone}</span>
                </div>
              )}
              {location && (
                <div className="flex items-center gap-2 text-sm bg-white/10 px-3 py-1.5 rounded-lg backdrop-blur-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>{location}</span>
                </div>
              )}
              {(linkedin || github) && (
                <div className="flex items-center gap-3">
                  {linkedin && (
                    <a href={linkedin} target="_blank" rel="noopener noreferrer" className="text-sm bg-white/10 p-2 rounded-lg backdrop-blur-sm hover:bg-white/20 transition-colors">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                      </svg>
                    </a>
                  )}
                  {github && (
                    <a href={github} target="_blank" rel="noopener noreferrer" className="text-sm bg-white/10 p-2 rounded-lg backdrop-blur-sm hover:bg-white/20 transition-colors">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                      </svg>
                    </a>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      <div className="p-8">{/* Professional Summary */}

      {/* Professional Summary */}
      {summary && summary.trim() && (
        <section className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-emerald-500 to-teal-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-slate-800">Professional Summary</h2>
          </div>
          <p className="text-slate-700 leading-relaxed text-base pl-7">{summary}</p>
        </section>
      )}

      {/* Key Skills */}
      {skillsList.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-violet-500 to-purple-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-slate-800">Key Skills</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 pl-7">
            {skillsList.map((skill, i) => {
              const skillName = typeof skill === 'object' ? skill.name : skill;
              const skillLevel = typeof skill === 'object' ? skill.level : null;
              
              return (
                <div
                  key={i}
                  className="bg-gradient-to-br from-slate-50 to-gray-100 border border-slate-200 px-4 py-3 rounded-lg text-sm font-semibold text-slate-700 hover:shadow-md hover:border-violet-300 transition-all group"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-violet-500 rounded-full group-hover:bg-purple-500 transition-colors"></span>
                    <span className="flex-1">{skillName}</span>
                    {skillLevel && (
                      <span className="text-xs text-violet-600 font-bold">
                        {skillLevel}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Work Experience */}
      {experienceList.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-slate-800">Professional Experience</h2>
          </div>
          <div className="pl-7 space-y-6">
            {experienceList.map((job, i) => {
              const jobTitle = job.title || job.role || job.position || "";
              const company = job.company || job.employer || "";
              const dates = job.dates || job.years || job.duration || job.period || "";
              const description = job.description || "";
              const points = job.points || job.responsibilities || job.achievements || [];
              
              if (!jobTitle && !company) return null;
              
              return (
                <div key={i} className="relative pl-6 border-l-2 border-slate-200 pb-6 last:pb-0 hover:border-blue-400 transition-colors">
                  <div className="absolute -left-[9px] top-0 w-4 h-4 bg-blue-500 rounded-full border-4 border-white shadow-md"></div>
                  <div className="flex flex-wrap justify-between items-start gap-3 mb-3">
                    <div className="flex-1">
                      {jobTitle && (
                        <h3 className="text-lg font-bold text-slate-800">
                          {jobTitle}
                        </h3>
                      )}
                      {company && (
                        <p className="text-base font-semibold text-blue-600 mt-1">
                          {company}
                        </p>
                      )}
                    </div>
                    {dates && (
                      <span className="text-sm font-medium text-slate-600 bg-slate-100 px-4 py-1.5 rounded-full whitespace-nowrap">
                        {dates}
                      </span>
                    )}
                  </div>
                  {(description || points.length > 0) && (
                    <div className="mt-3">
                      {description && (
                        <p className="text-slate-700 leading-relaxed mb-3">
                          {description}
                        </p>
                      )}
                      {Array.isArray(points) && points.length > 0 && (
                        <ul className="space-y-2">
                          {points.map((point, j) => (
                            <li key={j} className="text-slate-700 flex items-start gap-3">
                              <span className="text-blue-500 mt-1.5 flex-shrink-0">
                                <svg className="w-2 h-2 fill-current" viewBox="0 0 8 8">
                                  <circle cx="4" cy="4" r="4" />
                                </svg>
                              </span>
                              <span className="flex-1">{point}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Projects */}
      {projectList.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-amber-500 to-orange-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-slate-800">Notable Projects</h2>
          </div>
          <div className="pl-7 grid gap-4">
            {projectList.map((project, i) => {
              const projectName = project.name || project.title || "";
              const projectDesc = project.desc || project.description || "";
              const technologies = project.technologies || project.tech || [];
              
              if (!projectName && !projectDesc) return null;
              
              return (
                <div key={i} className="bg-gradient-to-br from-slate-50 to-amber-50 border border-slate-200 p-5 rounded-xl hover:shadow-lg hover:border-amber-300 transition-all">
                  {projectName && (
                    <h3 className="font-bold text-lg text-slate-800 mb-2">
                      {projectName}
                    </h3>
                  )}
                  {projectDesc && (
                    <p className="text-slate-700 leading-relaxed mb-4">
                      {projectDesc}
                    </p>
                  )}
                  {Array.isArray(technologies) && technologies.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {technologies.map((tech, j) => (
                        <span
                          key={j}
                          className="bg-white border border-amber-300 text-amber-700 px-3 py-1 rounded-full text-xs font-semibold"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Education */}
      {educationList.length > 0 && (
        <section className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-rose-500 to-pink-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-slate-800">Education</h2>
          </div>
          <div className="pl-7 space-y-4">
            {educationList.map((edu, i) => {
              const degree = edu.degree || edu.qualification || "";
              const school = edu.school || edu.institution || edu.university || "";
              const year = edu.year || edu.years || edu.graduation || "";
              const details = edu.details || edu.gpa || "";
              
              if (!degree && !school) return null;
              
              return (
                <div key={i} className="bg-gradient-to-r from-slate-50 to-rose-50 border border-slate-200 p-4 rounded-lg hover:shadow-md hover:border-rose-300 transition-all">
                  <div className="flex flex-wrap justify-between items-start gap-3">
                    <div className="flex-1">
                      {degree && (
                        <h3 className="font-bold text-base text-slate-800">
                          {degree}
                        </h3>
                      )}
                      {school && (
                        <p className="text-base font-semibold text-rose-600 mt-1">
                          {school}
                        </p>
                      )}
                      {details && (
                        <p className="text-sm text-slate-600 mt-1">
                          {details}
                        </p>
                      )}
                    </div>
                    {year && (
                      <span className="text-sm font-medium text-slate-600 bg-white px-4 py-1.5 rounded-full whitespace-nowrap border border-slate-200">
                        {year}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Certifications & Awards */}
      {certificationList.length > 0 && (
        <section className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-teal-500 to-cyan-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-slate-800">Certifications & Awards</h2>
          </div>
          <div className="pl-7 grid md:grid-cols-2 gap-3">
            {certificationList.map((cert, i) => (
              <div key={i} className="flex items-start gap-3 bg-gradient-to-r from-slate-50 to-teal-50 border border-slate-200 p-4 rounded-lg hover:shadow-md hover:border-teal-300 transition-all">
                <div className="flex-shrink-0 w-6 h-6 bg-teal-500 rounded-full flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="text-slate-700 font-medium flex-1 leading-relaxed">{cert}</span>
              </div>
            ))}
          </div>
        </section>
      )}
      </div>
    </div>
  );
}
