# PerfectCV - AI-Powered Resume Builder

![PerfectCV Logo](static/Logo.png)

PerfectCV is a modern, AI-powered resume builder that helps users create professional, ATS-friendly resumes quickly and efficiently. The application features a Flask backend with MongoDB integration and a React frontend for a seamless user experience.

## ✨ Features

- **AI-Powered Suggestions**: Get smart recommendations to improve your CV content and format
- **Professional Templates**: Choose from a variety of modern, recruiter-friendly templates  
- **PDF Export**: Download your CV in professional PDF format
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Real-time Editing**: Make changes and see updates instantly

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **MongoDB Atlas** - Cloud database
- **PyMongo** - MongoDB driver for Python
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation
- **OpenAI API** - AI-powered content suggestions
- **GridFS** - File storage system

### Frontend
- **React** - Modern JavaScript library
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

## 📋 Prerequisites

Before running this project, make sure you have the following installed:

- **Python 3.8+** 
- **Node.js 16+** and **npm**
- **Git**
- **MongoDB Atlas Account** (for database)
- **OpenAI API Key** (for AI features)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Dhivanujan/MiniProject-PerfectCV.git
cd MiniProject-PerfectCV
```

### 2. Backend Setup (Flask)

#### Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install flask flask-pymongo flask-wtf flask-login flask-bcrypt flask-mail
pip install openai PyPDF2 fpdf2 itsdangerous werkzeug wtforms
```

#### Configure Environment Variables
1. Open `app.py` and update the following configurations:
   ```python
   # MongoDB Atlas connection
   app.config["MONGO_URI"] = "your_mongodb_connection_string"
   
   # OpenAI API Key
   client = OpenAI(api_key="your_openai_api_key")
   
   # Flask Secret Key
   app.secret_key = "your_secret_key"
   ```

### 3. Frontend Setup (React)

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Node Dependencies
```bash
npm install
```

#### Copy Static Assets
```bash
# From the main project directory
# On Windows:
xcopy static frontend\public\static\ /E /I

# On macOS/Linux:
cp -r static/* frontend/public/static/
```

## 🏃‍♂️ Running the Application

### Option 1: Development Mode (Recommended)

#### 1. Start Flask Backend
```bash
# From the main project directory
# Make sure virtual environment is activated
python app.py
```
The Flask backend will run on `http://localhost:5000`

#### 2. Start React Frontend
```bash
# From the frontend directory
npm start
```
The React frontend will run on `http://localhost:3000`

### Option 2: Production Build

#### Build React for Production
```bash
cd frontend
npm run build
```

#### Serve React Build with Flask
Update your Flask `app.py` to serve the React build files.

## 📱 Usage

1. **Access the Application**: Open `http://localhost:3000` in your browser
2. **Register/Login**: Create an account or login to existing account
3. **Create CV**: Use the dashboard to start building your resume
4. **AI Assistance**: Get AI-powered suggestions for content improvement
5. **Export**: Download your finished CV as a PDF

## 📁 Project Structure

```
MiniProject-PerfectCV/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── context/            # React context (Auth)
│   │   └── App.js              # Main React app
│   ├── public/                 # Static files
│   └── package.json            # Node dependencies
├── static/                     # Static assets (images)
│   ├── CV.png
│   ├── Hero.png
│   └── Logo.png
├── venv/                       # Python virtual environment
├── app.py                      # Flask backend application
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

## 🔧 Configuration

### MongoDB Setup
1. Create a MongoDB Atlas account at https://www.mongodb.com/atlas
2. Create a new cluster and database
3. Get your connection string and update `MONGO_URI` in `app.py`

### OpenAI Setup
1. Get an API key from https://platform.openai.com/
2. Update the `client` configuration in `app.py`

### Email Configuration (Optional)
For password reset functionality, configure email settings in `app.py`:
```python
app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email'
app.config['MAIL_PASSWORD'] = 'your_password'
```

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure virtual environment is activated and all dependencies are installed
2. **MongoDB Connection Error**: Verify your MongoDB Atlas connection string and network access
3. **CORS Issues**: Ensure frontend and backend are running on different ports
4. **Static Files Not Loading**: Make sure static assets are copied to `frontend/public/static/`

### Port Conflicts
- Flask Backend: `http://localhost:5000`
- React Frontend: `http://localhost:3000`

If ports are in use, you can change them:
- Flask: Modify `app.run(port=5000)` in `app.py`
- React: Set `PORT=3001` in frontend `.env` file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Dhivanujan** - Initial work - [GitHub Profile](https://github.com/Dhivanujan)

## 🙏 Acknowledgments

- OpenAI for providing AI capabilities
- MongoDB Atlas for cloud database services
- React and Flask communities for excellent documentation
- Tailwind CSS for the styling framework

## 📞 Support

If you have any questions or issues, please:
1. Check the troubleshooting section above
2. Search existing issues in the GitHub repository
3. Create a new issue with detailed description

---

**Made with ❤️ by the PerfectCV Team**
