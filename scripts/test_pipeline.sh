#!/bin/bash

# Test script to demonstrate the PDF processing pipeline

echo "=== PDF Processing Pipeline Test ==="
echo

# Check if we have any test PDFs
if [ ! -f "raw_pdfs/*.pdf" ] && [ "$(ls -A raw_pdfs/ 2>/dev/null)" = "" ]; then
    echo "No PDFs found in raw_pdfs/ directory."
    echo "To test the pipeline:"
    echo "1. Drop some PDF files into the raw_pdfs/ directory"
    echo "2. Run: ./pdf_processor.sh process"
    echo
    echo "Or run in monitoring mode:"
    echo "./pdf_processor.sh monitor"
    echo
else
    echo "Found PDFs in raw_pdfs/ directory. Running processor..."
    ./pdf_processor.sh process
fi

echo
echo "=== Pipeline Commands Summary ==="
echo
echo "1. Setup and dependency check:"
echo "   ./setup.sh"
echo
echo "2. Process all PDFs once:"
echo "   ./pdf_processor.sh process"
echo
echo "3. Monitor directory continuously:"
echo "   ./pdf_processor.sh monitor"
echo
echo "4. View processing log:"
echo "   tail -f workflow.log"
echo
echo "5. Manual commands for individual steps:"
echo
echo "   # Convert PDF to images:"
echo "   pdftoppm -png input.pdf output_prefix"
echo
echo "   # Preprocess image (grayscale + contrast):"
echo "   convert input.png -colorspace Gray -normalize -contrast-stretch 2%x1% output.png"
echo
echo "   # Remove artifacts with DeepErase:"
echo "   deep-erase --input input.png --output output.png --remove-underlines --remove-boxes"
echo
echo "   # OCR with Tesseract:"
echo "   tesseract input.png output -l eng --oem 1 --psm 6"
echo
echo "   # OCR with Kraken:"
echo "   kraken -i input.png output.txt"
echo
echo "   # OCR with Calamari:"
echo "   calamari-predict --files input.png --output.format txt"
echo
echo "   # eScriptorium batch processing:"
echo "   escriptorium batch --config batch_config.json"
echo
