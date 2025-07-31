from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import PyPDF2
import io
import os
import sys
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.core.pipeline import PDFMetadataPipeline, PipelineResult

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size for batch uploads

# Set up paths relative to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'uploads')
feedback_memory_path = os.path.join(project_root, 'data', 'feedback_memory.json')

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Load user preferences from fine-tuning system
def load_user_preferences():
    """Load user preferences from feedback memory"""
    try:
        if os.path.exists('feedback_memory.json'):
            with open('feedback_memory.json', 'r') as f:
                memory_data = json.load(f)
                return memory_data.get('user_preferences', {})
    except:
        pass
    return {}

# Initialize pipeline with fine-tuning preferences
user_preferences = load_user_preferences()
pipeline = PDFMetadataPipeline(user_preferences)

def refresh_pipeline_with_latest_preferences():
    """Refresh pipeline with latest fine-tuning preferences"""
    global pipeline
    user_preferences = load_user_preferences()
    pipeline = PDFMetadataPipeline(user_preferences)
    return user_preferences

# Global storage for processed PDFs metadata
processed_pdfs = {
    "session_id": str(uuid.uuid4()),
    "created_at": datetime.now().isoformat(),
    "total_documents": 0,
    "documents": []
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'Upload too large. Please try uploading fewer files at once or smaller PDFs. Current limit is 200MB total.'
    }), 413

def extract_text_from_pdf(file_stream):
    """Extract text content from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

# PDF to image conversion removed - no longer needed

def extract_metadata_from_text(text):
    """Extract structured metadata from PDF text using Ollama"""
    try:
        # Check if Ollama service is running
        health_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if health_response.status_code != 200:
            return {
                "date": "Ollama service unavailable",
                "title": "Ollama service unavailable",
                "description": "Ollama service unavailable",
                "volume_issue": "Ollama service unavailable",
                "error": "Ollama service is not responding"
            }
        
        prompt = f"""Analyze the following document text and extract these specific pieces of information in JSON format:

1. Date (publication date, issue date, or any relevant date)
2. Title (the EXACT main title of the document/article as it appears - do NOT summarize, just extract the literal title)
3. Description (brief summary or abstract, 2-3 sentences max)
4. Volume/Issue (volume number, issue number, or edition if available)

IMPORTANT: For the title, extract the EXACT title as written in the document. Do not paraphrase, summarize, or modify it. Look for the main heading, title page, or document header.

Document text:
{text[:3000]}...

