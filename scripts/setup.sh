#!/bin/bash

# Setup script for PDF processing pipeline
# Checks dependencies and provides installation guidance

echo "=== PDF Processing Pipeline Setup ==="
echo

# Function to check if command exists
check_command() {
    local cmd="$1"
    local install_info="$2"
    
    if command -v "$cmd" &> /dev/null; then
        echo "✅ $cmd is installed"
        return 0
    else
        echo "❌ $cmd is NOT installed"
        echo "   Install with: $install_info"
        return 1
    fi
}

# Check all required dependencies
echo "Checking dependencies..."
echo

missing_deps=0

# Core utilities
check_command "pdftoppm" "brew install poppler" || ((missing_deps++))
check_command "convert" "brew install imagemagick" || ((missing_deps++))
check_command "tesseract" "brew install tesseract" || ((missing_deps++))

# Optional but recommended
echo
echo "Handwriting OCR dependencies (RECOMMENDED):"
check_command "kraken" "pip install kraken" || echo "   (RECOMMENDED: for handwriting text recognition - HTR)"
check_command "calamari-predict" "pip install calamari-ocr" || echo "   (RECOMMENDED: for ensemble handwriting OCR)"
check_command "escriptorium" "pip install escriptorium" || echo "   (RECOMMENDED: for advanced HTR with segmentation)"

echo
echo "Image preprocessing dependencies:"
check_command "deep-erase" "pip install deep-erase" || echo "   (Optional: for artifact removal - smudges, underlines)"

echo
if [ $missing_deps -eq 0 ]; then
    echo "✅ All core dependencies are installed!"
    echo "You can run the PDF processor now."
else
    echo "⚠️  $missing_deps core dependencies are missing."
    echo "Please install them before running the processor."
fi

echo
echo "=== Usage ==="
echo "./pdf_processor.sh process    # Process all PDFs in raw_pdfs/ once"
echo "./pdf_processor.sh monitor    # Continuously monitor for new PDFs"
echo "./pdf_processor.sh help       # Show help"
echo
echo "Directory structure:"
echo "  raw_pdfs/    - Drop PDF files here"
echo "  outputs/     - Processed text files appear here"
echo "  used_pdfs/   - Processed PDFs are moved here"
echo "  temp/        - Temporary files (auto-cleaned)"
echo "  workflow.log - Processing log"
