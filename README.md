# AcademicDoc AI

AcademicDoc AI is a Python-based document processing and knowledge assistant for academic PDFs. It extracts information from digital and scanned documents, performs validation and consistency checks, compares documents, provides document analytics, and supports question answering using extracted document content.

## Features

### PDF Upload

Upload academic PDF documents for analysis.

### Text Extraction & OCR

Extracts text from digital PDFs and applies OCR when readable text is unavailable, including scanned documents.

### Academic Information Extraction

Identifies key academic information such as:

- Student name
- Institution
- Course
- Graduation year
- CGPA

### Document Validation

Checks whether required academic fields are present and validates formats such as CGPA and graduation year.

### Consistency Checking

Identifies missing fields, invalid values, and obvious inconsistencies in extracted information.

### Document Analytics

Displays document pages, extracted text sections, detected fields, and validation results.

### Document Comparison

Compares two academic PDFs and highlights differences in extracted fields.

### Question Answering

Allows users to ask questions about an uploaded document and receive answers based on its extracted content.

### Report & Data Export

Provides options to export extracted data and validation reports.

## Technologies

- Python
- Streamlit
- PyMuPDF
- Tesseract OCR
- OCR and document processing
- Retrieval-Augmented Generation (RAG)
- Local LLM-based question answering

## Project Structure

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
│   ├── upload.png
│   ├── ocr-extraction.png
│   ├── comparison-qa.png
│   └── results.png
│
└── data/
    ├── sample_academic_document.pdf
    ├── sample_academic_document_2.pdf
    └── scanned_academic_test.pdf
```

## Application Screenshots

### 1. Upload & Document Workspace

![AcademicDoc AI Upload](Screenshots/upload.png)

### 2. OCR & Academic Information Extraction

![AcademicDoc AI OCR](Screenshots/ocr-extraction.png)

### 3. Document Comparison & Question Answering

![AcademicDoc AI Comparison](Screenshots/comparison-qa.png)

### 4. Validation, Analytics & Export

![AcademicDoc AI Results](Screenshots/results.png)

## How It Works

1. Upload an academic PDF.
2. Extract text from the document.
3. Apply OCR when required for scanned documents.
4. Identify key academic information.
5. Perform validation and consistency checks.
6. Compare academic documents when a second document is provided.
7. Ask questions about the uploaded document.
8. Export extracted data or validation results.

## Project Purpose

AcademicDoc AI demonstrates how document processing, OCR, information extraction, validation checks, document comparison, and retrieval-based question answering can be combined into a single academic document assistant.

## Important Note

The validation features validate information extracted from the uploaded document. They do not establish that a document is an authentic certificate issued by an institution.
