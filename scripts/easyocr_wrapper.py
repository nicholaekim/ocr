#!/usr/bin/env python3
"""
EasyOCR Wrapper for Both Handwriting and Printed Text Recognition
Replaces PaddleOCR as the primary OCR solution due to stability issues
Configured for optimal performance with robust image handling and beautiful output formatting
"""

import sys
import os
import easyocr
import argparse
import cv2
import numpy as np
from PIL import Image

def preprocess_image_for_easyocr(image_path):
    """
    Preprocess image to ensure compatibility with EasyOCR/OpenCV
    """
    try:
        # Try to load with PIL first (more robust)
        pil_image = Image.open(image_path)
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert PIL to numpy array
        image_array = np.array(pil_image)
        
        # Ensure the image is in the correct format for OpenCV
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # RGB to BGR for OpenCV
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        elif len(image_array.shape) == 2:
            # Grayscale to BGR
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        
        # Ensure proper data type
        if image_array.dtype != np.uint8:
            # Normalize and convert to uint8
            if image_array.dtype == bool:
                image_array = image_array.astype(np.uint8) * 255
            else:
                image_array = ((image_array - image_array.min()) / 
                              (image_array.max() - image_array.min()) * 255).astype(np.uint8)
        
        return image_array
        
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        # Fallback: try direct OpenCV load
        try:
            image_array = cv2.imread(image_path)
            if image_array is not None:
                return image_array
        except:
            pass
        raise e

def classify_text_type(text, confidence):
    """Classify text as printed, handwritten, or mixed based on characteristics"""
    if confidence > 0.85 and len(text) > 5:
        return 'printed'
    elif confidence < 0.7 or len(text) <= 3:
        return 'handwritten'
    else:
        return 'mixed'

def save_formatted_results(results, output_path):
    """Save results with beautiful formatting like the enhanced OCR wrapper"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("📄 EASYOCR RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        # Classify and group results
        text_results = {
            'printed_text': [],
            'handwritten_text': [],
            'mixed_text': []
        }
        
        for item in results:
            if item['text'].strip() and item['confidence'] > 0.5:
                text_type = classify_text_type(item['text'], item['confidence'])
                text_results[f"{text_type}_text"].append(item)
        
        # Printed Text Section
        if text_results['printed_text']:
            f.write("🖨️  PRINTED TEXT\n")
            f.write("-" * 40 + "\n")
            for i, item in enumerate(text_results['printed_text'], 1):
                f.write(f"[{i:02d}] {item['text']}\n")
        
        # Handwritten Text Section
        if text_results['handwritten_text']:
            f.write("✍️  HANDWRITTEN TEXT\n")
            f.write("-" * 40 + "\n")
            for i, item in enumerate(text_results['handwritten_text'], 1):
                f.write(f"[{i:02d}] {item['text']}\n")
        
        # Mixed Text Section
        if text_results['mixed_text']:
            f.write("🔀 MIXED TEXT\n")
            f.write("-" * 40 + "\n")
            for i, item in enumerate(text_results['mixed_text'], 1):
                f.write(f"[{i:02d}] {item['text']}\n")
        
        # Summary
        total_items = len(text_results['printed_text']) + len(text_results['handwritten_text']) + len(text_results['mixed_text'])
        f.write("-" * 80 + "\n")
        f.write(f"📊 SUMMARY: {total_items} text segments extracted\n")
        f.write(f"   • Printed: {len(text_results['printed_text'])} segments\n")
        f.write(f"   • Handwritten: {len(text_results['handwritten_text'])} segments\n")
        f.write(f"   • Mixed: {len(text_results['mixed_text'])} segments\n")
        f.write(f"   • Engine: EasyOCR (unified detection)\n")
        f.write("=" * 80 + "\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python easyocr_wrapper.py <input_image> <output_file>", file=sys.stderr)
        sys.exit(1)
    
    input_image = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Check if input image exists
        if not os.path.exists(input_image):
            print(f"Error: Input image '{input_image}' not found", file=sys.stderr)
            sys.exit(1)
        
        print(f"Processing image with EasyOCR: {input_image}", file=sys.stderr)
        
        # Preprocess image to ensure compatibility
        processed_image = preprocess_image_for_easyocr(input_image)
        
        # Initialize EasyOCR reader with optimized settings for both handwriting and printed text
        reader = easyocr.Reader(
            ['en'], 
            gpu=False,  # Use CPU for stability
            verbose=False
        )
        
        # Run OCR with detailed results (including confidence and bounding boxes)
        results = reader.readtext(
            processed_image,
            detail=1,  # Return detailed results with confidence
            paragraph=False,  # Process individual text elements
            width_ths=0.7,  # Threshold for text width
            height_ths=0.7,  # Threshold for text height
            text_threshold=0.6,  # Text confidence threshold
            low_text=0.4,  # Low text threshold for detection
            link_threshold=0.4,  # Link threshold for text connection
            canvas_size=2560,  # Canvas size for processing
            mag_ratio=1.5  # Magnification ratio
        )
        
        # Process results into structured format
        processed_results = []
        for result in results:
            if len(result) >= 2:
                bbox, text, confidence = result[0], result[1], result[2]
                if text.strip() and confidence > 0.5:
                    processed_results.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox
                    })
        
        print(f"EasyOCR detected {len(processed_results)} text segments", file=sys.stderr)
        
        # Save formatted results
        save_formatted_results(processed_results, output_file)
        
        print(f"EasyOCR completed: results saved to {output_file}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error running EasyOCR: {e}", file=sys.stderr)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("📄 EASYOCR RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"❌ EasyOCR Error: {e}\n")
            f.write("=" * 80 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