Please respond with ONLY a JSON object in this exact format:
{{
  "date": "extracted date or 'Not found'",
  "title": "EXACT title as written in document or 'Not found'",
  "description": "brief description or 'Not found'",
  "volume_issue": "volume/issue info or 'Not found'"
}}"""
        
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        # Check if response is HTML (error page)
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            return {
                "date": "Ollama API error",
                "title": "Ollama API error",
                "description": "Ollama API error",
                "volume_issue": "Ollama API error",
                "error": f"Ollama returned HTML instead of JSON. Status: {response.status_code}"
            }
        
        response.raise_for_status()
        
        # Parse JSON response
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            return {
                "date": "JSON parse error",
                "title": "JSON parse error",
                "description": "JSON parse error",
                "volume_issue": "JSON parse error",
                "error": f"Failed to parse Ollama response as JSON: {str(e)}",
                "raw_response": response.text[:500]
            }
        
        ollama_response = result.get('response', '{}')
        
        # Try to parse JSON from the response
        try:
            # Find JSON in the response (in case there's extra text)
            start = ollama_response.find('{')
            end = ollama_response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = ollama_response[start:end]
                metadata = json.loads(json_str)
                return metadata
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback if JSON parsing fails
            return {
                "date": "Could not extract",
                "title": "Could not extract", 
                "description": "Could not extract",
                "volume_issue": "Could not extract",
                "error": f"Failed to parse metadata JSON: {str(e)}",
                "raw_response": ollama_response[:500]
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "date": "Connection error",
            "title": "Connection error",
            "description": "Connection error",
            "volume_issue": "Connection error",
            "error": "Cannot connect to Ollama service. Please ensure Ollama is running."
        }
    except requests.exceptions.Timeout:
        return {
            "date": "Timeout error",
            "title": "Timeout error",
            "description": "Timeout error",
            "volume_issue": "Timeout error",
            "error": "Ollama request timed out. The document may be too large or complex."
        }
    except Exception as e:
        return {
            "date": "Error during extraction",
            "title": "Error during extraction",
            "description": "Error during extraction", 
            "volume_issue": "Error during extraction",
            "error": f"Unexpected error: {str(e)}"
        }

def query_ollama(prompt, context=""):
    """Send query to Ollama model"""
    try:
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}" if context else prompt
        
        payload = {
            "model": "llama3.2",
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', 'No response received')
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}"
    except Exception as e:
        return f"Error processing request: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    pdf_context = data.get('pdf_context', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = query_ollama(message, pdf_context)
    return jsonify({'response': response})

@app.route('/upload', methods=['POST'])
def upload_file():
    global processed_pdfs
    
    # Refresh pipeline with latest fine-tuning preferences
    current_preferences = refresh_pipeline_with_latest_preferences()
    
    # Handle multiple files
    files = request.files.getlist('files')
    if not files or (len(files) == 1 and files[0].filename == ''):
        return jsonify({'error': 'No files provided'}), 400
    
    results = []
    errors = []
    
    for file in files:
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_stream = io.BytesIO(file.read())
                
                # Extract text from PDF
                text = extract_text_from_pdf(file_stream)
                
                # Process through simplified pipeline
                pipeline_result = pipeline.process_pdf(text)
                
                # Convert pipeline result to old format for compatibility
                if pipeline_result.success:
                    metadata = pipeline_result.data
                    # Add pipeline-specific information
                    metadata['pipeline_warnings'] = pipeline_result.warnings
                    metadata['processing_stage'] = pipeline_result.stage
                else:
                    metadata = {
                        "date": "Pipeline processing failed",
                        "title": "Pipeline processing failed", 
                        "description": "Pipeline processing failed",
                        "volume_issue": "Pipeline processing failed",
                        "error": f"Pipeline error: {'; '.join(pipeline_result.warnings)}",
                        "pipeline_warnings": pipeline_result.warnings,
                        "processing_stage": pipeline_result.stage
                    }
                
                # Create document entry
                document_entry = {
                    "id": str(uuid.uuid4()),
                    "filename": filename,
                    "processed_at": datetime.now().isoformat(),
                    "metadata": metadata,
                    "text_length": len(text),
                    "text_preview": text[:500] + "..." if len(text) > 500 else text
                }
                
                # Add to global storage
                processed_pdfs["documents"].append(document_entry)
                processed_pdfs["total_documents"] = len(processed_pdfs["documents"])
                processed_pdfs["last_updated"] = datetime.now().isoformat()
                
                results.append({
                    'filename': filename,
                    'metadata': metadata,
                    'document_id': document_entry["id"]
                })
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        else:
            errors.append(f"{file.filename}: Invalid file type")
    
    if not results and errors:
        return jsonify({'error': 'All files failed to process', 'details': errors}), 400
    
    return jsonify({
        'success': True,
        'processed_count': len(results),
        'total_documents': processed_pdfs["total_documents"],
        'results': results,
        'errors': errors if errors else None
    })

@app.route('/export-json', methods=['GET'])
def export_json():
    """Export all processed PDFs metadata as JSON file"""
    global processed_pdfs
    
    if processed_pdfs["total_documents"] == 0:
        return jsonify({'error': 'No documents have been processed yet'}), 400
    
    # Create a temporary file
    filename = f"pdf_metadata_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Write JSON data to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(processed_pdfs, f, indent=2, ensure_ascii=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/json')

@app.route('/get-all-documents', methods=['GET'])
def get_all_documents():
    """Get all processed documents metadata"""
    global processed_pdfs
    return jsonify(processed_pdfs)

@app.route('/clear-documents', methods=['POST'])
def clear_documents():
    """Clear all processed documents"""
    global processed_pdfs
    processed_pdfs = {
        "session_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "total_documents": 0,
        "documents": []
    }
    return jsonify({'success': True, 'message': 'All documents cleared'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
