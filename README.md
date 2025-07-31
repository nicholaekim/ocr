# PDF Metadata Extraction Pipeline

A comprehensive PDF metadata extraction system with interactive batch processing and web interface.

## 📁 Project Structure

```
ocr3.0/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core pipeline logic
│   │   ├── __init__.py
│   │   └── pipeline.py              # Main PDF processing pipeline
│   ├── 📁 utils/                    # Utility scripts
│   │   ├── __init__.py
│   │   └── data_checker.py          # Interactive batch processor
│   └── 📁 web/                      # Web application
│       ├── __init__.py
│       ├── app.py                   # Flask web app
│       └── 📁 templates/            # HTML templates
│           └── index.html
├── 📁 data/                         # Data storage
│   ├── 📁 raw/                      # Input PDFs for batch processing
│   ├── 📁 processed/                # Processed files
│   ├── 📁 results/                  # Batch processing results
│   └── feedback_memory.json        # User feedback and fine-tuning data
├── 📁 config/                       # Configuration files
│   └── config.py                    # Pipeline configuration
├── 📁 docs/                         # Documentation
│   ├── DATA_CHECKER_GUIDE.md       # Data checker usage guide
│   └── PIPELINE_SETUP.md           # Pipeline setup guide
├── 📁 uploads/                      # Web app file uploads
├── 🚀 app.py                        # Web app launcher (run this)
├── 🚀 data_checker.py               # Batch processor launcher (run this)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Web Interface
```bash
python3 app.py
# Visit: http://localhost:5001
```

### 2. Batch Processing
```bash
python3 data_checker.py
# Processes all PDFs in data/raw/ folder
```

## 🌟 Features

- **Multilingual Support**: Processes documents in any language (Spanish, Portuguese, English, etc.)
- **Interactive Learning**: User corrections improve future extractions
- **Date Range Targeting**: Focus extraction on specific time periods
- **Web Interface**: Drag-and-drop PDF upload with instant results
- **Batch Processing**: Process multiple PDFs with interactive review
- **Fine-tuning Memory**: System learns user preferences over time

## 📊 Metadata Extraction

The system extracts:
- **Title**: Document title (preserved in original language)
- **Date**: Publication date (recognizes multilingual formats)
- **Description**: Brief summary (output in English for consistency)
- **Volume/Issue**: Publication volume and issue numbers

## 🔧 Configuration

- Place PDFs in `data/raw/` for batch processing
- User feedback stored in `data/feedback_memory.json`
- Results saved in `data/results/`
- Web uploads go to `uploads/`

## 📝 Usage Examples

**Batch Processing with Date Range:**
```bash
python3 data_checker.py
# Enter target date: "1977-78"
# System focuses on finding dates from that period
```

**Web Interface:**
- Upload PDFs via drag-and-drop
- View extracted metadata instantly
- System applies learned preferences automatically
