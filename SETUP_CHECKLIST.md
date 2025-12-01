# ✅ Setup Checklist - AI-Enhanced CV Extraction

Use this checklist to set up the new AI-powered CV extraction features.

## 📦 Installation Steps

### Step 1: Install Python Dependencies
```bash
cd perfectcv-backend
pip install -r requirements.txt
```

Expected packages to install:
- ✅ openai (already in requirements)
- ✅ pytesseract (NEW - for OCR)
- ✅ pillow (NEW - for image processing)
- ✅ pdf2image (NEW - for PDF to image conversion)

### Step 2: Install System Dependencies (Optional - for OCR)

#### For Windows:
- [ ] Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- [ ] Add Tesseract to PATH environment variable
- [ ] Download [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- [ ] Add Poppler's `bin` folder to PATH
- [ ] Restart terminal/command prompt

#### For Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

#### For macOS:
```bash
brew install tesseract
brew install poppler
```

### Step 3: Get OpenAI API Key

- [ ] Visit https://platform.openai.com/api-keys
- [ ] Sign in or create an account
- [ ] Click "Create new secret key"
- [ ] Name it "PerfectCV" or similar
- [ ] Copy the API key (starts with `sk-...`)
- [ ] **Important**: Save the key securely - you can't view it again!

### Step 4: Configure API Key

- [ ] Open `perfectcv-backend/.env`
- [ ] Find the line: `OPENAI_API_KEY="your_openai_api_key_here"`
- [ ] Replace with your actual key: `OPENAI_API_KEY="sk-your-actual-key"`
- [ ] Save the file
- [ ] **DO NOT commit .env to git!**

### Step 5: Verify Setup

```bash
cd perfectcv-backend
python verify_setup.py
```

Expected output:
```
✓ openai is installed
✓ pytesseract is installed
✓ pillow is installed
✓ pdf2image is installed
✓ PyMuPDF is installed
✓ pdfplumber is installed
✓ google-generativeai is installed
✓ OPENAI_API_KEY is configured
✓ GOOGLE_API_KEY is configured
```

### Step 6: Test with Sample CV

- [ ] Start the backend server
- [ ] Upload a test CV (PDF or DOCX)
- [ ] Check if AI parsing works
- [ ] Verify structured data is returned
- [ ] Test with a scanned PDF (if OCR installed)

## 🎯 Feature Testing Checklist

### Basic CV Upload
- [ ] Upload PDF CV → Text extracted correctly
- [ ] Upload DOCX CV → Text extracted correctly
- [ ] Check console for "Successfully optimized CV with OpenAI GPT-4"

### AI Features
- [ ] Contact information extracted correctly (name, email, phone, location)
- [ ] Skills categorized (technical, soft, tools, frameworks)
- [ ] Work experience parsed with dates, company, achievements
- [ ] Education section extracted properly
- [ ] Projects identified and structured
- [ ] ATS score calculated

### OCR Testing (if installed)
- [ ] Upload scanned/image-based PDF
- [ ] Check console for "OCR processing page X/Y"
- [ ] Verify text extracted from scanned document
- [ ] Compare accuracy with regular PDF

### Fallback Testing
- [ ] Remove OPENAI_API_KEY from .env
- [ ] Upload CV → Should fall back to Gemini
- [ ] Remove both API keys → Should fall back to rule-based
- [ ] Verify app still works without AI

## 📊 Monitoring & Optimization

### Track API Usage
- [ ] Visit https://platform.openai.com/usage
- [ ] Monitor GPT-4 token usage
- [ ] Check costs (should be ~$0.01-0.03 per CV)
- [ ] Set up billing alerts if needed

### Performance Optimization
- [ ] Cache parsed CV results in database
- [ ] Only use AI for new/edited CVs
- [ ] Consider using GPT-3.5 for cost savings (less accurate)
- [ ] Implement rate limiting for API calls

## 🔒 Security Checklist

- [ ] .env file is in .gitignore
- [ ] API keys not hardcoded in source files
- [ ] .env.example created (without real keys)
- [ ] API key environment variable loaded correctly
- [ ] Production .env secured on server

## 📚 Documentation Review

- [ ] Read `AI_CV_EXTRACTION_GUIDE.md` for full documentation
- [ ] Review `CV_EXTRACTION_IMPROVEMENTS_SUMMARY.md` for overview
- [ ] Check code comments in `ai_cv_parser.py`
- [ ] Understand fallback mechanism in `cv_utils.py`

## 🐛 Troubleshooting

### Common Issues:

#### "OpenAI API key not configured"
- ✅ Check OPENAI_API_KEY in .env
- ✅ Restart backend server after editing .env
- ✅ Verify .env is in correct directory

#### "OCR not available" warning
- ✅ Install Tesseract OCR
- ✅ Add to PATH environment variable
- ✅ Restart terminal
- ✅ Run `tesseract --version` to verify

#### "Import pytesseract could not be resolved"
- ✅ Run `pip install pytesseract pillow pdf2image`
- ✅ Restart IDE/editor

#### API rate limit errors
- ✅ Check OpenAI usage dashboard
- ✅ Implement request throttling
- ✅ Use caching for parsed CVs

#### Low accuracy results
- ✅ Ensure using GPT-4 (not GPT-3.5)
- ✅ Check CV quality and format
- ✅ Test with different CV samples

## 🎉 Success Criteria

You're ready to go when:

- ✅ All dependencies installed successfully
- ✅ OpenAI API key configured
- ✅ `verify_setup.py` shows all green checkmarks
- ✅ Sample CV upload works and shows structured data
- ✅ Console shows "Successfully optimized CV with OpenAI GPT-4"
- ✅ ATS score and recommendations displayed
- ✅ (Optional) OCR works for scanned PDFs

## 🚀 Next Steps

After successful setup:

1. **Test with Real CVs**
   - Upload various CV formats
   - Compare AI results with rule-based
   - Note accuracy improvements

2. **Fine-tune if Needed**
   - Adjust AI prompts in `ai_cv_parser.py`
   - Modify categorization logic
   - Add custom section detection

3. **Monitor Performance**
   - Track API costs
   - Measure processing time
   - Collect user feedback

4. **Consider Enhancements**
   - Add cover letter generation
   - Implement CV scoring vs job descriptions
   - Create industry-specific templates
   - Add multi-language support

## 📞 Need Help?

If you encounter issues:

1. **Check Documentation**
   - Review `AI_CV_EXTRACTION_GUIDE.md`
   - Read troubleshooting section

2. **Run Diagnostics**
   - Execute `verify_setup.py`
   - Check console logs
   - Review error messages

3. **Test Components**
   - Test PDF extraction separately
   - Test AI parser independently
   - Verify API connectivity

4. **Common Fixes**
   - Restart backend server
   - Clear Python cache (`__pycache__`)
   - Reinstall dependencies
   - Check API key validity

---

## 📝 Notes

- **API Costs**: OpenAI GPT-4 is pay-per-use (~$0.01-0.03 per CV)
- **Privacy**: OpenAI has zero data retention for API calls
- **Fallback**: System always works, even without OpenAI API key
- **OCR**: Optional feature for scanned PDFs only

---

**Last Updated**: December 12, 2025  
**Version**: 2.0  
**Author**: PerfectCV Enhancement Team
