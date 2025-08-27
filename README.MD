# Smart ATS 🚀

An AI-powered **ATS Resume Analyzer & Optimizer** built with [Streamlit](https://streamlit.io/) and [Google Gemini](https://ai.google/).  
This tool helps job seekers improve their resumes by analyzing them against job descriptions, highlighting missing keywords, and rewriting resumes for **maximum ATS compatibility**.

---

## ✨ Features
- 📂 **Upload Resume (PDF)** – Extracts text (with OCR fallback for scanned resumes).  
- 📄 **Paste Job Description** – The JD is matched against the resume.  
- 🔎 **ATS Evaluation** –  
  - JD Match % (with progress bar)  
  - Missing keywords  
  - Profile summary  
- ✨ **Resume Optimization** –  
  - Rewrites your resume with **ATS-friendly keywords & metrics-driven achievements**  
  - Download as **TXT** or **PDF**  
- 🖼️ **OCR Fallback** – Handles scanned resumes using `pytesseract`.  

---

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/) – Web UI  
- [Google Generative AI (Gemini)](https://ai.google/) – Resume analysis & rewriting  
- [PyPDF2](https://pypi.org/project/PyPDF2/) – PDF text extraction  
- [pdf2image](https://pypi.org/project/pdf2image/) – PDF to image conversion (for OCR)  
- [pytesseract](https://pypi.org/project/pytesseract/) – OCR text extraction  
- [reportlab](https://pypi.org/project/reportlab/) – Resume PDF generation  
- [dotenv](https://pypi.org/project/python-dotenv/) – Environment variable handling  

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/mdsohailkhan/Smart_ATS.git
cd smart-ats

2️⃣ Setup Environment (Choose one)
Using Conda
conda create -p venv python=3.10 -y
conda activate venv/
pip install -r requirements.txt

🔑 Environment Variables

Create a .env file in the root directory with your Gemini API key:

GOOGLE_API_KEY=your_google_api_key_here


🚀 Run the App
streamlit run app.py


This will launch the app in your browser at:

http://localhost:8501

📂 Project Structure
smart-ats/
│-- app.py              # Main Streamlit app
│-- requirements.txt    # Python dependencies
│-- README.md           # Project documentation
│-- .env                # Environment variables (not committed)

📌 Requirements

requirements.txt:

streamlit
google-generativeai
python-dotenv
PyPDF2
reportlab
pdf2image
pytesseract
Pillow

🎯 Future Improvements

✅ Cover letter generator based on JD.

✅ Multi-resume comparison.

✅ Keyword density visualization.

✅ LinkedIn import for resume generation.

📜 License

This project is licensed under the MIT License.

💡 Built with ❤️ using Streamlit + Gemini


