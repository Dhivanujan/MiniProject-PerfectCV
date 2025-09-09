from flask import Flask, render_template, url_for, redirect, flash, request, send_file
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
import io
from fpdf import FPDF
from PyPDF2 import PdfReader
import os

# OpenAI imports
from openai import OpenAI, RateLimitError

# -------------------- Configuration --------------------
app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB Atlas connection
app.config["MONGO_URI"] = "mongodb+srv://Dhivanujan:TFC3EDgFAwz3BNuO@cluster0.kml3jfs.mongodb.net/mydatabase"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# GridFS for file storage
fs = gridfs.GridFS(mongo.db)
users_collection = mongo.db.users

# OpenAI client
client = OpenAI(api_key="OpenAi API key")

# -------------------- Flask-Login --------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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

# -------------------- Flask-Mail --------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ""
app.config['MAIL_PASSWORD'] = ""
app.config['MAIL_DEFAULT_SENDER'] = "your_email@gmail.com"

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

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

# -------------------- Helper Functions --------------------
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

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

def optimize_cv_with_gpt(cv_text):
    try:
        prompt = f"""
        Rewrite this CV to make it ATS-friendly. Keep all details, improve formatting and keyword usage,
        and return the result as plain text with sections: Education, Experience, Skills, Projects, Contact.
        CV Content:
        {cv_text}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that optimizes CVs."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        return "⚠️ Error: You have exceeded your current OpenAI quota."
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

def clean_text(text):
    return text.replace("⚠️", "[ERROR]").encode("latin-1", "replace").decode("latin-1")

def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()

    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        text = clean_text(text)
        pdf.set_font("Helvetica", size=12)

    pdf.set_auto_page_break(auto=True, margin=15)

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
            pdf.cell(10)
            pdf.multi_cell(0, 8, f"• {line.lstrip('-*0123456789. ')}")
        else:
            pdf.multi_cell(0, 8, line)

    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes, "F")
    pdf_bytes.seek(0)
    return pdf_bytes

# -------------------- Routes --------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        users_collection.insert_one({
            "full_name": form.full_name.data,
            "username": form.username.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "password": hashed_pw
        })
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users_collection.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            login_user(User(user))
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = users_collection.find_one({"email": form.email.data})
        if user:
            token = serializer.dumps(user["email"], salt="password-reset-salt")
            reset_url = url_for('reset_password', token=token, _external=True)

            msg = Message("Password Reset Request", recipients=[user["email"]])
            msg.body = f"Click the link to reset your password: {reset_url}\n\nThis link will expire in 1 hour."
            mail.send(msg)

            flash("Password reset link sent to your email.", "success")
        else:
            flash("No account found with that email.", "danger")
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except:
        flash("The reset link is invalid or expired.", "danger")
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_pw}})
        flash("Password reset successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        file = request.files['cv_file']
        if file.filename == '':
            flash("No file selected", "danger")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{file.filename}")

            if file.filename.lower().endswith('.pdf'):
                cv_text = extract_text_from_pdf(file)
            else:
                cv_text = file.read().decode('utf-8', errors='ignore')

            optimized_cv = optimize_cv_with_gpt(cv_text)
            pdf_bytes = generate_pdf(optimized_cv)
            fs.put(pdf_bytes, filename=f"ATS_{filename}", content_type="application/pdf", user_id=current_user.id)
            flash("CV uploaded and optimized successfully!", "success")
            return redirect(request.url)
        else:
            flash("Invalid file type. Only PDF, DOC, DOCX allowed.", "danger")
            return redirect(request.url)

    user_files = fs.find({"user_id": current_user.id})
    return render_template('dashboard.html', user=current_user, user_files=user_files)

@app.route('/download/<file_id>')
@login_required
def download(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(file_obj.read()),
                         download_name=file_obj.filename,
                         mimetype=file_obj.content_type,
                         as_attachment=True)
    except:
        flash("File not found.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/delete_cv/<file_id>')
@login_required
def delete_cv(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        if str(file_obj.user_id) != current_user.id:
            flash("You are not authorized to delete this file.", "danger")
            return redirect(url_for('dashboard'))
        fs.delete(ObjectId(file_id))
        flash("CV deleted successfully!", "success")
    except:
        flash("File not found.", "danger")
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
