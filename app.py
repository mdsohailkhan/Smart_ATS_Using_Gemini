import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from pdf2image import convert_from_bytes
import pytesseract
import time

# -------------------- Setup --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------------------- Helper Functions --------------------

def get_gemini_response(input_prompt, json_mode=False, retries=3):
    """Call Gemini model to generate content with retry logic"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    for attempt in range(retries):
        try:
            if json_mode:
                response = model.generate_content(
                    input_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
            else:
                response = model.generate_content(input_prompt)

            if response.candidates:
                return response.candidates[0].content.parts[0].text
            return response.text or ""
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)  # wait before retry
            else:
                return f"❌ Error generating response: {str(e)}"

@st.cache_data
def input_pdf_text(uploaded_file):
    """Extract text from uploaded PDF with OCR fallback"""
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        if text.strip():
            return text
    except:
        pass

    # OCR fallback for scanned PDFs
    try:
        images = convert_from_bytes(uploaded_file.read())
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"❌ Error reading PDF (OCR failed): {str(e)}"

def optimize_resume(resume_text, jd):
    """Ask Gemini to rewrite resume to match JD"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    You are a professional resume writer and specialist in ATS optimization. 
    Revise the resume to achieve maximum ATS compatibility (aiming for close to 100%). 
    
    Guidelines:
    1. Impact Framework with Metrics:
    
    Articulate your achievements using the following structure:
    “Accomplished [X] as measured by [Y] metric or percentage by executing [Z].”

    - [X]: What specific result or outcome did you achieve? (e.g., improved revenue, increased efficiency, reduced costs)
    - [Y]: What metric or percentage quantifies the success of your achievement? (e.g., 20% growth, $100K saved, 50% improvement)
    - [Z]: What actions, strategies, or initiatives did you implement to realize this result? (e.g., process overhaul, team collaboration, new technology)

    Example Prompts:
    
    - “Accomplished [X] as measured by [Y] metric or percentage by executing [Z].”
      e.g., Increased sales by 15% as measured by revenue growth by implementing a targeted email marketing campaign.

    - “Accomplished [X] by [Y]% in [Z] time frame by [action].”
      e.g., Reduced customer churn by 30% in 3 months by revamping the onboarding process.





    Job Description:
    {jd}

    Current Resume:
    {resume_text}

    Return the improved resume text only.
    """
    return get_gemini_response(prompt)

def safe_json_parse(response):
    """Safely parse Gemini's response into JSON"""
    try:
        return json.loads(response)
    except:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return {"error": "Failed to parse JSON", "raw": response}
        return {"error": "Invalid response format", "raw": response}

def generate_pdf(text):
    """Generate formatted PDF from text using platypus"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), styles["Normal"]))
            story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------- Prompt Template --------------------

input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer and (AI PM, Cybersecurity, Generative AI). Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.

Resume:
{text}

Job Description:
{jd}

I want the response in JSON:
{{
  "JD Match":"%",
  "MissingKeywords":[],
  "Profile Summary":""
}}
"""

# -------------------- Streamlit UI --------------------

st.title("Smart ATS 🚀")
st.text("Upload your resume and job description to get ATS feedback and optimization")

jd = st.text_area("📄 Paste the Job Description")
uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF)", type="pdf")

# Initialize session state
st.session_state.setdefault("resume_text", None)
st.session_state.setdefault("jd", None)

# -------------------- Evaluate Resume --------------------
if st.button("🔎 Evaluate Resume"):
    if uploaded_file is not None and jd.strip() != "":
        resume_text = input_pdf_text(uploaded_file)

        st.session_state["resume_text"] = resume_text
        st.session_state["jd"] = jd

        final_prompt = input_prompt.format(text=resume_text, jd=jd)

        with st.spinner("Analyzing resume with ATS..."):
            response = get_gemini_response(final_prompt, json_mode=True)

        parsed = safe_json_parse(response)

        st.subheader("📝 ATS Evaluation")
        if "error" in parsed:
            st.warning("⚠ Could not parse response, showing raw output:")
            st.text(parsed.get("raw", response))
        else:
            # Progress bar for JD Match %
            try:
                match_value = int(parsed["JD Match"].replace("%", "").strip())
                st.progress(match_value / 100)
                st.metric("JD Match", f"{match_value}%")
            except:
                st.json(parsed)

            # Show missing keywords as tags
            if parsed.get("MissingKeywords"):
                st.write("**Missing Keywords:**")
                st.write(", ".join([f"`{kw}`" for kw in parsed["MissingKeywords"]]))

            # Profile summary
            if parsed.get("Profile Summary"):
                st.write("**Profile Summary:**")
                st.info(parsed["Profile Summary"])
    else:
        st.warning("⚠ Please provide both a Job Description and a PDF resume.")

# -------------------- Optimize Resume --------------------
if st.session_state["resume_text"] and st.session_state["jd"]:
    if st.button("✨ Optimize Resume"):
        with st.spinner("Rewriting resume for ATS optimization..."):
            optimized_resume = optimize_resume(st.session_state["resume_text"], st.session_state["jd"])

        st.subheader("✅ Optimized Resume Preview")
        st.markdown(f"```\n{optimized_resume}\n```")

        # Download as TXT
        st.download_button(
            "⬇ Download Optimized Resume (TXT)",
            optimized_resume,
            file_name="optimized_resume.txt"
        )

        # Download as PDF
        pdf_file = generate_pdf(optimized_resume)
        st.download_button(
            "⬇ Download Optimized Resume (PDF)",
            pdf_file,
            file_name="optimized_resume.pdf"
        )
