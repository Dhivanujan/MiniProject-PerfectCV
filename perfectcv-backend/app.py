import traceback
from flask import Flask, render_template, url_for, redirect, flash, request, jsonify, send_file
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from bson import ObjectId
from werkzeug.utils import secure_filename
import gridfs

from flask import current_app
from app.utils.cv_utils import extract_text_from_any, optimize_cv
import io
from fpdf import FPDF
from PyPDF2 import PdfReader
import os 
from dotenv import load_dotenv

from flask_cors import CORS
import traceback

# -------------------- Gemini Setup --------------------
import google.generativeai as genai
# Load environment variables from .env (project root) before we call any os.getenv
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # try one level up (in case the backend is in a subfolder)
    parent_env = os.path.join(BASE_DIR, '..', '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)

# Configure Gemini/OpenAI-like client using API_KEY from environment
genai.configure(api_key=os.getenv("API_KEY"))

def get_valid_model():
    for m in genai.list_models():
        name = getattr(m, "name", None)
        methods = getattr(m, "supported_generation_methods", [])
        if methods and "generateContent" in methods:
            return name
    raise RuntimeError("No valid model found that supports generateContent!")

MODEL_NAME = get_valid_model()

# -------------------- Flask Config --------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key:
    # fallback for local development; warn because tokens won't survive restarts
    fallback_key = 'dev-secret-change-me'
    app.secret_key = fallback_key
    print("WARNING: SECRET_KEY not set. Using development fallback secret. Set SECRET_KEY in .env for production.")
CORS(app, supports_credentials=True)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

fs = gridfs.GridFS(mongo.db)
users_collection = mongo.db.users

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL")
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# -------------------- Forms --------------------
class RegisterForm(FlaskForm):
    full_name = StringField(validators=[InputRequired(), Length(min=2, max=50)])
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField(validators=[InputRequired(), Email()])
    phone = StringField(validators=[InputRequired(), Length(min=10, max=15)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        if users_collection.find_one({"username": username.data}):
            raise ValidationError("That username already exists.")
    
    def validate_email(self, email):
        if users_collection.find_one({"email": email.data}):
            raise ValidationError("That email is already registered.")

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Login")

class ForgotPasswordForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    submit = SubmitField("Send Reset Link")

class ResetPasswordForm(FlaskForm):
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")

# -------------------- User Loader --------------------
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict["_id"])
        self.email = user_dict["email"]
        self.full_name = user_dict.get("full_name", "")
        self.username = user_dict.get("username", "")

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(user)
    return None

# -------------------- Helper Functions --------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_stream):
    reader = PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def optimize_cv_with_gemini(cv_text):
    try:
        prompt = f"""
        I will provide you with a CV. Your task is to:

        1. Rewrite the CV in a professional, ATS-friendly format suitable for automated resume scanners. Use the following sections: 
           - Contact Information
           - Professional Summary
           - Skills (use relevant keywords for job roles)
           - Education
           - Work Experience (include job title, company, location, dates, and achievements in bullet points)
           - Projects (if applicable)
           - Certifications & Awards (if applicable)

        2. Ensure:
           - Proper formatting: clean headings, bullet points, no graphics or tables.
           - ATS keyword optimization: include relevant skills and terminology commonly scanned by ATS systems.
           - Consistent tense and formatting across experiences.
           - Highlight measurable achievements and results where possible.
           - Use simple, clear language.

        3. After rewriting, provide a separate section called "Improvement Suggestions" listing actionable tips to further enhance the CV, such as skills to add, formatting fixes, or sections to expand.

        CV Content:
        {cv_text}
        """
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt])
        content = response.text.strip() if hasattr(response, "text") and response.text else "No response"
        if "Improvement Suggestions:" in content:
            parts = content.split("Improvement Suggestions:")
            optimized_cv = parts[0].strip()
            suggestions = parts[1].strip()
        else:
            optimized_cv = content
            suggestions = "No suggestions provided."
        return optimized_cv, suggestions
    except Exception as e:
        return f"[ERROR] {str(e)}", "Check logs or try again."

