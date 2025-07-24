# Installation Guide

## Quick Setup

### 1. Core Dependencies (Required)
These are needed for basic PDF processing:

```bash
# macOS with Homebrew
brew install poppler imagemagick tesseract

# Verify installation
pdftoppm -h
convert -version
tesseract --version
```

### 2. Check Installation Status
```bash
./run.sh setup
```

## Handwriting OCR Setup

### Option 1: EasyOCR (Recommended)
Simple installation with good handwriting support:

```bash
# Create virtual environment
python3 -m venv ocr_env
source ocr_env/bin/activate
pip install easyocr

# Test
python3 -c "import easyocr; print('EasyOCR installed successfully')"
```

### Option 2: Using pipx (Isolated)
```bash
# Install pipx
brew install pipx
pipx ensurepath

# Install OCR tools
pipx install easyocr
pipx install paddlepaddle
pipx install paddleocr
```

### Option 3: Advanced Tools (Kraken, Calamari)
For professional manuscript processing:

```bash
# Create clean environment
python3 -m venv handwriting_env
source handwriting_env/bin/activate

# Install with specific versions to avoid conflicts
pip install torch==1.10.0
pip install kraken
pip install calamari-ocr
```

### Option 4: Docker (Most Reliable)
```bash
# Pull containers
docker pull paddlepaddle/paddle:latest
docker pull kraken-ocr/kraken

# Use in pipeline (automatically detected)
```

## Troubleshooting

### Python Environment Issues
```bash
# Reset environment
rm -rf ocr_env
python3 -m venv ocr_env
source ocr_env/bin/activate
pip install --upgrade pip
pip install easyocr
```

### Permission Issues
```bash
# Fix script permissions
chmod +x run.sh
chmod +x scripts/*.sh
```

### Dependency Conflicts
```bash
# Use system packages instead
brew install tesseract-lang
brew install imagemagick
```

## Verification

After installation, verify everything works:

```bash
./run.sh setup    # Check dependencies
./run.sh status   # Check pipeline status
./run.sh test     # Run test processing
```
