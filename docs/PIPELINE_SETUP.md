# PDF Metadata Extraction Pipeline Setup

## Overview
This pipeline extracts structured metadata (title, date, abstract, volume/issue) from PDFs using OCR, text preprocessing, LLM-based extraction, validation, and optional Google Sheets export.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Basic Usage (No OCR, No Google Sheets)
```bash
python app.py
```
Upload PDFs through the web interface at `http://localhost:5001`

### 3. Enable OCR Processing
```bash
export USE_OCR=true
python app.py
```

### 4. Enable Google Sheets Export
1. Create a Google Cloud project and enable the Sheets API
2. Download credentials as `credentials.json` in the project root
3. Set your Google Sheet ID:
```bash
export GOOGLE_SHEET_ID=your_sheet_id_here
python app.py
```

## Pipeline Stages

### Stage 1: OCR (Optional)
- **Purpose**: Extract text from scanned PDFs or images
- **Engine**: EasyOCR with English language support
- **Input**: PDF pages converted to images
- **Output**: Raw OCR text

### Stage 2: Text Preprocessing
- **Purpose**: Clean and segment text for better LLM processing
- **Process**: 
  - Remove OCR artifacts and normalize whitespace
  - Split into logical segments (paragraphs)
  - Limit to first 10 segments for efficiency
- **Output**: List of clean text segments

### Stage 3: Metadata Extraction (LLM)
- **Purpose**: Extract structured metadata using Ollama
- **Model**: llama3.2 (configurable)
- **Extracts**:
  - **Title**: Exact document title as written
  - **Date**: Publication or issue date
  - **Abstract**: 1-3 sentence summary
  - **Volume/Issue**: Volume and issue numbers if available

### Stage 4: Validation
- **Purpose**: Validate extracted metadata and flag issues
- **Checks**:
  - Title length (3-200 characters)
  - Date format (contains 4-digit year)
  - Abstract length (10-1000 characters)
  - JSON schema compliance
- **Output**: Validated data with warnings list

### Stage 5: HITL Review (Human-in-the-Loop)
- **Purpose**: Flag uncertain extractions for human review
- **Trigger**: When validation warnings exist
- **Action**: Log warnings (in production, would notify human reviewer)

### Stage 6: Export (Optional)
- **Purpose**: Export validated metadata to Google Sheets
- **Format**: One row per document with Title, Date, Abstract, Volume/Issue columns
- **Trigger**: Only when validation passes and Google Sheets is configured

## Configuration

### Environment Variables
- `USE_OCR=true/false` - Enable OCR processing
- `GOOGLE_SHEET_ID=your_id` - Google Sheet ID for export

### Files
- `credentials.json` - Google Sheets API credentials
- `token.json` - Auto-generated OAuth token

## Troubleshooting

### Common Issues
1. **Ollama not running**: Start Ollama service and pull llama3.2 model
2. **OCR dependencies**: Install system dependencies for EasyOCR
3. **Google Sheets auth**: Ensure credentials.json is properly configured
4. **Memory issues**: Large PDFs may require more RAM for OCR processing

### System Dependencies (for OCR)
- **macOS**: `brew install poppler` (for pdf2image)
- **Ubuntu**: `sudo apt-get install poppler-utils` 
- **Windows**: Download poppler binaries

## Performance Notes
- OCR processing is memory and CPU intensive
- Large batch uploads may timeout - process smaller batches
- First OCR run downloads EasyOCR models (~100MB)
