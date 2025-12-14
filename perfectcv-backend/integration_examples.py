"""
Example Frontend Integration
Demonstrates how to integrate the CV generation API with a frontend
"""

# ============================================================================
# REACT EXAMPLE
# ============================================================================

react_example = '''
// components/CVUploader.jsx
import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/cv';

export default function CVUploader() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cvData, setCvData] = useState(null);
  const [atsScore, setAtsScore] = useState(null);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.type === 'application/pdf' || 
        selectedFile.name.endsWith('.docx'))) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a PDF or DOCX file');
    }
  };

  // Extract CV data (preview before generation)
  const handleExtract = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE_URL}/extract-cv`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setCvData(response.data.data);
      setAtsScore(response.data.ats_score);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to extract CV data');
    } finally {
      setLoading(false);
    }
  };

  // Generate improved PDF
  const handleGeneratePDF = async (improve = true) => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_BASE_URL}/generate-cv?improve=${improve}`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          responseType: 'blob'
        }
      );

      // Download the generated PDF
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `improved_cv_${Date.now()}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);

      alert('CV generated successfully!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate CV');
    } finally {
      setLoading(false);
    }
  };

  // Improve existing CV data
  const handleImprove = async () => {
    if (!cvData) {
      setError('Please extract CV data first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/improve-cv`, cvData);
      setCvData(response.data.data);
      setAtsScore(response.data.ats_score);
      alert('CV data improved successfully!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to improve CV');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cv-uploader">
      <h2>CV Generator</h2>
      
      {/* File Upload */}
      <div className="upload-section">
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileChange}
          disabled={loading}
        />
        {file && <p>Selected: {file.name}</p>}
      </div>

      {/* Error Message */}
      {error && <div className="error">{error}</div>}

      {/* Action Buttons */}
      <div className="actions">
        <button onClick={handleExtract} disabled={!file || loading}>
          {loading ? 'Processing...' : 'Extract Data'}
        </button>
        <button onClick={() => handleGeneratePDF(false)} disabled={!file || loading}>
          Generate PDF (No Improvement)
        </button>
        <button onClick={() => handleGeneratePDF(true)} disabled={!file || loading}>
          Generate Improved PDF
        </button>
      </div>

      {/* CV Data Preview */}
      {cvData && (
        <div className="cv-preview">
          <h3>Extracted Data</h3>
          <div className="cv-field">
            <strong>Name:</strong> {cvData.name}
          </div>
          <div className="cv-field">
            <strong>Email:</strong> {cvData.email}
          </div>
          <div className="cv-field">
            <strong>Phone:</strong> {cvData.phone}
          </div>
          <div className="cv-field">
            <strong>Skills:</strong> {cvData.skills.join(', ')}
          </div>
          <div className="cv-field">
            <strong>Experience:</strong> {cvData.experience.length} positions
          </div>
          
          <button onClick={handleImprove} disabled={loading}>
            Improve with AI
          </button>
        </div>
      )}

      {/* ATS Score */}
      {atsScore && (
        <div className="ats-score">
          <h3>ATS Score: {atsScore.percentage}%</h3>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${atsScore.percentage}%` }}
            />
          </div>
          {atsScore.suggestions.length > 0 && (
            <div className="suggestions">
              <h4>Suggestions:</h4>
              <ul>
                {atsScore.suggestions.map((suggestion, idx) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
'''

# ============================================================================
# VANILLA JAVASCRIPT EXAMPLE
# ============================================================================

