# 📄 AcademicDoc AI

AcademicDoc AI is an academic document verification and knowledge assistant that extracts information from academic PDFs, validates key fields, compares documents, and answers questions using the extracted document content.

## ✨ Features

- 📤 **PDF Upload**  
  Upload academic PDF documents for analysis.

- 🔍 **Text Extraction & OCR**  
  Extracts text from digital PDFs and uses OCR when readable text is unavailable.

- 🎓 **Academic Information Extraction**  
  Detects:
  - Student name
  - Institution
  - Course
  - Graduation year
  - CGPA

- ✅ **Document Verification**  
  Checks whether required academic fields are present and validates CGPA and graduation-year formats.

- 🧩 **Consistency Checking**  
  Identifies missing fields, invalid values, and obvious inconsistencies in extracted information.

- 📊 **Document Analytics**  
  Displays pages, text sections, detected fields, and verification results.

- 🔄 **Document Comparison**  
  Compares two academic PDFs and highlights differences in extracted fields.

- 💬 **Question Answering**  
  Ask questions about the uploaded document and receive answers based on its extracted content.

- 📥 **Report & Data Export**  
  Provides extracted-data and verification-report export options.

## 🛠️ Technologies

- Python
- Streamlit
- PyMuPDF
- Tesseract OCR
- OCR/document processing
- Local RAG-based document question answering

## 📁 Project Structure

```text
AcademicDoc-AI/
│
├── app.py
├── vector_store.py
├── test.py
├── .gitignore
├── requirements.txt
│
├── Screenshots/
│   ├── 01-upload.png
│   ├── 02-ocr-extraction.png
│   ├── 03-comparison-qa.png
│   └── 04-results.png
│
└── data/
    ├── sample_academic_document.pdf
    ├── sample_academic_document_2.pdf
    └── scanned_academic_test.pdf
