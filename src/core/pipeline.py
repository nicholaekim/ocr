"""
Simplified PDF Metadata Extraction Pipeline
Core functionality without heavy dependencies (OCR, Google Sheets)
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from jsonschema import validate, ValidationError
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Container for pipeline processing results"""
    data: Dict[str, Any]
    warnings: List[str]
    success: bool
    stage: str

# OCR functionality removed to reduce dependencies

class TextPreprocessor:
    """Handles text preprocessing and segmentation"""
    
    @staticmethod
    def clean_and_segment(raw_text: str) -> List[str]:
        """Clean whitespace and segment text into logical parts"""
        try:
            # Clean whitespace and remove OCR artifacts
            text = raw_text.strip().replace("\n\n", "\n")
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)  # Remove OCR artifacts
            
            # Split into logical segments (paragraphs)
            segments = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 20]
            
            # If no good segments, split by sentences
            if not segments:
                sentences = re.split(r'[.!?]+', text)
                segments = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            return segments[:10]  # Limit to first 10 segments for processing
        except Exception as e:
            logger.error(f"Text preprocessing failed: {str(e)}")
            return [raw_text[:1000]]  # Fallback to first 1000 chars

class MetadataExtractor:
    """Handles LLM-based metadata extraction"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate"):
        self.ollama_url = ollama_url
    
    def _query_ollama(self, prompt: str, model: str = "llama3.2") -> str:
        """Query Ollama API"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get('response', '')
        except Exception as e:
            logger.error(f"Ollama query failed: {str(e)}")
            return ""
    
    def extract_title(self, segments: List[str]) -> str:
        """Extract document title (multilingual)"""
        text = '\n'.join(segments[:3])  # Use first 3 segments
        prompt = f"""You are a multilingual metadata bot that understands ALL languages.
From the following text segment, extract ONLY the document's title.
The text may be in Spanish, Portuguese, English, or any other language.
Return just the title in its original language, nothing else. If uncertain, return blank.

Text:
{text}

Title:"""
        return self._query_ollama(prompt).strip()
    
    def extract_date(self, segments: List[str], target_date_range: str = None) -> str:
        """Extract publication date with optional target date range (multilingual)"""
        text = '\n'.join(segments[:5])  # Use first 5 segments
        
        base_prompt = "You are a multilingual metadata bot that understands ALL languages.\nFrom the following text, find the most likely publication date.\nThe text may be in Spanish (e.g., 'junio 1979', 'marzo de 1978'), Portuguese, English, or any other language."
        
        if target_date_range:
            base_prompt += f"\n\nIMPORTANT: Look specifically for dates around {target_date_range}. This document should contain dates from this time period."
        
        prompt = f"""{base_prompt}
Return the date in a clear format (e.g., 'June 1979', 'March 1978'). If no date is present, return blank.

Text:
{text}

Date:"""
        return self._query_ollama(prompt).strip()
    
    def extract_description(self, segments: List[str], user_preferences: dict = None) -> str:
        """Extract document description with user fine-tuning (multilingual)"""
        text = '\n'.join(segments)
        
        # Build prompt with user preferences and multilingual support
        base_prompt = "You are a multilingual metadata bot that understands ALL languages.\nExtract a brief description that summarizes the entire document.\nThe text may be in Spanish, Portuguese, English, or any other language.\nProvide the description in English for consistency."
        
        if user_preferences and "description_style" in user_preferences:
            style_guide = user_preferences["description_style"]
            base_prompt += f"\n\nUser preferences: {style_guide}"
        
        if user_preferences and "description_examples" in user_preferences:
            examples = user_preferences["description_examples"]
            base_prompt += f"\n\nExamples of good descriptions: {examples}"
        
        prompt = f"""{base_prompt}

Text:
{text}

Description:"""
        return self._query_ollama(prompt).strip()
    
    def extract_volume_issue(self, segments: List[str]) -> str:
        """Extract volume and issue information (multilingual)"""
        text = '\n'.join(segments[:3])  # Use first 3 segments
        prompt = f"""You are a multilingual metadata bot that understands ALL languages.
From the text below, extract volume and issue information.
The text may be in Spanish (e.g., "Volumen 5, Número 2", "Tomo 12"), Portuguese (e.g., "Volume 5, Número 2"), English (e.g., "Vol. 5, No. 2"), or any other language.
Return the volume/issue info in a clear format (e.g., "Vol. 5, No. 2"). If none found, return blank.

Text:
{text}

Volume/Issue:"""
        return self._query_ollama(prompt).strip()

class MetadataValidator:
    """Validates extracted metadata"""
    
    SCHEMA = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "pub_date": {"type": "string"},
            "description": {"type": "string"},
            "volume_issue": {"type": "string"}
        },
        "required": ["title", "description"]
    }
    
    @classmethod
    def validate_metadata(cls, title: str, pub_date: str, description: str, volume_issue: str) -> PipelineResult:
        """Validate extracted metadata and return warnings"""
        warnings = []
        
        # Check title
        if not title or len(title) < 3:
            warnings.append("Title missing or too short")
        elif len(title) > 200:
            warnings.append("Title unusually long - may be incorrect")
        
        # Check date format
        if pub_date and not re.search(r'\b(19|20)\d{2}\b', pub_date):
            warnings.append("Date format unexpected - no 4-digit year found")
        
        # Check description
        if not description or len(description) < 10:
            warnings.append("Description missing or too short")
        elif len(description) > 1000:
            warnings.append("Description unusually long - may include extra content")
        
        # JSON schema validation
        data = {
            "title": title,
            "pub_date": pub_date,
            "description": description,
            "volume_issue": volume_issue
        }
        
        try:
            validate(data, cls.SCHEMA)
        except ValidationError as e:
            warnings.append(f"Schema validation error: {e.message}")
        
        return PipelineResult(
            data=data,
            warnings=warnings,
            success=len(warnings) == 0,
            stage="validation"
        )

# Google Sheets functionality removed to reduce dependencies

class PDFMetadataPipeline:
    """Main pipeline orchestrator with fine-tuning capabilities"""
    
    def __init__(self, user_preferences=None):
        # Initialize core components with user preferences
        self.preprocessor = TextPreprocessor()
        self.extractor = MetadataExtractor()
        self.validator = MetadataValidator()
        self.user_preferences = user_preferences or {}
    
    def process_pdf(self, pdf_text: str, target_date_range: str = None) -> PipelineResult:
        """Process a PDF through the simplified pipeline"""
        try:
            # Step 1: Preprocess text
            logger.info("Preprocessing text...")
            segments = self.preprocessor.clean_and_segment(pdf_text)
            
            if not segments:
                return PipelineResult(
                    data={},
                    warnings=["No text segments found after preprocessing"],
                    success=False,
                    stage="preprocessing"
                )
            
            # Step 2: Extract metadata using LLM with user preferences
            logger.info("Extracting metadata...")
            title = self.extractor.extract_title(segments)
            pub_date = self.extractor.extract_date(segments, target_date_range)
            description = self.extractor.extract_description(segments, self.user_preferences)
            volume_issue = self.extractor.extract_volume_issue(segments)
            
            # Step 3: Validate metadata
            logger.info("Validating metadata...")
            validation_result = self.validator.validate_metadata(title, pub_date, description, volume_issue)
            
            # Step 4: HITL Review (if warnings exist)
            if validation_result.warnings:
                logger.warning(f"Validation warnings: {validation_result.warnings}")
                # Log warnings for human review
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            return PipelineResult(
                data={},
                warnings=[f"Pipeline error: {str(e)}"],
                success=False,
                stage="pipeline"
            )