vanilla_js_example = '''
// vanilla-js-example.js
const API_BASE_URL = 'http://localhost:8000/api/cv';

// Upload and generate CV
async function uploadAndGenerateCV() {
  const fileInput = document.getElementById('cvFile');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Please select a file');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    // Show loading
    document.getElementById('loading').style.display = 'block';
    
    // Generate CV
    const response = await fetch(`${API_BASE_URL}/generate-cv?improve=true`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate CV');
    }
    
    // Download PDF
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'improved_cv.pdf';
    a.click();
    URL.revokeObjectURL(url);
    
    alert('CV generated successfully!');
  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    document.getElementById('loading').style.display = 'none';
  }
}

// Extract CV data
async function extractCVData() {
  const fileInput = document.getElementById('cvFile');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Please select a file');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    document.getElementById('loading').style.display = 'block';
    
    const response = await fetch(`${API_BASE_URL}/extract-cv`, {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    // Display results
    displayCVData(result.data);
    displayATSScore(result.ats_score);
  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    document.getElementById('loading').style.display = 'none';
  }
}

function displayCVData(data) {
  const container = document.getElementById('cvData');
  container.innerHTML = `
    <h3>Extracted CV Data</h3>
    <p><strong>Name:</strong> ${data.name}</p>
    <p><strong>Email:</strong> ${data.email}</p>
    <p><strong>Phone:</strong> ${data.phone}</p>
    <p><strong>Skills:</strong> ${data.skills.join(', ')}</p>
    <p><strong>Experience:</strong> ${data.experience.length} positions</p>
  `;
}

function displayATSScore(score) {
  const container = document.getElementById('atsScore');
  container.innerHTML = `
    <h3>ATS Score: ${score.percentage}%</h3>
    <div style="width: 100%; background: #eee; border-radius: 5px;">
      <div style="width: ${score.percentage}%; background: #4CAF50; height: 20px; border-radius: 5px;"></div>
    </div>
    ${score.suggestions.length > 0 ? `
      <h4>Suggestions:</h4>
      <ul>
        ${score.suggestions.map(s => `<li>${s}</li>`).join('')}
      </ul>
    ` : ''}
  `;
}
'''

# ============================================================================
# PYTHON CLIENT EXAMPLE
# ============================================================================

python_client_example = '''
# python_client.py
import requests
import json

class CVGeneratorClient:
    """Python client for CV Generation API"""
    
    def __init__(self, base_url='http://localhost:8000/api/cv'):
        self.base_url = base_url
    
    def generate_cv(self, file_path, improve=True, output_path='improved_cv.pdf'):
        """
        Upload CV and generate improved PDF
        
        Args:
            file_path: Path to CV file (PDF or DOCX)
            improve: Whether to improve with AI
            output_path: Where to save the generated PDF
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'improve': improve}
            
            response = requests.post(
                f'{self.base_url}/generate-cv',
                files=files,
                params=params
            )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out:
                out.write(response.content)
            print(f'✓ CV generated: {output_path}')
            return output_path
        else:
            raise Exception(f'Failed to generate CV: {response.text}')
    
    def extract_cv(self, file_path):
        """
        Extract structured data from CV
        
        Args:
            file_path: Path to CV file
            
        Returns:
            dict: CV data and ATS score
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{self.base_url}/extract-cv', files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to extract CV: {response.text}')
    
    def improve_cv(self, cv_data):
        """
        Improve existing CV data with AI
        
        Args:
            cv_data: CV data dictionary
            
        Returns:
            dict: Improved CV data and ATS score
        """
        response = requests.post(
            f'{self.base_url}/improve-cv',
            json=cv_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to improve CV: {response.text}')
    
    def generate_pdf_from_json(self, cv_data, output_path='custom_cv.pdf'):
        """
        Generate PDF from CV data dictionary
        
        Args:
            cv_data: CV data dictionary
            output_path: Where to save the PDF
        """
        response = requests.post(
            f'{self.base_url}/generate-pdf-from-json',
            json=cv_data
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out:
                out.write(response.content)
            print(f'✓ PDF generated: {output_path}')
            return output_path
        else:
            raise Exception(f'Failed to generate PDF: {response.text}')


# Usage Example
if __name__ == '__main__':
    client = CVGeneratorClient()
    
    # Example 1: Direct generation
    print("\\nExample 1: Generate improved CV directly")
    client.generate_cv('sample_resume.pdf', improve=True, output_path='improved.pdf')
    
    # Example 2: Extract, review, then generate
    print("\\nExample 2: Extract and review before generation")
    result = client.extract_cv('sample_resume.pdf')
    
    cv_data = result['data']
    ats_score = result['ats_score']
    
    print(f"Name: {cv_data['name']}")
    print(f"ATS Score: {ats_score['percentage']}%")
    print(f"Skills: {len(cv_data['skills'])}")
    
    # Improve the data
    improved = client.improve_cv(cv_data)
    improved_cv = improved['data']
    improved_score = improved['ats_score']
    
    print(f"Improved Score: {improved_score['percentage']}%")
    
    # Generate PDF from improved data
    client.generate_pdf_from_json(improved_cv, output_path='final_cv.pdf')
'''