def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Helvetica", size=12)
        text = text.encode("latin-1", "replace").decode("latin-1")
    pdf.set_auto_page_break(auto=True, margin=15)
    def get_width(indent=0):
        return pdf.w - pdf.l_margin - pdf.r_margin - indent
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
        if line.lower().startswith(("education", "experience", "skills", "projects", "contact")):
            pdf.set_font(pdf.font_family, "B", 14)
            pdf.cell(0, 10, line, ln=True)
            pdf.set_font(pdf.font_family, size=12)
        elif line.startswith(("-", "*")) or line[0:2].isdigit():
            indent = 10
            pdf.cell(indent)
            bullet = "•" if pdf.font_family == "DejaVu" else "-"
            safe_text = line.lstrip("-*0123456789. ")
            pdf.multi_cell(get_width(indent), 8, f"{bullet} {safe_text}")
        else:
            pdf.multi_cell(get_width(), 8, line)
    # Use 'S' to get PDF as string and encode to bytes (avoid passing BytesIO to FPDF.output)
    pdf_str = pdf.output(dest='S')
    pdf_data = pdf_str.encode('latin-1')
    pdf_bytes = io.BytesIO(pdf_data)
    pdf_bytes.seek(0)
    return pdf_bytes

# -------------------- Home Route --------------------
@app.route('/')
def home():
    return jsonify({"message": "API is running"})


# -------------------- Auth Routes --------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    form = RegisterForm(data=data)
    if form.validate():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        users_collection.insert_one({
            "full_name": form.full_name.data,
            "username": form.username.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "password": hashed_pw
        })
        return jsonify({"success": True, "message": "Registration successful! Please login."})
    return jsonify({"success": False, "errors": form.errors})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    form = LoginForm(data=data)
    if form.validate():
        user = users_collection.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            login_user(User(user))
            return jsonify({
                "success": True,
                "message": "Login successful!",
                "user": {"id": str(user["_id"]), "full_name": user["full_name"], "email": user["email"]}
            })
        return jsonify({"success": False, "message": "Invalid email or password."}), 401
    return jsonify({"success": False, "errors": form.errors})


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})


# -------------------- Forgot & Reset Password --------------------
@app.route('/forgot-password', methods=['POST'])
@app.route('/forgot_password', methods=['POST'])
@app.route('/api/forgot-password', methods=['POST'])
@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        form = ForgotPasswordForm(data=data)

        if form.validate():
            user = users_collection.find_one({"email": form.email.data})
            if not user:
                return jsonify({"success": False, "message": "No account found with that email."}), 404

            token = serializer.dumps(user["email"], salt="password-reset-salt")
            # Build reset URL safely: if frontend_url already contains the reset path, append token only
            frontend_base = data.get('frontend_url', 'http://localhost:5173') or 'http://localhost:5173'
            frontend_base = frontend_base.rstrip('/')
            if frontend_base.endswith('/reset-password') or frontend_base.endswith('/reset_password'):
                reset_url = f"{frontend_base}/{token}"
            else:
                reset_url = f"{frontend_base}/reset-password/{token}"

            msg = Message("Password Reset Request", recipients=[user["email"]])
            msg.body = f"Click the link to reset your password:\n\n{reset_url}\n\nThis link expires in 1 hour."
            try:
                mail.send(msg)
                return jsonify({"success": True, "message": "Password reset link sent to your email."})
            except Exception:
                # If mail fails (common in local dev), return the reset link to the client for testing
                traceback.print_exc()
                return jsonify({"success": True, "message": "Mail send failed; returning reset link for dev/testing.", "reset_link": reset_url})
        else:
            return jsonify({"success": False, "errors": form.errors})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/reset_password/<token>', methods=['POST'])
