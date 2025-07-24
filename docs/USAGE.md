# Usage Guide

## Quick Start

1. **Drop PDFs** into `raw_pdfs/` folder
2. **Run processing**: `./run.sh process`
3. **Get results** from `outputs/` folder

## Commands

### Basic Commands
```bash
./run.sh help          # Show all available commands
./run.sh status         # Check pipeline status
./run.sh setup          # Check dependencies
```

### Processing Commands
```bash
./run.sh process        # Process all PDFs once
./run.sh handwriting    # Enhanced handwriting processing
./run.sh monitor        # Continuous monitoring
```

### Maintenance Commands
```bash
./run.sh clean          # Clean up temp files and logs
./run.sh test           # Run tests and examples
./run.sh install-help   # Installation guidance
```

## Processing Modes

### Standard Processing
Best for documents with mostly printed text:
```bash
./run.sh process
```

**Features:**
- Tesseract OCR for printed text
- Basic image preprocessing
- Fast processing
- Good for typed documents

### Enhanced Handwriting Processing
Optimized for handwritten documents:
```bash
./run.sh handwriting
```

**Features:**
- Multiple preprocessing techniques
- Advanced Tesseract configurations
- Better handwriting recognition
- Slower but more thorough

### Continuous Monitoring
Automatically process new PDFs:
```bash
./run.sh monitor
```

**Features:**
- Watches `raw_pdfs/` folder
- Processes files as they appear
- Runs in background
- Press Ctrl+C to stop

## Output Format

Each PDF generates a text file with sections:

```
=== PAGE 1 ===

=== TESSERACT OUTPUT ===
[printed text content]

=== KRAKEN HTR OUTPUT ===
[handwriting content if available]

=== PAGE 2 ===
...
```

## File Management

- **Input**: `raw_pdfs/` - Drop PDF files here
- **Output**: `outputs/` - Text files appear here
- **Archive**: `used_pdfs/` - Processed PDFs moved here
- **Logs**: `logs/` - Processing logs and history
- **Temp**: `temp/` - Temporary files (auto-cleaned)

## Tips for Better Results

### For Handwriting Recognition
1. Use high-resolution scans (300+ DPI)
2. Ensure good contrast
3. Try the enhanced handwriting processor
4. Install specialized OCR tools (see INSTALLATION.md)

### For Mixed Documents
1. Use standard processing first
2. If handwriting is missed, try enhanced mode
3. Check logs for processing details

### For Batch Processing
1. Drop multiple PDFs in `raw_pdfs/`
2. Use `./run.sh process` for one-time batch
3. Use `./run.sh monitor` for ongoing processing

## Troubleshooting

### No Text Output
- Check if PDF is password-protected
- Verify image quality in original PDF
- Try enhanced handwriting mode

### Poor Recognition Quality
- Check original PDF resolution
- Install additional OCR engines
- Adjust preprocessing settings

### Processing Errors
- Check `logs/workflow.log` for details
- Verify dependencies with `./run.sh setup`
- Ensure sufficient disk space

## Advanced Usage

### Custom Processing
Modify scripts in `scripts/` folder for specific needs.

### Integration
Use individual scripts for integration with other systems:
```bash
scripts/pdf_processor.sh process
scripts/enhanced_handwriting_processor.sh process
```

### Monitoring Logs
```bash
tail -f logs/workflow.log    # Watch processing in real-time
```
