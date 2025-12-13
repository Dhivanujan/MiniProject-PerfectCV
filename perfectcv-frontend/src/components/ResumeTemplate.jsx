import React from 'react';
import { FaGithub, FaLinkedin, FaEnvelope, FaPhone, FaMapMarkerAlt, FaGlobe } from 'react-icons/fa';

const ResumeTemplate = ({ data }) => {
  if (!data) return null;

  // Normalization logic to handle both old 'template_data' and new 'structured_cv'
  const isStructured = !!data.personal_info;

  const normalize = (input) => {
    if (isStructured) {
      // Convert new format to a standard internal format
      return {
        header: {
          name: input.personal_info?.name || "Your Name",
          role: input.personal_info?.job_title || "",
          email: input.personal_info?.email,
          phone: input.personal_info?.phone,
          location: input.personal_info?.location,
          linkedin: input.personal_info?.linkedin,
          github: input.personal_info?.github,
          website: input.personal_info?.website,
        },
        summary: input.summary || input.professional_summary,
        skills: input.skills || {}, // Object or List
        experience: input.work_experience || input.experience || [],
        projects: input.projects || [],
        education: input.education || [],
        certifications: input.certifications || [],
        achievements: input.achievements || [],
        languages: input.languages || [],
        interests: input.interests || []
      };
    } else {
      // Legacy format
      return {
        header: {
          name: input.name || "Your Name",
          role: "", 
          contact_str: input.contact // Fallback if individual fields missing
        },
        summary: input.summary,
        skills: input.skills, // Likely a list of strings
        experience: input.experience || [],
        projects: input.projects || [],
        education: input.education || [],
        certifications: input.certifications || [],
        achievements: [],
        languages: [],
        interests: []
      };
    }
  };

  const cv = normalize(data);

  // Helper to render contact links
  const ContactItem = ({ icon: Icon, value, link }) => {
    if (!value) return null;
    return (
      <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 text-sm">
        <Icon className="text-indigo-600 dark:text-indigo-400" />
        {link ? (
          <a href={link} target="_blank" rel="noopener noreferrer" className="hover:text-indigo-600 hover:underline">
            {value}
          </a>
        ) : (
          <span>{value}</span>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-900 min-h-[1000px] w-full max-w-[210mm] mx-auto shadow-2xl overflow-hidden print:shadow-none print:w-full">
      {/* Header Section */}
      <header className="bg-slate-50 dark:bg-gray-800/50 p-8 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
              {cv.header.name}
            </h1>
            {cv.header.role && (
              <p className="text-xl text-indigo-600 dark:text-indigo-400 font-medium mt-1">
                {cv.header.role}
              </p>
            )}
            
            {/* Legacy Contact String Support */}
            {!isStructured && cv.header.contact_str && (
               <p className="text-sm text-gray-500 mt-2">{cv.header.contact_str}</p>
            )}
          </div>
          
          {isStructured && (
            <div className="flex flex-col items-end gap-2 text-right">
              {cv.header.email && <ContactItem icon={FaEnvelope} value={cv.header.email} link={`mailto:${cv.header.email}`} />}
              {cv.header.phone && <ContactItem icon={FaPhone} value={cv.header.phone} />}
              {cv.header.location && <ContactItem icon={FaMapMarkerAlt} value={cv.header.location} />}
              <div className="flex gap-4 mt-1">
                {cv.header.linkedin && (
                  <a href={cv.header.linkedin} target="_blank" rel="noreferrer" className="text-gray-500 hover:text-[#0077b5] transition-colors"><FaLinkedin size={18} /></a>
                )}
                {cv.header.github && (
                  <a href={cv.header.github} target="_blank" rel="noreferrer" className="text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"><FaGithub size={18} /></a>
                )}
                 {cv.header.website && (
                  <a href={cv.header.website} target="_blank" rel="noreferrer" className="text-gray-500 hover:text-indigo-600 transition-colors"><FaGlobe size={18} /></a>
                )}
              </div>
            </div>
          )}
        </div>
      </header>

      <div className="p-8 space-y-8">
        {/* Professional Summary */}
        {cv.summary && (
          <section>
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 border-b-2 border-indigo-500 inline-block mb-3">
              Professional Summary
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-[15px]">
              {cv.summary}
            </p>
          </section>
        )}

        {/* Technical Skills */}
        {cv.skills && (Object.keys(cv.skills).length > 0 || (Array.isArray(cv.skills) && cv.skills.length > 0)) && (
          <section>
             <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 border-b-2 border-indigo-500 inline-block mb-4">
              Technical Skills
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8">
              {Array.isArray(cv.skills) ? (
                 <div className="flex flex-wrap gap-2">
                   {cv.skills.map((skill, i) => (
                     <span key={i} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm rounded-full font-medium">
                       {skill}
                     </span>
                   ))}
                 </div>
              ) : (
                Object.entries(cv.skills).map(([category, items]) => {
                  if (!items || items.length === 0) return null;
                  const catName = category.replace(/_/g, ' ').replace('skills', '').trim();
                  return (
                    <div key={category} className="mb-2">
                      <span className="font-semibold text-gray-900 dark:text-white capitalize block mb-1.5 text-sm">
                        {catName}
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {(Array.isArray(items) ? items : [items]).map((skill, i) => (
                          <span key={i} className="px-2.5 py-0.5 bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-md">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </section>
        )}

        {/* Work Experience */}
        {cv.experience?.length > 0 && (
          <section>
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 border-b-2 border-indigo-500 inline-block mb-6">
              Work Experience
            </h2>
            <div className="space-y-6">
              {cv.experience.map((job, idx) => (
                <div key={idx} className="relative pl-4 border-l-2 border-gray-100 dark:border-gray-800 group hover:border-indigo-200 transition-colors">
                  <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-white dark:bg-gray-900 border-2 border-gray-300 dark:border-gray-600 group-hover:border-indigo-500 transition-colors" />
                  
                  <div className="flex flex-col sm:flex-row sm:items-baseline justify-between mb-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      {job.role || job.title}
                    </h3>
                    <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400 whitespace-nowrap">
                      {job.duration || job.dates}
                    </span>
                  </div>
                  
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                     {job.company} {job.location && <span className="font-normal text-gray-400">| {job.location}</span>}
                  </div>

                  <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed max-w-none">
                    {Array.isArray(job.details) || Array.isArray(job.points) ? (
                      <ul className="list-disc ml-4 space-y-1 marker:text-gray-400">
                        {(job.details || job.points).map((point, k) => (
                          <li key={k}>{point}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="whitespace-pre-line">{job.details || job.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Projects */}
        {cv.projects?.length > 0 && (
          <section className="break-inside-avoid-page">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 border-b-2 border-indigo-500 inline-block mb-5">
              Key Projects
            </h2>
            <div className="grid grid-cols-1 gap-5">
              {cv.projects.map((proj, idx) => (
                <div key={idx} className="bg-gray-50 dark:bg-gray-800/40 p-5 rounded-lg border border-gray-100 dark:border-gray-800">
                   <div className="flex justify-between items-start">
                     <h3 className="font-bold text-gray-900 dark:text-white text-[15px]">{proj.name}</h3>
                     {proj.url && (
                       <a href={proj.url} target="_blank" rel="noreferrer" className="text-xs text-indigo-500 hover:underline">View Project</a>
                     )}
                   </div>
                   
                   {proj.technologies && (
                     <div className="text-xs text-gray-500 mt-1 mb-2 font-mono">
                       {Array.isArray(proj.technologies) ? proj.technologies.join(' • ') : proj.technologies}
                     </div>
                   )}
                   
                   <p className="text-sm text-gray-700 dark:text-gray-300">
                     {proj.description || proj.desc}
                   </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Education & Certs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 break-inside-avoid-page">
          {cv.education?.length > 0 && (
            <section>
              <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 border-b-2 border-indigo-500 inline-block mb-4">
                Education
              </h2>
              <div className="space-y-4">
                {cv.education.map((edu, idx) => (
                  <div key={idx}>
                    <h3 className="font-bold text-gray-900 dark:text-white text-sm">
                      {edu.degree}
                    </h3>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {edu.institution || edu.school}
                    </div>
                     <div className="text-xs text-gray-400 mt-0.5">
                      {edu.year || edu.dates}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {(cv.certifications?.length > 0 || cv.achievements?.length > 0) && (
             <section>
              <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 border-b-2 border-indigo-500 inline-block mb-4">
                Certifications & Awards
              </h2>
              <ul className="space-y-3">
                 {[...(cv.certifications || []), ...(cv.achievements || [])].slice(0, 5).map((item, idx) => {
                   const title = typeof item === 'string' ? item : item.name;
                   const issuer = typeof item === 'object' ? item.provider || item.issuer : null;
                   return (
                     <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                       <span className="mt-1.5 w-1.5 h-1.5 bg-indigo-500 rounded-full shrink-0" />
                       <span>
                         <span className="font-medium">{title}</span>
                         {issuer && <span className="text-gray-500 text-xs block">{issuer}</span>}
                       </span>
                     </li>
                   )
                 })}
              </ul>
            </section>
          )}
        </div>
        
        {/* Languages & Interests Footer */}
        {(cv.languages?.length > 0 || cv.interests?.length > 0) && (
           <section className="pt-6 border-t border-gray-100 dark:border-gray-800 text-sm flex flex-wrap gap-8 text-gray-600 dark:text-gray-400">
              {cv.languages?.length > 0 && (
                <div>
                  <span className="font-bold text-gray-900 dark:text-white mr-2">Languages:</span>
                  {Array.isArray(cv.languages) 
                    ? cv.languages.map(l => typeof l === 'string' ? l : `${l.language} (${l.proficiency})`).join(', ')
                    : cv.languages}
                </div>
              )}
               {cv.interests?.length > 0 && (
                <div>
                  <span className="font-bold text-gray-900 dark:text-white mr-2">Interests:</span>
                  {Array.isArray(cv.interests) ? cv.interests.join(', ') : cv.interests}
                </div>
              )}
           </section>
        )}
      </div>
    </div>
  );
};

export default ResumeTemplate;
