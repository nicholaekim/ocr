#!/bin/bash

# PDF Processing Pipeline
# Monitors raw_pdfs/, converts PDFs to images, preprocesses, runs OCR, and outputs text files

set -e  # Exit on any error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Directory paths
RAW_DIR="raw_pdfs"
USED_DIR="used_pdfs"
OUTPUT_DIR="outputs"
TEMP_DIR="temp"
LOG_FILE="logs/workflow.log"

# Ensure directories exist
mkdir -p "$RAW_DIR" "$USED_DIR" "$OUTPUT_DIR" "$TEMP_DIR"

# Logging function
log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Function to determine best OCR engines based on image analysis
determine_ocr_engines() {
    local engines=("tesseract" "trocr")
    echo "${engines[@]}"
}

# Function to preprocess image
preprocess_image() {
    local input_image="$1"
    local output_image="$2"
    
    log_message "Preprocessing image: $input_image"
    
    # Create standard processed version for text OCR
    convert "$input_image" -colorspace Gray -normalize -contrast-stretch 2%x1% "$output_image.tmp"
    
    # Use DeepErase to remove artifacts (smudges, underlines, boxes)
    if command -v deep-erase &> /dev/null; then
        deep-erase --input "$output_image.tmp" --output "$output_image" --remove-underlines --remove-boxes --remove-smudges
        rm "$output_image.tmp"
    else
        log_message "WARNING: deep-erase not found, skipping artifact removal"
        mv "$output_image.tmp" "$output_image"
    fi
    
    # Create enhanced version optimized for handwriting recognition
    local handwriting_image="${output_image%.*}_handwriting.${output_image##*.}"
    convert "$input_image" \
        -colorspace Gray \
        -normalize \
        -contrast-stretch 1%x2% \
        -sharpen 0x1 \
        -threshold 50% \
        -morphology Close Diamond:1 \
        "$handwriting_image"
}

# Function to run Tesseract handwriting OCR fallback
run_tesseract_handwriting() {
    local image_path="$1"
    local output_base="$2"
    local combined_text_var="$3"
    
    # Get the handwriting-optimized image
    local handwriting_image="${image_path%.*}_handwriting.${image_path##*.}"
    
    if [ -f "$handwriting_image" ]; then
        log_message "Running Tesseract handwriting OCR on $handwriting_image"
        
        # Multiple Tesseract configurations optimized for handwriting
        local hw_output1="$output_base.hw1.txt"
        local hw_output2="$output_base.hw2.txt"
        local hw_output3="$output_base.hw3.txt"
        
        # Configuration 1: Single text block, preserve whitespace
        tesseract "$handwriting_image" "${hw_output1%.*}" -l eng --oem 1 --psm 6 \
            -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\ .,!?-:;\"\' 2>/dev/null
        
        # Configuration 2: Single word mode for scattered handwriting
        tesseract "$handwriting_image" "${hw_output2%.*}" -l eng --oem 1 --psm 8 \
            -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\ .,!?-:;\"\' 2>/dev/null
        
        # Configuration 3: Treat as single character (for very poor quality)
        tesseract "$handwriting_image" "${hw_output3%.*}" -l eng --oem 1 --psm 10 2>/dev/null
        
        # Combine handwriting results
        local hw_combined=""
        if [ -f "$hw_output1" ] && [ -s "$hw_output1" ]; then
            hw_combined="$hw_combined\n--- Tesseract Handwriting (Block Mode) ---\n$(cat "$hw_output1")"
            rm "$hw_output1"
        fi
        if [ -f "$hw_output2" ] && [ -s "$hw_output2" ]; then
            hw_combined="$hw_combined\n--- Tesseract Handwriting (Word Mode) ---\n$(cat "$hw_output2")"
            rm "$hw_output2"
        fi
        if [ -f "$hw_output3" ] && [ -s "$hw_output3" ]; then
            hw_combined="$hw_combined\n--- Tesseract Handwriting (Character Mode) ---\n$(cat "$hw_output3")"
            rm "$hw_output3"
        fi
        
        if [ -n "$hw_combined" ]; then
            # Use eval to update the combined_text variable in the calling function
            eval "$combined_text_var=\"\$$combined_text_var\\n\\n=== TESSERACT HANDWRITING OCR ===\$hw_combined\""
        fi
    fi
}

run_ocr() {
    local image_path="$1"
    local output_base="$2"
    local engines="$3"
    
    log_message "Running EasyOCR for both handwriting and printed text on $image_path"
    
    # Run EasyOCR wrapper that handles both printed and handwritten text
    if python3 "$SCRIPT_DIR/easyocr_wrapper.py" "$image_path" "$output_base.easyocr.txt" 2>/dev/null; then
        log_message "EasyOCR completed successfully"
        
        # EasyOCR wrapper already creates beautifully formatted output
        # Just rename it to the expected combined output file
        if [ -f "$output_base.easyocr.txt" ]; then
            mv "$output_base.easyocr.txt" "$output_base.combined.txt"
        else
            echo "" > "$output_base.combined.txt"
        fi
    else
        log_message "ERROR: EasyOCR failed completely"
        echo "EasyOCR processing failed" > "$output_base.combined.txt"
    fi

}