@app.route('/reset-password/<token>', methods=['POST'])
@app.route('/api/reset_password/<token>', methods=['POST'])
@app.route('/api/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
        data = request.json
        form = ResetPasswordForm(data=data)

        if form.validate():
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            users_collection.update_one({"email": email}, {"$set": {"password": hashed_pw}})
            return jsonify({"success": True, "message": "Password reset successful!"})
        else:
            return jsonify({"success": False, "errors": form.errors})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 400


# --- Email Test Route ---
@app.route('/test_mail')
def test_mail():
    try:
        msg = Message("Flask-Mail Test", recipients=[os.getenv("MAIL_USERNAME")])
        msg.body = "✅ Flask-Mail is configured properly!"
        mail.send(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        traceback.print_exc()
        return f"❌ Error: {e}"

# -------------------- Dashboard & CV --------------------
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    optimized_cv, suggestions, latest_file_id = None, None, None

    if request.method == 'POST':
        if 'cv_file' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        file = request.files['cv_file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            cv_text = extract_text_from_pdf(file) if file.filename.lower().endswith('.pdf') else file.read().decode('utf-8', errors='ignore')
            optimized_cv, suggestions = optimize_cv_with_gemini(cv_text)
            pdf_bytes = generate_pdf(optimized_cv)
            file_id = fs.put(pdf_bytes, filename=f"ATS_{filename}", content_type="application/pdf", user_id=str(current_user.id))
            latest_file_id = str(file_id)
            return jsonify({
                "success": True,
                "message": "CV uploaded and optimized successfully!",
                "optimized_cv": optimized_cv,
                "suggestions": suggestions,
                "file_id": latest_file_id
            })
        return jsonify({"success": False, "message": "Invalid file type."}), 400

    # GET user files
    user_files = [{"id": str(f._id), "filename": f.filename} for f in fs.find({"user_id": str(current_user.id)})]

    return jsonify({
        "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email},
        "user_files": user_files,
        "optimized_cv": optimized_cv,
        "suggestions": suggestions,
        "latest_file_id": latest_file_id
    })


@app.route('/download/<file_id>', methods=['GET'])
@login_required
def download(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(file_obj.read()),
                         download_name=file_obj.filename,
                         mimetype=file_obj.content_type,
                         as_attachment=True)
    except:
        return jsonify({"success": False, "message": "File not found"}), 404


@app.route('/delete_cv/<file_id>', methods=['DELETE'])
@login_required
def delete_cv(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        if str(file_obj.user_id) != current_user.id:
            return jsonify({"success": False, "message": "Not authorized"}), 403
        fs.delete(ObjectId(file_id))
        return jsonify({"success": True, "message": "CV deleted successfully"})
    except:
        return jsonify({"success": False, "message": "File not found"}), 404


# -------------------- API Routes for React --------------------
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user_id = users_collection.insert_one({
        "full_name": data["full_name"],
        "username": data["username"],
        "email": data["email"],
        "phone": data["phone"],
        "password": hashed_pw
    }).inserted_id

    # ✅ Added success message
    return jsonify({
        "success": True,
        "message": "Registration successful! Please log in.",
        "user": {
            "id": str(user_id),
            "full_name": data["full_name"],
            "email": data["email"]
        }
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        login_user(User(user))
        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": {
                "id": str(user["_id"]),
                "full_name": user["full_name"],
                "email": user["email"]
            }
        })
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/api/current-user')
def api_current_user():
    if current_user.is_authenticated:
        return jsonify({"user": {"id": current_user.id, "full_name": current_user.full_name, "email": current_user.email}})
    return jsonify({"user": None})

@app.route('/api/upload-cv', methods=['POST'])
@login_required
def api_upload_cv():
    if 'cv_file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['cv_file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        file_bytes = file.read()
        cv_text = extract_text_from_any(file_bytes, file.filename)

        job_domain = request.form.get('job_domain') or request.form.get('domain') or request.form.get('target_domain')
        result = optimize_cv(cv_text, job_domain=job_domain, use_ai=True)

        if not isinstance(result, dict):
            current_app.logger.warning('optimize_cv returned non-dict result; using safe defaults')
            result = {}

        optimized_cv = result.get('optimized_text') or result.get('optimized_cv') or cv_text
        optimized_ats_cv = result.get('optimized_ats_cv') or optimized_cv
        template_data = result.get('template_data') or {}
        suggestions = result.get('suggestions') or []

        grouped = {}
        try:
            if isinstance(suggestions, dict):
                grouped = suggestions
            else:
                for s in suggestions:
                    if isinstance(s, dict):
                        cat = s.get('category', 'general')
                        grouped.setdefault(cat, []).append(s.get('message'))
                    else:
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
        extracted_text = result.get('extracted_text') or cv_text
        structured_payload = structured_cv if isinstance(structured_cv, dict) else {}

        try:
            pdf_bytes = generate_pdf(optimized_ats_cv)
        except Exception as e:
            current_app.logger.warning("Error generating PDF, returning fallback text version: %s", e)
            pdf_bytes = generate_pdf(cv_text)

        file_id = fs.put(pdf_bytes.read(), filename=f"ATS_{filename}", content_type="application/pdf", user_id=str(current_user.id))

        return jsonify({
            "success": True,
            "message": "CV uploaded and optimized",
            "file_id": str(file_id),
            "optimized_text": optimized_ats_cv,
            "optimized_cv": optimized_ats_cv,
            "optimized_ats_cv": optimized_ats_cv,
            "extracted": result.get('extracted') or template_data,
            "extracted_text": extracted_text,
            "sections": sections,
            "ordered_sections": ordered_sections,
            "structured_sections": structured_sections,
            "structured_cv": structured_payload,
            "template_data": template_data,
            "suggestions": suggestions,
            "grouped_suggestions": grouped,
            "ats_score": ats_score,
            "recommended_keywords": recommended_keywords,
            "found_keywords": found_keywords,
        })
    return jsonify({"success": False, "message": "Invalid file type"}), 400

@app.route('/api/download/<file_id>')
@login_required
def api_download(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(file_obj.read()), download_name=file_obj.filename, mimetype=file_obj.content_type, as_attachment=True)
    except:
        return jsonify({"success": False, "message": "File not found"}), 404

@app.route('/api/delete-cv/<file_id>', methods=['DELETE'])
@login_required
def api_delete_cv(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        if str(file_obj.user_id) != current_user.id:
            return jsonify({"success": False, "message": "Not authorized"}), 403
        fs.delete(ObjectId(file_id))
        return jsonify({"success": True, "message": "CV deleted successfully"})
    except:
        return jsonify({"success": False, "message": "File not found"}), 404

@app.route('/api/user-files')
@login_required
def api_user_files():
    user_files = list(fs.find({"user_id": current_user.id}))
    files = [{"_id": str(f._id), "filename": f.filename} for f in user_files]
    return jsonify({"files": files})


# -------------------- Chatbot endpoints --------------------
@app.route('/api/chatbot/upload', methods=['POST'])
@login_required
def api_chatbot_upload():
    # Accept multiple files under form key 'files'
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No files provided."}), 400
    files = request.files.getlist('files')
    saved = []
    cv_texts_coll = mongo.db.cv_texts
    try:
        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f"{current_user.id}_{f.filename}")
                # Read and extract text
                if f.filename.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(f)
                    f.seek(0)
                else:
                    # for doc/docx we store raw bytes as fallback
                    data = f.read()
                    try:
                        text = data.decode('utf-8', errors='ignore')
                    except Exception:
                        text = ''
                    f.seek(0)

                # store file into GridFS
                file_id = fs.put(f.read(), filename=filename, content_type='application/octet-stream', user_id=str(current_user.id))
                # persist extracted text and metadata
                cv_texts_coll.insert_one({
                    'user_id': str(current_user.id),
                    'file_id': str(file_id),
                    'filename': filename,
                    'text': text,
                })
                saved.append({"file_id": str(file_id), "filename": filename})
        if not saved:
            return jsonify({"success": False, "message": "No valid files uploaded."}), 400
        return jsonify({"success": True, "message": "Files uploaded and processed.", "files": saved})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing files: {str(e)}"}), 500


@app.route('/api/chatbot/ask', methods=['POST'])
@login_required
def api_chatbot_ask():
    data = request.json or {}
    question = data.get('question') or data.get('q')
    if not question:
        return jsonify({"success": False, "message": "No question provided."}), 400

    # Aggregate user's CV texts
    cv_texts_coll = mongo.db.cv_texts
    cursor = cv_texts_coll.find({'user_id': str(current_user.id)})
    combined = []
    for doc in cursor:
        t = doc.get('text') or ''
        if t:
            combined.append(t)
    if not combined:
        return jsonify({"success": False, "message": "No CV uploaded for this user."}), 404

    # Prepare prompt for the model
    cv_context = '\n\n'.join(combined)
    # truncate to a safe length to avoid very long prompts
    if len(cv_context) > 20000:
        cv_context = cv_context[-20000:]

    prompt = f"You are a helpful assistant that answers questions based ONLY on the user's CV information provided below. If the answer is not present, reply saying you don't have enough information and ask for clarification.\n\nUser CV Data:\n{cv_context}\n\nQuestion: {question}\n\nAnswer succinctly and reference the CV where applicable." 

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt])
        answer = response.text.strip() if hasattr(response, 'text') and response.text else 'No response from model.'
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        return jsonify({"success": False, "message": f"Model error: {str(e)}"}), 500

# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(debug=True)
