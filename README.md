# PDF OCR Processing Pipeline

A clean, efficient pipeline for extracting both printed and handwritten text from PDFs using EasyOCR - a single, reliable OCR engine that handles all text types with excellent accuracy.

## 🚀 Quick Start

1. **Drop PDF files** into the `raw_pdfs/` folder
2. **Run the processor**: `./scripts/pdf_processor.sh process`
3. **Get your text files** from the `outputs/` folder

## 📁 Project Structure

```
pdf-processing-pipeline/
├── raw_pdfs/                 # Drop PDF files here
├── outputs/                  # Processed text files appear here
├── used_pdfs/               # Processed PDFs are moved here
├── temp/                    # Temporary files (auto-cleaned)
├── logs/                    # Processing logs
├── scripts/                 # All processing scripts
│   ├── pdf_processor.sh     # Main processing pipeline
│   ├── enhanced_handwriting_processor.sh  # Enhanced handwriting OCR
│   ├── setup.sh             # Dependency checker
│   ├── test_pipeline.sh     # Testing and examples
│   └── install_handwriting_ocr.sh  # Installation guide
├── docs/                    # Documentation
├── examples/               # Example files and outputs
└── ocr_env/               # Python virtual environment
```

## 🛠️ Scripts Overview

### Main Scripts

- **`pdf_processor.sh`** - Complete pipeline with multiple OCR engines
- **`enhanced_handwriting_processor.sh`** - Specialized handwriting recognition
- **`setup.sh`** - Check dependencies and installation status

### Usage

```bash
# Check dependencies
./scripts/setup.sh

# Process all PDFs once
./scripts/pdf_processor.sh process

# Monitor directory continuously
./scripts/pdf_processor.sh monitor

# Enhanced handwriting processing
./scripts/enhanced_handwriting_processor.sh process

# Get installation help
./scripts/install_handwriting_ocr.sh
```

## 🔧 Features

### Text Recognition
- **Tesseract OCR** - High-quality printed text recognition
- **Multiple preprocessing modes** - Grayscale, contrast adjustment, noise removal
- **Intelligent page segmentation** - Automatic layout detection

### Handwriting Recognition
- **Kraken HTR** - Advanced handwriting text recognition
- **Calamari OCR** - Ensemble handwriting models
- **eScriptorium** - Professional manuscript processing
- **Enhanced preprocessing** - Multiple image optimization techniques

### Pipeline Features
- **Batch processing** - Handle multiple PDFs automatically
- **Error handling** - Robust processing with detailed logging
- **File management** - Automatic organization of processed files
- **Monitoring mode** - Continuous processing of new files

## 📋 Dependencies

### Core (Required)
- `pdftoppm` - PDF to image conversion
- `convert` (ImageMagick) - Image preprocessing
- `tesseract` - Basic OCR functionality

### Handwriting OCR (Recommended)
- `kraken` - Advanced handwriting recognition
- `calamari-predict` - Ensemble OCR models
- `escriptorium` - Professional manuscript processing
- `easyocr` - Simple handwriting OCR alternative

### Optional
- `deep-erase` - Artifact removal (smudges, underlines)

## 🔍 Output Format

Each processed PDF generates a comprehensive text file with clearly labeled sections:

```
=== PAGE 1 ===

=== TESSERACT OUTPUT ===
[printed text results]

=== KRAKEN HTR OUTPUT ===
[handwriting recognition results]

=== CALAMARI HTR OUTPUT ===
[ensemble handwriting results]

=== PAGE 2 ===
...
```

## 🚨 Troubleshooting

### Handwriting Not Recognized?
1. Run `./scripts/setup.sh` to check dependencies
2. Install handwriting OCR tools: `./scripts/install_handwriting_ocr.sh`
3. Try the enhanced processor: `./scripts/enhanced_handwriting_processor.sh`

### Installation Issues?
- Use `pipx` for isolated Python environments
- Try Docker containers for complex dependencies
- Check the installation guide for alternatives

### Processing Errors?
- Check `logs/workflow.log` for detailed error messages
- Ensure PDFs are not password-protected
- Verify sufficient disk space in `temp/` directory

## 📊 Logging

All processing activities are logged to `logs/workflow.log` with timestamps:
- File processing status
- OCR engine results
- Error messages and warnings
- Performance metrics

## 🎯 Advanced Usage

### Custom OCR Settings
Modify the scripts to adjust OCR parameters for specific document types.

### Batch Processing
Use monitoring mode for automatic processing of incoming PDFs.

### Integration
The pipeline can be integrated into larger document processing workflows.

---

**Need help?** Check the scripts in the `scripts/` folder or run `./scripts/setup.sh` for dependency information.
