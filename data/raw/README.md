# 📁 Raw PDFs Folder

## 🎯 Purpose
This folder is for PDF files that you want to process with the batch data checker.

## 📋 How to Use

### 1. Add PDFs Here
- **Drag and drop** PDF files directly into this folder
- **Copy/paste** PDFs from other locations
- **Move** PDFs from Downloads or other folders

### 2. Run Batch Processing
```bash
# From the project root directory:
python3 data_checker.py
```

### 3. File Organization Tips
- Use descriptive filenames (e.g., `SOL_Box27b_FF14_1977-78.pdf`)
- Include date ranges in filenames when possible
- Group related documents together

## 🗂️ Supported Formats
- ✅ PDF files (.pdf)
- ✅ Any language (Spanish, Portuguese, English, etc.)
- ✅ Scanned or text-based PDFs

## 📊 What Happens Next
1. The system will ask for a target date range
2. It will extract metadata from each PDF:
   - Title
   - Publication date
   - Description/summary
   - Volume/issue numbers
3. You can review and correct the results
4. The system learns from your corrections

## 💡 Tips
- **Date Range Targeting**: When prompted, enter dates like "1977-78" or "1979" to help the system focus on the right time period
- **Multilingual Support**: The system automatically detects and processes documents in any language
- **Learning System**: Your corrections improve future extractions

---
*Ready to process your PDFs? Just drag them into this folder and run `python3 data_checker.py`!*
