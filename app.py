import io
import re
from datetime import datetime

import streamlit as st
import fitz  # PyMuPDF
import pytesseract

from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AcademicDoc AI",
    page_icon="📄",
    layout="wide"
)

# Tesseract path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# PROFESSIONAL UI
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(124,58,237,.10), transparent 28%),
            radial-gradient(circle at 92% 8%, rgba(37,99,235,.10), transparent 30%),
            #f7f8fc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .hero {
        padding: 34px 38px;
        border-radius: 28px;
        color: white;
        background: linear-gradient(135deg, #111827 0%, #312e81 48%, #2563eb 100%);
        box-shadow: 0 20px 50px rgba(37,50,100,.18);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: '';
        position: absolute;
        width: 250px; height: 250px;
        right: -80px; top: -100px;
        border-radius: 50%;
        background: rgba(255,255,255,.09);
    }

    .hero-kicker {
        font-size: 12px; font-weight: 800; letter-spacing: 1.6px;
        text-transform: uppercase; opacity: .82; margin-bottom: 8px;
    }

    .hero-title { font-size: 38px; line-height: 1.1; font-weight: 800; margin: 0; }
    .hero-subtitle { font-size: 16px; margin-top: 10px; opacity: .88; max-width: 720px; }

    .workflow {
        display: grid; grid-template-columns: repeat(4,1fr); gap: 12px;
        margin: 18px 0 30px;
    }

    .step {
        background: rgba(255,255,255,.88); border: 1px solid #e5e7eb;
        border-radius: 17px; padding: 16px;
        box-shadow: 0 8px 24px rgba(15,23,42,.05);
        transition: all .18s ease;
    }
    .step:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(15,23,42,.09); }
    .step-number { font-size: 11px; font-weight: 800; color: #6366f1; margin-bottom: 6px; }
    .step-name { font-size: 15px; font-weight: 700; color: #1e293b; }

    .section-title { font-size: 22px; font-weight: 800; color: #111827; margin-top: 28px; margin-bottom: 5px; }
    .section-subtitle { color: #64748b; font-size: 14px; margin-bottom: 16px; }

    .card {
        background: rgba(255,255,255,.92); border: 1px solid #e5e7eb;
        border-radius: 20px; padding: 22px;
        box-shadow: 0 8px 28px rgba(15,23,42,.055); margin-bottom: 18px;
    }

    .mini-label { color:#64748b; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.7px; }
    .mini-value { color:#111827; font-size:16px; font-weight:700; margin-top:5px; word-break:break-word; }

    [data-testid='stMetric'] {
        background:white; border:1px solid #e5e7eb; border-radius:16px;
        padding:16px; box-shadow:0 7px 20px rgba(15,23,42,.045);
    }
    [data-testid='stMetricLabel'] { color:#64748b !important; }
    [data-testid='stMetricValue'] { color:#111827 !important; }

    [data-testid='stFileUploader'] {
        background:white; border-radius:18px; padding:8px;
        border:1px solid #e5e7eb; box-shadow:0 8px 25px rgba(15,23,42,.045);
    }
    [data-testid='stFileUploaderDropzone'] { border-radius:14px !important; border:1px dashed #94a3b8 !important; }

    [data-testid='stTextInput'] input {
        border-radius:12px !important; border:1px solid #cbd5e1 !important; min-height:46px;
    }
    [data-testid='stTextInput'] input:focus {
        border-color:#6366f1 !important; box-shadow:0 0 0 2px rgba(99,102,241,.12) !important;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius:12px !important;
        border:1px solid #dbeafe !important;
        background:linear-gradient(135deg,#4f46e5,#2563eb) !important;
        color:white !important; font-weight:700 !important; min-height:44px;
        box-shadow:0 8px 18px rgba(37,99,235,.18);
        cursor:pointer !important; transition:all .18s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform:translateY(-1px); box-shadow:0 12px 24px rgba(37,99,235,.25);
    }

    [data-testid='stAlert'] { border-radius:14px; }
    [data-testid='stExpander'] { border:1px solid #e5e7eb; border-radius:14px; background:rgba(255,255,255,.72); }
    [data-testid='stDataFrame'] { border-radius:14px; overflow:hidden; }

    .footer { text-align:center; color:#94a3b8; font-size:12px; padding:24px 0 4px; }

    @media (max-width:800px) {
        .workflow { grid-template-columns:repeat(2,1fr); }
        .hero-title { font-size:30px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================
if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "page_texts" not in st.session_state:
    st.session_state.page_texts = []

if "academic_info" not in st.session_state:
    st.session_state.academic_info = {}

if "filename" not in st.session_state:
    st.session_state.filename = ""

if "second_document_text" not in st.session_state:
    st.session_state.second_document_text = ""

if "second_academic_info" not in st.session_state:
    st.session_state.second_academic_info = {}

if "used_ocr" not in st.session_state:
    st.session_state.used_ocr = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    """Clean extracted/OCR text."""
    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")

    # Normalize spaces but preserve line structure
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def ocr_page(page):
    """Render a PDF page and perform OCR."""
    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2),
        alpha=False
    )

    image = Image.open(io.BytesIO(pix.tobytes("png")))

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return clean_text(text)


def extract_pdf(file_bytes):
    """
    Extract text from PDF.
    If normal PDF extraction gives little/no text,
    automatically use OCR.
    """

    doc = fitz.open(stream=file_bytes, filetype="pdf")

    page_texts = []
    used_ocr = False

    for page in doc:
        text = clean_text(page.get_text("text"))

        # OCR fallback for scanned pages
        if len(text.strip()) < 30:
            text = ocr_page(page)
            used_ocr = True

        page_texts.append(text)

    doc.close()

    full_text = "\n\n".join(
        f"Page {i + 1}\n{text}"
        for i, text in enumerate(page_texts)
        if text.strip()
    )

    return page_texts, clean_text(full_text), used_ocr


# ============================================================
# FIELD EXTRACTION
# ============================================================

def extract_student_name(text):
    patterns = [
        r"Student\s*Name\s*[:\-]\s*([^\n]+)",
        r"Name\s*of\s*Student\s*[:\-]\s*([^\n]+)",
        r"Student\s*[:\-]\s*([^\n]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value:
                return value

    return "Not found"


def extract_institution(text):
    patterns = [
        r"Institution\s*[:\-]\s*([^\n]+)",
        r"College\s*[:\-]\s*([^\n]+)",
        r"University\s*[:\-]\s*([^\n]+)",
        r"Institute\s*[:\-]\s*([^\n]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value:
                return value

    return "Not found"


def extract_course(text):
    """
    Course extraction.

    Important:
    The test document contains:

    Bachelor of Technology in Computer Science

    WITHOUT writing:
    Course: Bachelor of Technology...

    Therefore we explicitly detect common degree phrases.
    """

    # First try explicit Course labels
    labeled_patterns = [
        r"Course\s*[:\-]\s*([^\n]+)",
        r"Program\s*[:\-]\s*([^\n]+)",
        r"Degree\s*[:\-]\s*([^\n]+)",
        r"Programme\s*[:\-]\s*([^\n]+)"
    ]

    for pattern in labeled_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1).strip()

            if value and value.lower() not in [
                "not found",
                "n/a",
                "na"
            ]:
                return value

    # Detect degree names even without "Course:"
    degree_patterns = [
        r"(Bachelor\s+of\s+Technology\s+in\s+[A-Za-z&,\-\s]+)",
        r"(Bachelor\s+of\s+Engineering\s+in\s+[A-Za-z&,\-\s]+)",
        r"(Bachelor\s+of\s+Science\s+in\s+[A-Za-z&,\-\s]+)",
        r"(Bachelor\s+of\s+Computer\s+Applications)",
        r"(Bachelor\s+of\s+Business\s+Administration)",
        r"(Master\s+of\s+Technology\s+in\s+[A-Za-z&,\-\s]+)",
        r"(Master\s+of\s+Engineering\s+in\s+[A-Za-z&,\-\s]+)",
        r"(Master\s+of\s+Science\s+in\s+[A-Za-z&,\-\s]+)",
        r"(Master\s+of\s+Computer\s+Applications)",
        r"(Diploma\s+in\s+[A-Za-z&,\-\s]+)"
    ]

    for pattern in degree_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1).strip()

            # Remove accidental trailing labels
            value = re.split(
                r"\b(?:Graduation|Year|CGPA|Grade|GPA)\b",
                value,
                flags=re.IGNORECASE
            )[0].strip()

            return value

    return "Not found"


def extract_graduation_year(text):
    patterns = [
        r"Graduation\s*Year\s*[:\-]\s*(\d{4})",
        r"Year\s*of\s*Graduation\s*[:\-]\s*(\d{4})",
        r"Graduated\s*[:\-]\s*(\d{4})",
        r"Graduation\s*[:\-]\s*(\d{4})"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1)

    return "Not found"


def extract_cgpa(text):
    patterns = [
        r"CGPA\s*[:\-]\s*(\d+(?:\.\d+)?)",
        r"C\.G\.P\.A\.?\s*[:\-]\s*(\d+(?:\.\d+)?)",
        r"Cumulative\s+GPA\s*[:\-]\s*(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1)

    return "Not found"


def extract_academic_info(text):
    return {
        "Student Name": extract_student_name(text),
        "Institution": extract_institution(text),
        "Course": extract_course(text),
        "Graduation Year": extract_graduation_year(text),
        "CGPA": extract_cgpa(text)
    }


# ============================================================
# VERIFICATION
# ============================================================

def verify_academic_info(info):
    results = []

    # CGPA
    cgpa = info["CGPA"]

    if cgpa == "Not found":
        results.append({
            "name": "CGPA",
            "passed": False,
            "message": "CGPA was not found."
        })
    else:
        try:
            value = float(cgpa)

            if 0 <= value <= 10:
                results.append({
                    "name": "CGPA",
                    "passed": True,
                    "message": f"CGPA format is valid: {cgpa}"
                })
            else:
                results.append({
                    "name": "CGPA",
                    "passed": False,
                    "message": f"CGPA is outside the expected 0–10 range: {cgpa}"
                })

        except ValueError:
            results.append({
                "name": "CGPA",
                "passed": False,
                "message": f"CGPA format is invalid: {cgpa}"
            })

    # Graduation year
    year = info["Graduation Year"]

    if year == "Not found":
        results.append({
            "name": "Graduation Year",
            "passed": False,
            "message": "Graduation year format could not be validated."
        })
    else:
        try:
            year_value = int(year)
            current_year = datetime.now().year

            if 1900 <= year_value <= current_year + 10:
                results.append({
                    "name": "Graduation Year",
                    "passed": True,
                    "message": f"Graduation year format is valid: {year}"
                })
            else:
                results.append({
                    "name": "Graduation Year",
                    "passed": False,
                    "message": f"Graduation year is outside the expected range: {year}"
                })

        except ValueError:
            results.append({
                "name": "Graduation Year",
                "passed": False,
                "message": "Graduation year is not a valid year."
            })

    # Required academic fields
    missing = []

    for field, value in info.items():
        if value == "Not found":
            missing.append(field)

    results.append({
        "name": "Required Fields",
        "passed": len(missing) == 0,
        "message": (
            "All required academic fields were found."
            if not missing
            else "Missing: " + ", ".join(missing)
        )
    })

    return results


def consistency_checks(info):
    issues = []

    # Missing values
    for field, value in info.items():
        if value == "Not found":
            issues.append(f"{field} is missing.")

    # CGPA check
    if info["CGPA"] != "Not found":
        try:
            cgpa = float(info["CGPA"])

            if cgpa < 0 or cgpa > 10:
                issues.append("CGPA is outside the expected 0–10 range.")

        except ValueError:
            issues.append("CGPA is not numeric.")

    # Graduation year check
    if info["Graduation Year"] != "Not found":
        try:
            year = int(info["Graduation Year"])

            if year < 1900 or year > datetime.now().year + 10:
                issues.append("Graduation year appears unusual.")

        except ValueError:
            issues.append("Graduation year is not numeric.")

    return issues


# ============================================================
# RAG / QUESTION ANSWERING
# ============================================================

def retrieve_relevant_sections(question, page_texts, top_k=3):
    valid_pages = [
        text for text in page_texts
        if text and text.strip()
    ]

    if not valid_pages:
        return []

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        matrix = vectorizer.fit_transform(
            valid_pages + [question]
        )

        similarities = cosine_similarity(
            matrix[-1],
            matrix[:-1]
        )[0]

        ranked = similarities.argsort()[::-1]

        results = []

        for index in ranked[:top_k]:
            if similarities[index] > 0:
                results.append({
                    "page": index + 1,
                    "text": valid_pages[index],
                    "score": similarities[index]
                })

        return results

    except Exception:
        return []


def answer_question(question, info, page_texts):
    question_lower = question.lower()

    # Direct structured answers
    if "student" in question_lower and "name" in question_lower:
        return info["Student Name"], []

    if "institution" in question_lower or "college" in question_lower:
        return info["Institution"], []

    if "course" in question_lower or "degree" in question_lower:
        return info["Course"], []

    if "graduation" in question_lower and "year" in question_lower:
        return info["Graduation Year"], []

    if "cgpa" in question_lower or "gpa" in question_lower:
        return info["CGPA"], []

    # Generic retrieval
    results = retrieve_relevant_sections(
        question,
        page_texts
    )

    if not results:
        return (
            "I could not find relevant information in the document.",
            []
        )

    best = results[0]["text"]

    # Simple answer from relevant passage
    answer = best[:1200]

    return answer, results


# ============================================================
# PDF REPORT
# ============================================================

def create_verification_report(
    filename,
    info,
    verification_results,
    consistency_issues
):
    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(
        50,
        y,
        "AcademicDoc AI - Verification Report"
    )

    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        50,
        y,
        f"Document: {filename}"
    )

    y -= 35

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(
        50,
        y,
        "Extracted Academic Information"
    )

    y -= 25

    pdf.setFont("Helvetica", 10)

    for field, value in info.items():

        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        pdf.drawString(
            60,
            y,
            f"{field}: {value}"
        )

        y -= 20

    y -= 15

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(
        50,
        y,
        "Verification Results"
    )

    y -= 25

    pdf.setFont("Helvetica", 10)

    for result in verification_results:

        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        status = "PASS" if result["passed"] else "FAIL"

        pdf.drawString(
            60,
            y,
            f"{status}: {result['message']}"
        )

        y -= 20

    y -= 15

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(
        50,
        y,
        "Consistency Check"
    )

    y -= 25

    pdf.setFont("Helvetica", 10)

    if not consistency_issues:
        pdf.drawString(
            60,
            y,
            "No obvious consistency issues were detected."
        )
    else:
        for issue in consistency_issues:

            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)

            pdf.drawString(
                60,
                y,
                f"- {issue}"
            )

            y -= 20

    y -= 30

    pdf.setFont("Helvetica-Oblique", 8)

    pdf.drawString(
        50,
        y,
        "These checks do not prove that the document is an authentic"
    )

    y -= 12

    pdf.drawString(
        50,
        y,
        "certificate issued by an institution."
    )

    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# DASHBOARD UI
# ============================================================

if "question_answer" not in st.session_state:
    st.session_state.question_answer = ""
if "question_sources" not in st.session_state:
    st.session_state.question_sources = []
if "second_filename" not in st.session_state:
    st.session_state.second_filename = ""

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 18% 0%, rgba(91,108,140,.22), transparent 30%),
            radial-gradient(circle at 82% 18%, rgba(57,75,110,.18), transparent 34%),
            linear-gradient(135deg, #0d1627 0%, #17263d 48%, #0b1322 100%);
        color: #eef4ff;
    }
    .block-container { max-width: 1540px; padding: 24px 22px 32px; }
    header, #MainMenu, footer { visibility: hidden; }
    * { font-family: Inter, Arial, sans-serif; }

    /* Larger, clearer typography */
    .top-title { text-align:center; margin-bottom:8px; }
    .top-title h1 { margin:0; color:#fff; font-size:36px; font-weight:800; letter-spacing:-.8px; }
    .top-title p { margin:6px 0 18px; color:#e0e8f5; font-size:15px; line-height:1.5; }
    .workflow { display:flex; justify-content:center; align-items:center; margin:0 auto 22px; max-width:900px; }
    .workflow .wf-step { color:#f2f6ff; font-size:14px; font-weight:600; display:flex; align-items:center; gap:7px; white-space:nowrap; }
    .workflow .line { width:70px; height:2px; background:#667895; margin:0 14px; }
    .workflow .num { font-size:12px; font-weight:800; opacity:.95; }

    .panel-title { font-size:17px; font-weight:750; color:#f0f5ff; margin:0 0 12px; }
    .mini-label { font-size:13px; color:#c4d0e3; margin-bottom:5px; line-height:1.45; }
    .status-pill { display:inline-block; padding:6px 11px; border-radius:14px; background:#d8f5d5; color:#175d24; font-size:12px; font-weight:750; margin-bottom:8px; }

    /* Larger file/upload cards */
    .file-card {
        background:rgba(255,255,255,.10);
        border:1px solid rgba(255,255,255,.20);
        border-radius:12px;
        padding:13px 14px;
        color:#f1f6ff;
        font-size:13px;
        line-height:1.5;
        margin-top:10px;
        transition:all .18s ease;
    }
    .file-card:hover {
        border-color:rgba(147,197,253,.65);
        background:rgba(255,255,255,.14);
        transform:translateY(-1px);
    }

    .info-card { background:rgba(250,252,255,.98); color:#172238; border-radius:10px; padding:14px 16px; margin-top:8px; font-size:13px; line-height:1.75; box-shadow:0 4px 14px rgba(0,0,0,.16); }
    .info-card b { color:#111b2e; }
    .ok { color:#8cff8c; font-size:13px; margin:6px 0; }
    .warn { color:#ffd77f; font-size:13px; margin:6px 0; }
    .note { color:#cbd7e8; font-size:11px; line-height:1.5; margin-top:7px; }
    .analytics-title { margin-top:14px; font-size:14px; font-weight:750; color:#e9f1ff; }

    .metric-card { background:#f5f8fd; color:#263248; border-radius:9px; padding:11px 13px; min-height:68px; border:1px solid #d8e0ec; }
    .metric-card .label { font-size:11px; color:#53647c; }
    .metric-card .value { font-size:21px; font-weight:800; margin-top:4px; }

    /* More balanced three-column panels */
    .side-card {
        background:rgba(18,30,49,.78);
        border:1px solid rgba(255,255,255,.19);
        border-radius:14px;
        padding:16px;
        margin-bottom:14px;
        box-shadow:0 8px 24px rgba(0,0,0,.16);
    }
    .side-card:hover { border-color:rgba(148,163,184,.38); }
    .side-card h3 { margin:0 0 12px; color:#f1f5ff; font-size:17px; font-weight:750; }

    .answer-card { background:#f5f8fd; color:#172238; border-radius:10px; padding:14px; margin-top:10px; font-size:13px; line-height:1.6; }
    .source-card { background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.14); border-radius:9px; padding:10px; margin-top:8px; color:#e3ebf8; font-size:12px; line-height:1.5; }
    .footer-note { text-align:center; color:#b4c0d2; font-size:11px; margin-top:18px; }

    /* Clear interactive affordances */
    button, [role="button"], input[type="file"], .stDownloadButton button, textarea, input { cursor:pointer !important; }
    .stButton > button, .stDownloadButton > button {
        border-radius:10px !important;
        font-weight:750 !important;
        min-height:50px !important;
        font-size:14px !important;
        transition:transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform:translateY(-2px);
        box-shadow:0 8px 20px rgba(0,0,0,.28);
        border-color:#93c5fd !important;
    }
    .stButton > button:active, .stDownloadButton > button:active { transform:translateY(0); }

    /* Larger upload control; dark text on the white control */
    [data-testid="stFileUploader"] {
        background:rgba(255,255,255,.97) !important;
        border:1px solid #cbd5e1 !important;
        border-radius:12px !important;
        padding:12px !important;
        box-shadow:0 5px 16px rgba(0,0,0,.14);
    }
    [data-testid="stFileUploaderDropzone"] {
        min-height:150px !important;
        border:2px dashed #64748b !important;
        border-radius:10px !important;
        background:#f8fafc !important;
        padding:20px !important;
        transition:all .18s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color:#6366f1 !important;
        background:#eef2ff !important;
        box-shadow:0 0 0 3px rgba(99,102,241,.10);
    }
    [data-testid="stFileUploader"] button {
        min-height:46px !important;
        font-size:14px !important;
        font-weight:750 !important;
        color:#172033 !important;
        background:#ffffff !important;
        border:2px solid #94a3b8 !important;
        border-radius:9px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        color:#111827 !important;
        background:#eef2ff !important;
        border-color:#6366f1 !important;
    }
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] label {
        color:#334155 !important;
        font-size:13px !important;
    }

    /* Larger Ask input */
    .stTextInput input, .stTextArea textarea {
        background:#f8fafc !important;
        color:#172238 !important;
        border:2px solid #94a3b8 !important;
        border-radius:10px !important;
        font-size:15px !important;
        line-height:1.55 !important;
        padding:12px 14px !important;
    }
    .stTextArea textarea { min-height:170px !important; }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#64748b !important; opacity:1 !important; }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color:#818cf8 !important;
        box-shadow:0 0 0 3px rgba(129,140,248,.18) !important;
    }

    [data-testid="stHorizontalBlock"] { gap:20px !important; }

    @media (max-width:1100px) {
        .top-title h1 { font-size:32px; }
        .workflow .line { width:40px; margin:0 8px; }
    }
    @media (max-width:800px) {
        .top-title h1 { font-size:28px; }
        .top-title p { font-size:14px; }
        .workflow { flex-wrap:wrap; gap:8px; }
        .workflow .line { display:none; }
        .side-card { padding:14px; }
        [data-testid="stFileUploaderDropzone"] { min-height:125px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="top-title">
        <h1>AcademicDoc AI</h1>
        <p>Extract, verify, compare and ask questions about academic documents from one clean workspace</p>
    </div>
    <div class="workflow">
        <div class="wf-step"><span class="num">01</span> ⇧ Upload</div><div class="line"></div>
        <div class="wf-step"><span class="num">02</span> ◌ Extract</div><div class="line"></div>
        <div class="wf-step"><span class="num">03</span> ✓ Verify</div><div class="line"></div>
        <div class="wf-step"><span class="num">04</span> ◌ Ask</div>
    </div>
    """,
    unsafe_allow_html=True
)

left, center, right = st.columns([1.15, 1.85, 1.15], gap="medium")

with left:
    st.markdown('<div class="side-card"><h3>⇧ Upload Document</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload an academic PDF to analyze its contents.",
        type=["pdf"], key="main_pdf", label_visibility="collapsed"
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        if st.session_state.filename != uploaded_file.name:
            with st.spinner("Extracting document..."):
                try:
                    page_texts, full_text, used_ocr = extract_pdf(file_bytes)
                    academic_info = extract_academic_info(full_text)
                    st.session_state.page_texts = page_texts
                    st.session_state.document_text = full_text
                    st.session_state.academic_info = academic_info
                    st.session_state.filename = uploaded_file.name
                    st.session_state.used_ocr = used_ocr
                    st.session_state.question_answer = ""
                    st.session_state.question_sources = []
                except Exception as e:
                    st.error(f"Error processing PDF: {e}")
                    st.stop()
        st.markdown('<span class="status-pill">⌕ OCR Used</span>' if st.session_state.used_ocr else '<span class="status-pill">✓ Text Extracted</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="file-card">📄 {st.session_state.filename}<br><span style="color:#9fb0c8">'
            f'{len(file_bytes)/1024:.1f} KB • {len(st.session_state.page_texts)} page(s)</span> ✓</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

with center:
    if st.session_state.document_text:
        info = st.session_state.academic_info
        verification_results = verify_academic_info(info)
        passed_count = sum(r["passed"] for r in verification_results)
        consistency_issues = consistency_checks(info)
        fields_detected = sum(v != "Not found" for v in info.values())

        st.markdown('<div class="side-card">', unsafe_allow_html=True)
        st.markdown('<span class="status-pill">⌕ OCR Used</span>' if st.session_state.used_ocr else '<span class="status-pill">✓ Text Extracted</span>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📄 Document</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mini-label">{st.session_state.filename}</div><div class="mini-label">Extracted {len(st.session_state.page_texts)} text section(s)</div>', unsafe_allow_html=True)
        with st.expander("📖 Preview extracted document text", expanded=False):
            for i, page_text in enumerate(st.session_state.page_texts):
                st.markdown(f"**Page {i+1}**")
                st.text(page_text)
        st.success("Document indexed successfully.")

        st.markdown('<div class="panel-title">🎓 Academic Information</div>', unsafe_allow_html=True)
        st.markdown(f'''<div class="info-card">
        <b>Student Name:</b> {info['Student Name']}<br>
        <b>Institution:</b> {info['Institution']}<br>
        <b>Course:</b> {info['Course']}<br>
        <b>Graduation Year:</b> {info['Graduation Year']}<br>
        <b>CGPA:</b> {info['CGPA']}
        </div>''', unsafe_allow_html=True)

        st.markdown('<div class="panel-title" style="margin-top:10px">🔍 Document Verification</div>', unsafe_allow_html=True)
        vleft, vright = st.columns(2)
        for idx, r in enumerate(verification_results):
            target = vleft if idx < 2 else vright
            with target:
                cls = "ok" if r["passed"] else "warn"
                icon = "✓" if r["passed"] else "⚠"
                st.markdown(f'<div class="{cls}">{icon} {r["message"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="note">Verification checks passed: {passed_count}/3</div>', unsafe_allow_html=True)
        st.markdown('<div class="note">These checks validate information extracted from the uploaded document. They do not prove that the document is an authentic certificate issued by an institution.</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-title" style="margin-top:10px">🧩 Document Consistency</div>', unsafe_allow_html=True)
        if consistency_issues:
            st.markdown(f'<div class="warn">⚠ {len(consistency_issues)} consistency issue(s) detected.</div>', unsafe_allow_html=True)
            with st.expander("View consistency checks"):
                for issue in consistency_issues:
                    st.write("• " + issue)
        else:
            st.markdown('<div class="ok">✣ No obvious consistency issues were detected.</div>', unsafe_allow_html=True)
        st.markdown('<div class="note">Consistency checks identify issues in extracted document content. They are not a substitute for institutional verification or certificate authentication.</div>', unsafe_allow_html=True)

        st.markdown('<div class="analytics-title">📊 Document Analytics</div>', unsafe_allow_html=True)
        a,b,c,d = st.columns(4)
        for col,(label,value) in zip([a,b,c,d], [("Pages",len(st.session_state.page_texts)),("Text Sections",len(st.session_state.page_texts)),("Fields Detected",f"{fields_detected}/5"),("Verification",f"{passed_count}/3")]):
            with col:
                st.markdown(f'<div class="metric-card"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-title" style="margin-top:10px">📥 Export</div>', unsafe_allow_html=True)
        ex1, ex2 = st.columns(2)
        export_text = "\n".join(f"{field}: {value}" for field,value in info.items())
        report = create_verification_report(st.session_state.filename, info, verification_results, consistency_issues)
        with ex1:
            st.download_button("⇩ Export Data", export_text, "academic_extracted_data.txt", "text/plain", use_container_width=True)
        with ex2:
            st.download_button("⇩ Verification Report", report, "academic_verification_report.pdf", "application/pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="side-card" style="min-height:430px"><div class="panel-title">📄 Document</div><div class="note">Upload an academic PDF to begin.</div></div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="side-card"><h3>▤ Compare Documents</h3>', unsafe_allow_html=True)
    second_file = st.file_uploader("Choose a second academic PDF", type=["pdf"], key="second_pdf", label_visibility="collapsed")
    if second_file is not None and st.session_state.document_text:
        if st.session_state.second_filename != second_file.name:
            try:
                second_pages, second_text, _ = extract_pdf(second_file.getvalue())
                st.session_state.second_document_text = second_text
                st.session_state.second_academic_info = extract_academic_info(second_text)
                st.session_state.second_filename = second_file.name
            except Exception as e:
                st.error(f"Could not process second PDF: {e}")
        if st.session_state.second_academic_info:
            fields=["Student Name","Institution","Course","Graduation Year","CGPA"]
            matching=sum(st.session_state.academic_info[f] == st.session_state.second_academic_info[f] for f in fields)
            different=[(f,st.session_state.academic_info[f],st.session_state.second_academic_info[f]) for f in fields if st.session_state.academic_info[f] != st.session_state.second_academic_info[f]]
            st.caption(f"Matching: {matching}/5 • Different: {len(different)}")
            for f,v1,v2 in different:
                st.warning(f"{f}: {v1} ↔ {v2}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-card"><h3>💬 Ask a Question</h3>', unsafe_allow_html=True)
    question = st.text_area("Your question", placeholder="What is the student's CGPA?", height=180, key="question_box")
    if st.button("⌕ Ask", type="primary", use_container_width=True):
        if not st.session_state.document_text:
            st.warning("Upload a PDF first.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            answer, sources = answer_question(question, st.session_state.academic_info, st.session_state.page_texts)
            st.session_state.question_answer = answer
            st.session_state.question_sources = sources
    if st.session_state.question_answer:
        st.markdown(f'<div class="answer-card"><b>Answer</b><br>{st.session_state.question_answer}</div>', unsafe_allow_html=True)
        for i,source in enumerate(st.session_state.question_sources[:2]):
            st.markdown(f'<div class="source-card"><b>Result {i+1} • Page {source["page"]}</b><br>{source["text"][:500]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">AcademicDoc AI • Local RAG-based academic document assistant</div>', unsafe_allow_html=True)
