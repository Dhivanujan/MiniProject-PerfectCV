from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson import ObjectId
import gridfs
import io
from app.utils.cv_utils import extract_text_from_pdf, generate_pdf, optimize_cv

files_bp = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        # Extract text depending on type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(io.BytesIO(file_bytes))
        else:
            try:
                text = file_bytes.decode('utf-8', errors='ignore')
            except Exception:
                text = ''

        # Accept optional job_domain form field to tailor optimization
        job_domain = request.form.get('job_domain') or request.form.get('domain') or request.form.get('target_domain')

        # Attempt optimization (AI); function will fallback to rule-based if AI not configured
        result = optimize_cv(text, job_domain=job_domain, use_ai=True)

        if not isinstance(result, dict):
            current_app.logger.warning('optimize_cv returned non-dict result; using safe defaults')
            result = {}

        optimized_cv = result.get('optimized_text') or result.get('optimized_cv') or text
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
        ats_score = result.get('ats_score')
        recommended_keywords = result.get('recommended_keywords', [])
        found_keywords = result.get('found_keywords', [])

        # Generate PDF directly from optimized preview text to ensure parity with UI
        try:
            pdf_bytes = generate_pdf(optimized_cv)
        except Exception as e:
            current_app.logger.warning("Error generating PDF, returning fallback text version: %s", e)
            pdf_bytes = generate_pdf(text)

        fs = gridfs.GridFS(current_app.mongo.db)
        filename = secure_filename(f"ATS_{current_user.get_id()}_{file.filename.rsplit('.',1)[0]}.pdf")
        file_id = fs.put(pdf_bytes.read(), filename=filename, content_type='application/pdf', user_id=str(current_user.get_id()))

        return jsonify({
            "success": True,
            "message": "Uploaded and optimized",
            "file_id": str(file_id),
            "optimized_text": optimized_cv,
            "optimized_cv": optimized_cv,
            "extracted": result.get('extracted') or template_data,
            "sections": sections,
            "ordered_sections": ordered_sections,
            "structured_sections": structured_sections,
            "template_data": template_data,
            "suggestions": suggestions,
            "grouped_suggestions": grouped,
            "ats_score": ats_score,
            "recommended_keywords": recommended_keywords,
            "found_keywords": found_keywords,
        })
    except Exception as e:
        current_app.logger.exception("Error saving/processing file to GridFS")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@files_bp.route('/download/<file_id>', methods=['GET'])
@login_required
def download(file_id):
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        file_obj = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(file_obj.read()), download_name=file_obj.filename, mimetype=file_obj.content_type, as_attachment=True)
    except Exception as e:
        current_app.logger.exception("Download error")
        return jsonify({"success": False, "message": "File not found"}), 404


@files_bp.route('/delete-cv/<file_id>', methods=['DELETE'])
@login_required
def delete_cv(file_id):
    try:
        fs = gridfs.GridFS(current_app.mongo.db)
        file_obj = fs.get(ObjectId(file_id))
        if str(file_obj.user_id) != str(current_user.get_id()):
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
        cursor = fs.find({"user_id": str(current_user.get_id())})
        files = [{"_id": str(f._id), "filename": f.filename} for f in cursor]
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
