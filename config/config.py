"""
Configuration file for PDF Metadata Extraction Pipeline
"""

import os

# Pipeline Configuration
class PipelineConfig:
    # OCR Settings
    USE_OCR = os.getenv('USE_OCR', 'false').lower() == 'true'
    OCR_LANGUAGES = ['en']  # Add more languages as needed: ['en', 'es', 'fr']
    
    # Google Sheets Integration
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', None)
    GOOGLE_CREDENTIALS_FILE = 'credentials.json'
    
    # Ollama Settings
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "llama3.2"
    
    # Processing Settings
    MAX_TEXT_SEGMENTS = 10
    PDF_TO_IMAGE_DPI = 300
    
    # Validation Settings
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_ABSTRACT_LENGTH = 10
    MAX_ABSTRACT_LENGTH = 1000
    
    @classmethod
    def get_pipeline_settings(cls):
        """Get all pipeline settings as a dictionary"""
        return {
            'use_ocr': cls.USE_OCR,
            'ocr_languages': cls.OCR_LANGUAGES,
            'google_sheet_id': cls.GOOGLE_SHEET_ID,
            'ollama_url': cls.OLLAMA_API_URL,
            'ollama_model': cls.OLLAMA_MODEL,
            'max_segments': cls.MAX_TEXT_SEGMENTS,
            'pdf_dpi': cls.PDF_TO_IMAGE_DPI
        }
