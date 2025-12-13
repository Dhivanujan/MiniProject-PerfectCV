"""
Updated files route using clean architecture and new services.
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson import ObjectId
import gridfs
import io
import logging

from app.services.extraction_service import ExtractionService
from app.services.validation_service import ValidationService
from app.services.ai_service import AIService
from app.services.cv_generation_service import CVGenerationService
from config.config import Config

logger = logging.getLogger(__name__)

files_bp_v2 = Blueprint('files_v2', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@files_bp_v2.route('/upload-cv-v2', methods=['POST'])
@login_required
def upload_cv_v2():
    """
    Enhanced CV upload endpoint with full extraction and AI processing.
    
    Process:
    1. Extract text from PDF/DOCX
    2. Clean and normalize text
    3. Extract entities using spaCy + regex
    4. Validate extracted data
    5. Use AI fallback for missing fields (if available)
    6. Improve CV content with AI (if requested)
    7. Generate ATS-optimized PDF
    8. Store in GridFS and return results
    """
    # Validate request
    if 'cv_file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['cv_file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type. Allowed: PDF, DOCX"}), 400
    
    # Get optional parameters
    job_domain = request.form.get('job_domain') or request.form.get('domain')
    use_ai_improvement = request.form.get('use_ai', 'true').lower() == 'true'
    
    try:
        logger.info(f"Processing CV upload: {file.filename} for user: {current_user.get_id()}")
        
        # Read file bytes
        file_bytes = file.read()
        
        # ==========================================
        # STAGE 1-4: EXTRACTION AND VALIDATION
        # ==========================================
        logger.info("=" * 50)
        logger.info("STAGE 1-4: TEXT EXTRACTION AND ENTITY RECOGNITION")
        logger.info("=" * 50)
        
        extraction_service = ExtractionService()
        cv_data = extraction_service.process_cv(file_bytes, file.filename)
        
        entities = cv_data['entities']
        sections = cv_data['sections']
        cleaned_text = cv_data['cleaned_text']
        
        # Validate extracted data
        validation_service = ValidationService()
        validation_report = validation_service.get_validation_report(entities, sections)
        
        logger.info(f"Validation: completeness={validation_report['completeness_score']:.1f}%, "
                   f"valid={validation_report['is_valid']}")
        
        # ==========================================
        # STAGE 5: AI FALLBACK FOR MISSING FIELDS
        # ==========================================
        if validation_report['missing_critical'] and use_ai_improvement:
            logger.info("=" * 50)
            logger.info("STAGE 5: AI FALLBACK FOR MISSING FIELDS")
            logger.info("=" * 50)
            
            ai_service = AIService(
                openai_api_key=getattr(Config, 'OPENAI_API_KEY', None),
                google_api_key=getattr(Config, 'GOOGLE_API_KEY', None),
                groq_api_key=getattr(Config, 'GROQ_API_KEY', None),
                provider=getattr(Config, 'AI_PROVIDER', 'openai')
            )
            
            if ai_service.is_available():
                logger.info(f"Using AI to extract missing fields: {validation_report['missing_critical']}")
                ai_extracted = ai_service.extract_missing_fields(
                    cleaned_text, 
                    validation_report['missing_critical']
                )
                
                # Merge AI-extracted fields
                for field, value in ai_extracted.items():
                    if value and not entities.get(field):
                        entities[field] = value
                        logger.info(f"AI extracted {field}: {value}")
                
                # Re-validate
                validation_report = validation_service.get_validation_report(entities, sections)
                logger.info(f"Post-AI validation: completeness={validation_report['completeness_score']:.1f}%")
            else:
                logger.warning("AI service not available for fallback extraction")
        
        # ==========================================
        # STAGE 6: AI CONTENT IMPROVEMENT
        # ==========================================
        improved_sections = sections.copy()
        if use_ai_improvement and (sections.get('summary') or sections.get('experience')):
            logger.info("=" * 50)
            logger.info("STAGE 6: AI CONTENT IMPROVEMENT")
            logger.info("=" * 50)
            
            ai_service = AIService(
                openai_api_key=getattr(Config, 'OPENAI_API_KEY', None),
                google_api_key=getattr(Config, 'GOOGLE_API_KEY', None),
                groq_api_key=getattr(Config, 'GROQ_API_KEY', None),
                provider=getattr(Config, 'AI_PROVIDER', 'openai')
            )
            
            if ai_service.is_available():
                logger.info(f"Improving CV content for domain: {job_domain or 'general'}")
                improved_sections = ai_service.improve_cv_content(sections, job_domain)
                logger.info("CV content improved by AI")
            else:
                logger.warning("AI service not available for content improvement")
        
        # ==========================================
        # STAGE 7: GENERATE ATS-OPTIMIZED PDF
        # ==========================================
        logger.info("=" * 50)
        logger.info("STAGE 7: GENERATING ATS-OPTIMIZED PDF")
        logger.info("=" * 50)
        
        generation_service = CVGenerationService()
        
        # Prepare CV data with improved sections
        final_cv_data = cv_data.copy()
        final_cv_data['sections'] = improved_sections
        
        pdf_bytes = generation_service.generate_cv_pdf(final_cv_data, template_name='professional.html')
        logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")
        
        # ==========================================
        # STAGE 8: STORE IN GRIDFS
        # ==========================================
        logger.info("=" * 50)
        logger.info("STAGE 8: STORING IN GRIDFS")
        logger.info("=" * 50)
        
        fs = gridfs.GridFS(current_app.mongo.db)
        filename = secure_filename(f"ATS_{current_user.get_id()}_{file.filename.rsplit('.', 1)[0]}.pdf")
        
        # Store with metadata
        file_id = fs.put(
            pdf_bytes,
            filename=filename,
            content_type='application/pdf',
            original_filename=file.filename,
            user_id=current_user.get_id(),
            job_domain=job_domain,
            ats_score=validation_report['completeness_score'],
            extraction_method=cv_data.get('extraction_method'),
            ai_improved=use_ai_improvement,
            entities=entities,
            sections=list(sections.keys())
        )
        
        logger.info(f"Stored in GridFS with ID: {file_id}")
        
        # ==========================================
        # PREPARE RESPONSE
        # ==========================================
        
        # Build suggestions
        suggestions_list = []
        for warning in validation_report['warnings']:
            suggestions_list.append({'category': 'warning', 'message': warning})
        for suggestion in validation_report['suggestions']:
            suggestions_list.append({'category': 'suggestion', 'message': suggestion})
        
        response_data = {
            "success": True,
            "message": "CV processed successfully",
            "file_id": str(file_id),
            "filename": filename,
            "original_filename": file.filename,
            
            # Extraction results
            "extraction": {
                "method": cv_data.get('extraction_method'),
                "sections_found": list(sections.keys()),
                "entities_extracted": {
                    "name": entities.get('name'),
                    "email": entities.get('email'),
                    "phone": entities.get('phone'),
                    "location": entities.get('location'),
                    "skills_count": len(entities.get('skills', [])),
                    "organizations_count": len(entities.get('organizations', [])),
                }
            },
            
            # Validation results
            "validation": {
                "is_complete": validation_report['is_valid'],
                "completeness_score": round(validation_report['completeness_score'], 1),
                "missing_critical": validation_report['missing_critical'],
                "missing_important": validation_report['missing_important'],
            },
            
            # Processing info
            "processing": {
                "ai_used": use_ai_improvement,
                "job_domain": job_domain,
                "improvements_applied": use_ai_improvement and ai_service.is_available()
            },
            
            # Suggestions
            "suggestions": suggestions_list,
            
            # Data for frontend display
            "cv_data": {
                "name": entities.get('name', 'Unknown'),
                "email": entities.get('email', ''),
                "phone": entities.get('phone', ''),
                "summary": improved_sections.get('summary', ''),
                "skills": entities.get('skills', []),
                "experience": improved_sections.get('experience', ''),
            }
        }
        
        logger.info("=" * 50)
        logger.info("CV PROCESSING COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
        return jsonify(response_data), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"success": False, "message": str(e)}), 400
    
    except Exception as e:
        logger.exception(f"Error processing CV: {e}")
        return jsonify({
            "success": False, 
            "message": "An error occurred while processing your CV. Please try again.",
            "error": str(e)
        }), 500


@files_bp_v2.route('/download-cv/<file_id>', methods=['GET'])
@login_required
def download_cv_v2(file_id):
    """Download processed CV from GridFS."""
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        grid_file = fs.get(ObjectId(file_id))
        
        # Verify ownership
        if grid_file.user_id != current_user.get_id():
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        return send_file(
            io.BytesIO(grid_file.read()),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=grid_file.filename
        )
    
    except Exception as e:
        logger.error(f"Error downloading CV: {e}")
        return jsonify({"success": False, "message": "File not found"}), 404


@files_bp_v2.route('/cv-list', methods=['GET'])
@login_required
def list_cvs_v2():
    """List all CVs for current user."""
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        
        # Find user's files
        files = fs.find({"user_id": current_user.get_id()}).sort("uploadDate", -1)
        
        file_list = []
        for grid_file in files:
            file_list.append({
                "_id": str(grid_file._id),
                "filename": grid_file.filename,
                "originalFilename": getattr(grid_file, 'original_filename', None),
                "uploadDate": grid_file.upload_date.isoformat() if grid_file.upload_date else None,
                "size": grid_file.length,
                "jobDomain": getattr(grid_file, 'job_domain', None),
                "atsScore": getattr(grid_file, 'ats_score', None),
                "extractionMethod": getattr(grid_file, 'extraction_method', None),
                "aiImproved": getattr(grid_file, 'ai_improved', False),
            })
        
        return jsonify({"success": True, "files": file_list}), 200
    
    except Exception as e:
        logger.error(f"Error listing CVs: {e}")
        return jsonify({"success": False, "message": "Error retrieving CV list"}), 500