# Function to process a single PDF
process_pdf() {
    local pdf_path="$1"
    local pdf_name=$(basename "$pdf_path" .pdf)
    local temp_prefix="$TEMP_DIR/${pdf_name}"
    
    log_message "Processing PDF: $pdf_path"
    
    # Convert PDF to PNG images
    log_message "Converting PDF to images using pdftoppm"
    if ! pdftoppm -png "$pdf_path" "$temp_prefix" 2>/dev/null; then
        log_message "ERROR: Failed to convert PDF $pdf_path to images"
        return 1
    fi
    
    # Find all generated PNG files
    local png_files=("$temp_prefix"*.png)
    if [ ${#png_files[@]} -eq 0 ] || [ ! -f "${png_files[0]}" ]; then
        log_message "ERROR: No PNG files generated from $pdf_path"
        return 1
    fi
    
    local final_text=""
    local page_num=1
    
    # Process each page image
    for png_file in "${png_files[@]}"; do
        if [ -f "$png_file" ]; then
            log_message "Processing page $page_num: $png_file"
            
            # Preprocess the image
            local processed_image="${png_file%.*}_processed.png"
            preprocess_image "$png_file" "$processed_image"
            
            # Determine best OCR engines for this image
            local ocr_engines=$(determine_ocr_engines)
            
            # Run OCR
            local ocr_output_base="${png_file%.*}_ocr"
            run_ocr "$processed_image" "$ocr_output_base" "$ocr_engines"
            
            # Add page results to final text
            if [ -f "$ocr_output_base.combined.txt" ]; then
                final_text="$final_text\n\n=== PAGE $page_num ===\n"
                final_text="$final_text$(cat "$ocr_output_base.combined.txt")"
                rm "$ocr_output_base.combined.txt"
            fi
            
            # Clean up temporary files
            rm -f "$png_file" "$processed_image"
            
            ((page_num++))
        fi
    done
    
    # Save final combined text output
    local output_file="$OUTPUT_DIR/${pdf_name}.txt"
    echo -e "$final_text" > "$output_file"
    log_message "Saved OCR output to: $output_file"
    
    # Move original PDF to used directory
    mv "$pdf_path" "$USED_DIR/"
    log_message "Moved original PDF to: $USED_DIR/$(basename "$pdf_path")"
    
    log_message "Successfully processed: $pdf_path"
    return 0
}

# Function to process all PDFs in raw_pdfs directory
process_all_pdfs() {
    local pdf_count=0
    local success_count=0
    local error_count=0
    
    log_message "Starting PDF processing batch"
    
    # Process all PDF files in raw_pdfs directory
    for pdf_file in "$RAW_DIR"/*.pdf; do
        # Check if glob matched any files
        if [ ! -f "$pdf_file" ]; then
            log_message "No PDF files found in $RAW_DIR"
            break
        fi
        
        ((pdf_count++))
        
        # Process the PDF with error handling
        if process_pdf "$pdf_file"; then
            ((success_count++))
        else
            ((error_count++))
            log_message "ERROR: Failed to process $pdf_file"
        fi
    done
    
    log_message "Batch complete: $pdf_count total, $success_count successful, $error_count errors"
    
    # Clean up any remaining temporary files
    rm -f "$TEMP_DIR"/*
}

# Function to monitor directory and process new PDFs
monitor_and_process() {
    log_message "Starting PDF monitoring service"
    
    while true; do
        # Check for new PDFs
        if ls "$RAW_DIR"/*.pdf 1> /dev/null 2>&1; then
            log_message "New PDF files detected, starting processing"
            process_all_pdfs
        fi
        
        # Wait before checking again (adjust interval as needed)
        sleep 10
    done
}

# Function to run eScriptorium batch processing (optional advanced feature)
run_escriptorium_batch() {
    local pdf_name="$1"
    local temp_prefix="$2"
    
    if command -v escriptorium &> /dev/null; then
        log_message "Running eScriptorium batch processing for $pdf_name"
        
        # Create a batch configuration for eScriptorium
        local batch_config="$TEMP_DIR/${pdf_name}_batch.json"
        cat > "$batch_config" << EOF
{
    "images": ["${temp_prefix}*.png"],
    "output_format": "txt",
    "segmentation": true,
    "ocr_engine": "kraken",
    "output_dir": "$TEMP_DIR"
}
EOF
        
        # Run eScriptorium batch processing
        if escriptorium batch --config "$batch_config" 2>/dev/null; then
            log_message "eScriptorium batch processing completed for $pdf_name"
            return 0
        else
            log_message "WARNING: eScriptorium batch processing failed for $pdf_name"
            return 1
        fi
    else
        log_message "WARNING: eScriptorium not found, skipping advanced processing"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-process}" in
        "monitor")
            monitor_and_process
            ;;
        "process")
            process_all_pdfs
            ;;
        "help")
            echo "Usage: $0 [monitor|process|help]"
            echo "  monitor  - Continuously monitor raw_pdfs/ for new files"
            echo "  process  - Process all PDFs in raw_pdfs/ once"
            echo "  help     - Show this help message"
            ;;
        *)
            echo "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