# ============================================================================
# HTML EXAMPLE PAGE
# ============================================================================

html_example = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .container {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 30px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-section {
            margin: 20px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        input[type="file"] {
            width: 100%;
            padding: 10px;
        }
        .buttons {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        button {
            flex: 1;
            padding: 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #45a049;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .results {
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 5px;
        }
        .ats-score {
            margin: 20px 0;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #eee;
            border-radius: 15px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(to right, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI-Powered CV Generator</h1>
        
        <div class="upload-section">
            <h3>Upload Your CV</h3>
            <input type="file" id="cvFile" accept=".pdf,.docx">
        </div>
        
        <div class="buttons">
            <button onclick="extractCVData()">Extract Data</button>
            <button onclick="generateCV(false)">Generate PDF</button>
            <button onclick="generateCV(true)">Generate Improved PDF</button>
        </div>
        
        <div id="loading" class="loading">
            <p>Processing... Please wait...</p>
        </div>
        
        <div id="results" class="results" style="display: none;">
            <div id="cvData"></div>
            <div id="atsScore"></div>
        </div>
    </div>
    
    <script>
        const API_BASE_URL = 'http://localhost:8000/api/cv';
        
        async function generateCV(improve) {
            const fileInput = document.getElementById('cvFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                document.getElementById('loading').style.display = 'block';
                
                const response = await fetch(
                    `${API_BASE_URL}/generate-cv?improve=${improve}`,
                    { method: 'POST', body: formData }
                );
                
                if (!response.ok) throw new Error('Generation failed');
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `cv_${improve ? 'improved_' : ''}${Date.now()}.pdf`;
                a.click();
                URL.revokeObjectURL(url);
                
                alert('✓ CV generated successfully!');
            } catch (error) {
                alert('✗ Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        async function extractCVData() {
            const fileInput = document.getElementById('cvFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                document.getElementById('loading').style.display = 'block';
                
                const response = await fetch(`${API_BASE_URL}/extract-cv`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                displayResults(result);
            } catch (error) {
                alert('✗ Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayResults(result) {
            const { data, ats_score } = result;
            
            document.getElementById('cvData').innerHTML = `
                <h3>📄 Extracted CV Data</h3>
                <p><strong>Name:</strong> ${data.name}</p>
                <p><strong>Email:</strong> ${data.email}</p>
                <p><strong>Phone:</strong> ${data.phone}</p>
                <p><strong>Skills:</strong> ${data.skills.join(', ')}</p>
                <p><strong>Experience:</strong> ${data.experience.length} positions</p>
                <p><strong>Education:</strong> ${data.education.length} entries</p>
            `;
            
            document.getElementById('atsScore').innerHTML = `
                <div class="ats-score">
                    <h3>📊 ATS Score: ${ats_score.percentage}%</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${ats_score.percentage}%"></div>
                    </div>
                    ${ats_score.suggestions.length > 0 ? `
                        <h4>💡 Suggestions:</h4>
                        <ul>
                            ${ats_score.suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
            
            document.getElementById('results').style.display = 'block';
        }
    </script>
</body>
</html>
'''

# Print examples
if __name__ == "__main__":
    print("="*70)
    print("FRONTEND INTEGRATION EXAMPLES")
    print("="*70)
    print("\n1. REACT EXAMPLE")
    print("-"*70)
    print(react_example)
    print("\n2. VANILLA JAVASCRIPT EXAMPLE")
    print("-"*70)
    print(vanilla_js_example)
    print("\n3. PYTHON CLIENT EXAMPLE")
    print("-"*70)
    print(python_client_example)
    print("\n4. HTML EXAMPLE PAGE")
    print("-"*70)
    print(html_example)
