from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson import ObjectId
import gridfs
from gridfs.errors import NoFile
import io
import json
from app.utils.cv_utils import extract_text_from_any, generate_pdf, optimize_cv
from app.utils.cv_template_mapper import normalize_cv_for_template

files_bp = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _serialize_grid_file(grid_file):
    """Return a serializable snapshot of a GridFS file."""
    uploaded_at = getattr(grid_file, 'upload_date', None)
    display_name = getattr(grid_file, 'original_filename', None) or grid_file.filename
    return {
        "_id": str(grid_file._id),
        "filename": display_name,
        "storageFilename": grid_file.filename,
        "contentType": getattr(grid_file, 'content_type', None),
        "uploadedAt": uploaded_at.isoformat() if uploaded_at else None,
        "size": getattr(grid_file, 'length', None),
        "jobDomain": getattr(grid_file, 'job_domain', None),
        "atsScore": getattr(grid_file, 'ats_score', None),
    }


@files_bp.route('/upload-cv', methods=['POST'])
@login_required
def upload_cv():
    if 'cv_file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['cv_file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type"}), 400

    try:
        # Read file bytes once
        file_bytes = file.read()
        
        # ═══════════════════════════════════════════════════════════════
        # UNIFIED SPACY-BASED EXTRACTION SYSTEM
        # ═══════════════════════════════════════════════════════════════
        from app.services.unified_cv_extractor import get_cv_extractor
        
        try:
            # Use unified spaCy-based extraction system
            extractor = get_cv_extractor()
            extraction_result = extractor.extract_from_file(file_bytes, file.filename)
            text = extraction_result['cleaned_text']
            text_extraction_metadata = {
                'method': extraction_result['extraction_method'],
                'char_count': len(text),
                'word_count': len(text.split()),
            }
            current_app.logger.info(f"✨ Unified extraction: {extraction_result['extraction_method']}, "
                                  f"{len(text.split())} words")
        except Exception as e:
            current_app.logger.warning(f"Unified extraction failed, using fallback: {e}")
            # Fallback to legacy extraction
            from app.utils.cv_utils import extract_text_from_any
            text = extract_text_from_any(file_bytes, file.filename)
            text_extraction_metadata = {}

        # Accept optional job_domain form field to tailor optimization
        job_domain = request.form.get('job_domain') or request.form.get('domain') or request.form.get('target_domain')

        # ═══════════════════════════════════════════════════════════════
        # STEP 1: SPACY-BASED EXTRACTION WITH CUSTOM RULES
        # ═══════════════════════════════════════════════════════════════
        # Extract structured data from the extraction result
        entities = extraction_result.get('entities', {})
        sections = extraction_result.get('sections', {})
        
        # Build contact info from extracted entities
        contact_info = {
            'name': entities.get('name'),
            'email': entities.get('email'),
            'phone': entities.get('phone'),
            'location': entities.get('location'),
        }
        current_app.logger.info(f"📧 Unified extraction: name={contact_info.get('name')}, email={contact_info.get('email')}, phone={contact_info.get('phone')}")
        
        # Build structured sections from entities
        structured_sections = {
            'skills': {'technical': entities.get('skills', [])},
            'work_experience': entities.get('experience', []),
            'education': entities.get('education', []),
            'professional_summary': entities.get('summary', ''),
            'certifications': [],
            'projects': [],
        }
        
        # Build primary extraction data package
        primary_extraction = {
            'contact_info': contact_info,
            'skills': structured_sections.get('skills', {}),
            'experience': structured_sections.get('work_experience', []),
            'education': structured_sections.get('education', []),
            'summary': structured_sections.get('professional_summary', ''),
            'certifications': structured_sections.get('certifications', []),
            'projects': structured_sections.get('projects', []),
        }
        
        # Use entities as final extraction (spaCy-based extraction is already robust)
        final_extraction = primary_extraction
        
        # Combine all extraction metadata
        extraction_metadata = {
            **text_extraction_metadata,  # Text extraction (PyMuPDF, etc.)
            'extraction_method': 'spacy_custom_rules',
            'sections_found': list(sections.keys()),
        }
        
        # Build contact validation result
        completeness = sum([1 for field in ['name', 'email', 'phone'] if contact_info.get(field)])
        missing_fields = [field for field in ['name', 'email', 'phone'] if not contact_info.get(field)]
        
        contact_validation = {
            'is_complete': completeness == 3,
            'completeness': completeness,
            'score': (completeness / 3) * 100,
            'missing_fields': missing_fields
        }
        
        # Log extraction results
        current_app.logger.info(f"✅ Extraction completeness: {contact_validation['score']:.1f}%")
        current_app.logger.info(f"📊 Extraction method: spaCy with custom rules")

        # ═══════════════════════════════════════════════════════════════
        # STEP 2: ANALYZE ATS SCORE
        # ═══════════════════════════════════════════════════════════════
        from app.utils.cv_utils import analyze_ats_score_detailed
        ats_analysis = analyze_ats_score_detailed(text, job_domain)
        ats_score = ats_analysis['overall_score']
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: FORMAT EXTRACTED TEXT WITH MODERN PRESENTATION
        # ═══════════════════════════════════════════════════════════════
        from app.utils.cv_utils import format_extracted_text_with_sections
        from app.utils.modern_formatter import format_cv_modern
        
        # Use final extraction data (with AI fallback if used)
        structured_data = {
            'professional_summary': final_extraction.get('summary', ''),
            'skills': final_extraction.get('skills', {}),
            'work_experience': final_extraction.get('experience', []),
            'education': final_extraction.get('education', []),
            'certifications': final_extraction.get('certifications', []),
            'projects': final_extraction.get('projects', []),
            'contact_information': contact_info,
        }
        
        # Legacy formatted output (backward compatibility)
        formatted_result = format_extracted_text_with_sections(text)
        formatted_text = formatted_result['formatted_text']
        text_sections = formatted_result['sections']
        section_order = formatted_result['section_order']
        
        # Modern Rich-formatted output
        modern_formatted = {
            'text': '',
            'html': '',
            'markdown': ''
        }
        
        try:
            cv_display_data = {
                'name': contact_info.get('name', ''),
                'contact_info': contact_info,
                'professional_summary': structured_data.get('professional_summary', ''),
                'skills': structured_data.get('skills', {}),
                'work_experience': structured_data.get('work_experience', []),
                'projects': structured_data.get('projects', []),
                'education': structured_data.get('education', []),
                'certifications': structured_data.get('certifications', []),
                'structured_data': structured_data
            }
            
            modern_formatted['text'] = format_cv_modern(cv_display_data, 'text')
            modern_formatted['html'] = format_cv_modern(cv_display_data, 'html')
            modern_formatted['markdown'] = format_cv_modern(cv_display_data, 'markdown')
            
            current_app.logger.info(f"✨ Modern formatting applied: text, html, markdown")
        except Exception as e:
            current_app.logger.warning(f"Modern formatting failed: {e}")
            modern_formatted = {'text': formatted_text, 'html': '', 'markdown': ''}
        
        current_app.logger.info(f"📋 Formatted text into {len(section_order)} sections: {', '.join(section_order)}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: CONDITIONAL OPTIMIZATION (BASED ON ATS SCORE)
        # ═══════════════════════════════════════════════════════════════
        # If ATS score >= 75: minimal processing, return original with analysis
        # If ATS score < 75: full AI optimization with keywords and proper formatting
        if ats_score >= 75:
            current_app.logger.info(f"High ATS score ({ats_score}), skipping optimization")
            # Build basic structure without heavy AI processing
            from app.utils.cv_utils import build_standardized_sections, build_structured_cv_payload
            structured = build_standardized_sections(text)
            
            # Inject extracted contact info into structured payload
            structured_payload = build_structured_cv_payload(structured)
            if 'Personal Information' not in structured_payload or not structured_payload['Personal Information']:
                structured_payload['Personal Information'] = contact_info
            else:
                # Merge with existing data, preferring extracted values
                existing = structured_payload['Personal Information']
                for field in ['name', 'email', 'phone', 'linkedin', 'github']:
                    if contact_info.get(field) and not existing.get(field):
                        existing[field] = contact_info[field]
            
            result = {
                "optimized_text": text,
                "optimized_cv": text,
                "optimized_ats_cv": text,
                "formatted_text": formatted_text,  # Add formatted text with sections
                "text_sections": text_sections,  # Add individual sections
                "section_order": section_order,  # Add section order
                "sections": {},
                "structured_cv": structured_payload,
                "contact_info": contact_info,  # Add extracted contact info
                "contact_validation": contact_validation,  # Add validation results
                "ats_score": ats_score,
                "ats_analysis": ats_analysis,
                "recommended_keywords": ats_analysis['missing_keywords'],
                "found_keywords": ats_analysis['found_keywords'],
                "suggestions": [{"category": "info", "message": "Your CV already has a good ATS score! Minor improvements suggested below."}] + 
                              [{"category": "improvement", "message": rec} for rec in ats_analysis['recommendations']],
                "extracted_text": text,
                "needs_optimization": False
            }
        else:
            current_app.logger.info(f"Low ATS score ({ats_score}), generating optimized CV")
            # Full AI-powered optimization with keywords
            result = optimize_cv(text, job_domain=job_domain, use_ai=True)
            
            # Inject extracted contact info, formatted text, and ATS analysis into result
            if result:
                result['ats_score'] = ats_score
                result['ats_analysis'] = ats_analysis
                result['needs_optimization'] = True
                result['contact_info'] = contact_info  # Add extracted contact info
                result['contact_validation'] = contact_validation  # Add validation results
                result['formatted_text'] = formatted_text  # Add formatted text with sections
                result['text_sections'] = text_sections  # Add individual sections
                result['section_order'] = section_order  # Add section order
                
                # Ensure contact info is in structured_cv
                if 'structured_cv' in result and isinstance(result['structured_cv'], dict):
                    if 'Personal Information' not in result['structured_cv'] or not result['structured_cv']['Personal Information']:
                        result['structured_cv']['Personal Information'] = contact_info
                    else:
                        # Merge with existing data
                        existing = result['structured_cv']['Personal Information']
                        for field in ['name', 'email', 'phone', 'linkedin', 'github']:
                            if contact_info.get(field) and not existing.get(field):
                                existing[field] = contact_info[field]

        if not isinstance(result, dict):
            current_app.logger.warning('optimize_cv returned non-dict result; using safe defaults')
            result = {}

        optimized_cv = result.get('optimized_text') or result.get('optimized_cv') or text
        optimized_ats_cv = result.get('optimized_ats_cv') or optimized_cv
        template_data = result.get('template_data') or {}
        suggestions = result.get('suggestions') or []
        # normalize suggestions into list of {category, message}
        grouped = {}
        try:
            if isinstance(suggestions, dict):
                # if AI returned grouped suggestions already
                grouped = suggestions
            else:
                for s in suggestions:
                    if isinstance(s, dict):
                        cat = s.get('category', 'general')
                        grouped.setdefault(cat, []).append(s.get('message'))
                    else:
                        # string
                        grouped.setdefault('general', []).append(str(s))
        except Exception:
            grouped = {'general': [str(suggestions)]}
        sections = result.get('sections', {})
        ordered_sections = result.get('ordered_sections') or []
        structured_sections = result.get('structured_sections') or {}
        structured_cv = result.get('structured_cv') or {}
        ats_score = result.get('ats_score')
        recommended_keywords = result.get('recommended_keywords', [])
        found_keywords = result.get('found_keywords', [])
        extracted_text = result.get('extracted_text') or text
        structured_payload = structured_cv if isinstance(structured_cv, dict) else {}

        # Normalize structured CV data for the template component
        # Try different sources for normalization in order of preference
        normalization_source = None
        if structured_payload and any(structured_payload.values()):
            normalization_source = structured_payload
        elif result.get('extracted') and isinstance(result.get('extracted'), dict):
            normalization_source = result['extracted']
        elif result.get('template_data') and isinstance(result.get('template_data'), dict):
            normalization_source = result['template_data']
        
        if normalization_source:
            template_data = normalize_cv_for_template(normalization_source)
        else:
            # Fallback to empty template if no source available
            template_data = {}
        
        current_app.logger.info(f"Template data created - Name: {template_data.get('name')}, Skills: {len(template_data.get('skills', []))}, Experience: {len(template_data.get('experience', []))}")

        # Generate PDF with structured data for better formatting
        try:
            # Pass structured CV data to generate_pdf for professional HTML/CSS rendering
            if structured_payload and any(structured_payload.values()):
                pdf_bytes = generate_pdf(structured_payload)
            else:
                pdf_bytes = generate_pdf(optimized_ats_cv)
        except Exception as e:
            current_app.logger.warning("Error generating PDF, returning fallback text version: %s", e)
            pdf_bytes = generate_pdf(optimized_ats_cv)

        fs = gridfs.GridFS(current_app.mongo.db)
        # Create a clean, descriptive filename for the optimized CV
        base_name = file.filename.rsplit('.', 1)[0]
        optimized_filename = secure_filename(f"{base_name}_ATS_Optimized.pdf")
        
        pdf_bytes.seek(0)
        file_id = fs.put(
            pdf_bytes.read(),
            filename=optimized_filename,
            content_type='application/pdf',
            user_id=str(current_user.get_id()),
            original_filename=file.filename,
            job_domain=job_domain,
            ats_score=ats_score,
        )

        try:
            stored_file = fs.get(file_id)
            file_payload = _serialize_grid_file(stored_file)
        except Exception:
            current_app.logger.warning("Unable to reload stored file metadata", exc_info=True)
            file_payload = {"_id": str(file_id), "filename": file.filename, "uploadedAt": None}

        return jsonify({
            "success": True,
            "message": "Uploaded and optimized",
            "file_id": str(file_id),
            "optimized_text": optimized_ats_cv,
            "optimized_cv": optimized_ats_cv,
            "optimized_ats_cv": optimized_ats_cv,
            "extracted": result.get('extracted') or template_data,
            "extracted_text": extracted_text,
            "formatted_text": result.get('formatted_text', ''),  # Legacy formatted text
            "text_sections": result.get('text_sections', {}),  # Individual sections
            "section_order": result.get('section_order', []),  # Section display order
            "modern_formatted": modern_formatted,  # NEW: Modern Rich-formatted outputs (text, html, markdown)
            "extraction_metadata": extraction_metadata,  # NEW: Extraction quality metrics
            "contact_info": result.get('contact_info', {}),  # Extracted contact information
            "contact_validation": result.get('contact_validation', {}),  # Validation results
            "sections": sections,
            "ordered_sections": ordered_sections,
            "structured_sections": structured_sections,
            "structured_cv": structured_payload,
            "template_data": template_data,  # Properly normalized data for ResumeTemplate
            "suggestions": suggestions,
            "grouped_suggestions": grouped,
            "ats_score": ats_score,
            "ats_analysis": result.get('ats_analysis'),  # Full ATS analysis
            "needs_optimization": result.get('needs_optimization', False),  # Whether optimization was applied
            "recommended_keywords": recommended_keywords,
            "found_keywords": found_keywords,
            "file": file_payload,
        })
    except Exception as e:
        current_app.logger.exception("Error saving/processing file to GridFS")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@files_bp.route('/debug-cv/<file_id>', methods=['GET'])
@login_required
def debug_cv_data(file_id):
    """Debug endpoint to inspect raw CV data before template normalization"""
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        file_obj = fs.get(ObjectId(file_id))
        
        # Check authorization
        if str(getattr(file_obj, 'user_id', '')) != str(current_user.get_id()):
            return jsonify({"success": False, "message": "Not authorized"}), 403
        
        # Get the metadata
        metadata = file_obj.metadata or {}
        structured_cv = metadata.get('structured_cv', {})
        
        # Return debug information
        debug_info = {
            "file_id": file_id,
            "filename": file_obj.filename,
            "has_structured_cv": bool(structured_cv),
            "structured_cv_keys": list(structured_cv.keys()) if isinstance(structured_cv, dict) else "Not a dict",
            "raw_structured_cv": json.dumps(structured_cv, indent=2, default=str),
            "normalized_preview": None
        }
        
        # Try normalizing
        if structured_cv:
            try:
                normalized = normalize_cv_for_template(structured_cv)
                debug_info["normalized_preview"] = {
                    "name": normalized.get('name'),
                    "email": normalized.get('email'),
                    "skills_count": len(normalized.get('skills', [])),
                    "skills_sample": normalized.get('skills', [])[:5],
                    "experience_count": len(normalized.get('experience', [])),
                    "experience_sample": normalized.get('experience', [])[:2],
                    "education_count": len(normalized.get('education', [])),
                    "education_sample": normalized.get('education', [])[:2],
                }
            except Exception as e:
                debug_info["normalization_error"] = str(e)
        
        return jsonify({"success": True, "debug": debug_info}), 200
        
    except NoFile:
        return jsonify({"success": False, "message": "File not found"}), 404
    except Exception as e:
        current_app.logger.exception("Debug endpoint error")
        return jsonify({"success": False, "message": str(e)}), 500


@files_bp.route('/download/<file_id>', methods=['GET'])
@login_required
def download(file_id):
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        file_obj = fs.get(ObjectId(file_id))
        if str(getattr(file_obj, 'user_id', '')) != str(current_user.get_id()):
            return jsonify({"success": False, "message": "Not authorized"}), 403
        
        # Use optimized filename if available, otherwise use stored filename
        download_name = file_obj.filename
        if not download_name.lower().endswith('.pdf'):
            download_name = f"{download_name}.pdf"
        
        return send_file(
            io.BytesIO(file_obj.read()),
            download_name=download_name,
            mimetype=file_obj.content_type or 'application/pdf',
            as_attachment=True,
        )
    except NoFile:
        current_app.logger.exception("Download error - file missing")
        return jsonify({"success": False, "message": "File not found"}), 404
    except Exception:
        current_app.logger.exception("Download error")
        return jsonify({"success": False, "message": "Unable to download file"}), 500


@files_bp.route('/download-optimized-cv', methods=['POST'])
@login_required
def download_optimized_cv():
    """Generate and download PDF from optimized CV data sent from frontend."""
    try:
        current_app.logger.info(f"Download request from user: {current_user.get_id()}")
        
        data = request.get_json()
        if not data:
            current_app.logger.error("No data provided in request")
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Extract CV data from request
        structured_cv = data.get('structured_cv') or data.get('template_data')
        optimized_text = data.get('optimized_text') or data.get('optimized_cv')
        filename = data.get('filename', 'Optimized_CV.pdf')
        
        # Ensure filename has .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename = f"{filename.rsplit('.', 1)[0]}_Optimized.pdf"
        
        current_app.logger.info(f"Download request - Structured CV: {bool(structured_cv)}, Text length: {len(optimized_text) if optimized_text else 0}")
        
        # Generate PDF from structured data or optimized text
        pdf_bytes = None
        if structured_cv and isinstance(structured_cv, dict) and any(structured_cv.values()):
            current_app.logger.info("Generating PDF from structured CV data")
            try:
                pdf_bytes = generate_pdf(structured_cv)
            except Exception as e:
                current_app.logger.warning(f"Failed to generate from structured data: {e}, trying text fallback")
                pdf_bytes = None
        
        if not pdf_bytes and optimized_text:
            current_app.logger.info("Generating PDF from optimized text")
            try:
                pdf_bytes = generate_pdf(optimized_text)
            except Exception as e:
                current_app.logger.error(f"Failed to generate from text: {e}")
                return jsonify({"success": False, "message": f"PDF generation failed: {str(e)}"}), 500
        
        if not pdf_bytes:
            current_app.logger.error("No valid CV data provided")
            return jsonify({"success": False, "message": "No valid CV data provided"}), 400
        
        # Ensure we're at the start of the BytesIO
        pdf_bytes.seek(0)
        
        current_app.logger.info(f"Sending PDF file: {filename}")
        
        # Use the correct parameter name for Flask's send_file
        # In Flask 2.0+, it's 'download_name', in older versions it's 'attachment_filename'
        try:
            return send_file(
                pdf_bytes,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        except TypeError:
            # Fallback for older Flask versions
            return send_file(
                pdf_bytes,
                mimetype='application/pdf',
                as_attachment=True,
                attachment_filename=filename
            )
    except Exception as e:
        current_app.logger.exception("Error generating optimized CV PDF")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@files_bp.route('/delete-cv/<file_id>', methods=['DELETE'])
@login_required
def delete_cv(file_id):
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        file_obj = fs.get(ObjectId(file_id))
        if str(getattr(file_obj, 'user_id', '')) != str(current_user.get_id()):
            return jsonify({"success": False, "message": "Not authorized"}), 403
        fs.delete(ObjectId(file_id))
        return jsonify({"success": True, "message": "Deleted"})
    except Exception as e:
        current_app.logger.exception("Delete error")
        return jsonify({"success": False, "message": "File not found"}), 404


@files_bp.route('/user-files')
@login_required
def user_files():
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        cursor = fs.find({"user_id": str(current_user.get_id())}).sort("uploadDate", -1)
        files = [_serialize_grid_file(f) for f in cursor]
        return jsonify({"files": files})
    except Exception as e:
        current_app.logger.exception("List files error")
        return jsonify({"files": []}), 200


@files_bp.route('/current-user')
def current_user_info():
    try:
        if current_user.is_authenticated:
            return jsonify({"user": {"id": str(current_user.get_id()), "full_name": getattr(current_user, 'full_name', None), "username": getattr(current_user, 'username', None), "email": getattr(current_user, 'email', None)}})
        return jsonify({"user": None})
    except Exception:
        return jsonify({"user": None})


@files_bp.route('/generate-pdf-from-json', methods=['POST'])
@login_required
def generate_pdf_from_json():
    """
    Generate a PDF from structured CV JSON data (for creating new CVs).
    Accepts CV data in JSON format and returns a PDF file.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No CV data provided"}), 400
        
        current_app.logger.info(f"Generating PDF from JSON for user: {current_user.get_id()}")
        
        # Extract CV structure from request
        cv_data = data.get('cv_data') or data.get('structured_cv') or data
        filename = data.get('filename', 'Generated_CV.pdf')
        
        # Ensure filename has .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename = f"{filename.rsplit('.', 1)[0]}.pdf"
        
        # Generate PDF from structured CV data
        try:
            pdf_bytes = generate_pdf(cv_data)
            pdf_bytes.seek(0)
        except Exception as e:
            current_app.logger.error(f"PDF generation failed: {e}")
            return jsonify({"success": False, "message": f"PDF generation failed: {str(e)}"}), 500
        
        # Optionally save to GridFS if requested
        save_to_storage = data.get('save_to_storage', False)
        file_id = None
        
        if save_to_storage:
            try:
                fs = gridfs.GridFS(current_app.mongo.db)
                pdf_bytes.seek(0)
                file_id = fs.put(
                    pdf_bytes.read(),
                    filename=secure_filename(filename),
                    content_type='application/pdf',
                    user_id=str(current_user.get_id()),
                    cv_type='generated'
                )
                current_app.logger.info(f"Saved generated CV to GridFS: {file_id}")
                pdf_bytes.seek(0)
            except Exception as e:
                current_app.logger.warning(f"Failed to save to GridFS: {e}")
        
        # Return PDF file for download
        response_data = {
            "success": True,
            "message": "CV PDF generated successfully"
        }
        
        if file_id:
            response_data["file_id"] = str(file_id)
        
        # For download requests, return the file directly
        if data.get('download', True):
            return send_file(
                pdf_bytes,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            # Return JSON response with file info
            return jsonify(response_data)
            
    except Exception as e:
        current_app.logger.exception("Error in generate_pdf_from_json")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@files_bp.route('/improve-cv-with-ai', methods=['POST'])
@login_required
def improve_cv_with_ai():
    """
    Improve CV content using Phi-3 AI.
    Enhances professional summary and experience descriptions while preserving facts.
    """
    try:
        data = request.get_json()
        cv_data = data.get('cv_data')
        
        if not cv_data:
            return jsonify({
                "success": False, 
                "message": "Missing cv_data in request"
            }), 400
        
        current_app.logger.info("🎨 CV Improvement requested")
        
        # Use Gemini AI for improvement
        from app.utils.cv_utils import optimize_cv
        
        # Convert cv_data to text format
        cv_text = json.dumps(cv_data, indent=2)
        result = optimize_cv(cv_text, use_ai=True)
        
        if not result or not result.get('optimized_text'):
            return jsonify({
                "success": False,
                "message": "AI improvement failed"
            }), 500
        
        improved_data = result
        
        return jsonify({
            "success": True,
            "message": "CV improved successfully",
            "improved_cv": improved_data,
            "original_cv": cv_data
        })
        
    except Exception as e:
        current_app.logger.exception("Error in improve_cv_with_ai")
        return jsonify({
            "success": False, 
            "message": f"Server error: {str(e)}"
        }), 500

