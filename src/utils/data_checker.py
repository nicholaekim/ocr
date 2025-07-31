#!/usr/bin/env python3
"""
Interactive Data Checker for PDF Batch Processing
Processes all PDFs in raw_data folder with user feedback and learning
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import PyPDF2
import io

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.core.pipeline import PDFMetadataPipeline, PipelineResult

class FeedbackMemory:
    """Manages user feedback and fine-tuning preferences"""
    
    def __init__(self, memory_file=None):
        if memory_file is None:
            # Use data folder in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            memory_file = os.path.join(project_root, "data", "feedback_memory.json")
        self.memory_file = memory_file
        self.feedback_data = self.load_memory()
    
    def load_memory(self):
        """Load existing feedback memory"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "corrections": [],
            "patterns": {},
            "user_preferences": {
                "description_style": "",
                "description_examples": [],
                "title_format": "",
                "date_format": "",
                "volume_format": ""
            },
            "fine_tuning_prompts": {
                "title": "",
                "date": "",
                "description": "",
                "volume_issue": ""
            },
            "last_updated": None
        }
    
    def save_memory(self):
        """Save feedback memory to file"""
        self.feedback_data["last_updated"] = datetime.now().isoformat()
        with open(self.memory_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
    
    def add_correction(self, filename, field, original_value, corrected_value, context=""):
        """Record a user correction and update fine-tuning"""
        correction = {
            "filename": filename,
            "field": field,
            "original": original_value,
            "corrected": corrected_value,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_data["corrections"].append(correction)
        
        # Update patterns
        if field not in self.feedback_data["patterns"]:
            self.feedback_data["patterns"][field] = {}
        
        pattern_key = original_value.lower()[:50] if original_value else "empty"
        self.feedback_data["patterns"][field][pattern_key] = corrected_value
        
        # Update fine-tuning preferences based on corrections
        self.update_fine_tuning_preferences(field, original_value, corrected_value)
        
        self.save_memory()
        print(f"✅ Fine-tuned: {field} correction learned and will guide future extractions")
    
    def update_fine_tuning_preferences(self, field, original_value, corrected_value):
        """Update fine-tuning preferences based on user corrections"""
        if field == "description":
            # Learn description style preferences
            if len(corrected_value) < 50:
                self.feedback_data["user_preferences"]["description_style"] = "Keep descriptions brief and concise"
            elif len(corrected_value) > 200:
                self.feedback_data["user_preferences"]["description_style"] = "Provide detailed comprehensive descriptions"
            
            # Add to examples
            if corrected_value not in self.feedback_data["user_preferences"]["description_examples"]:
                self.feedback_data["user_preferences"]["description_examples"].append(corrected_value)
                # Keep only last 5 examples
                if len(self.feedback_data["user_preferences"]["description_examples"]) > 5:
                    self.feedback_data["user_preferences"]["description_examples"].pop(0)
        
        elif field == "title":
            # Learn title format preferences
            if corrected_value.isupper():
                self.feedback_data["user_preferences"]["title_format"] = "Prefer uppercase titles"
            elif corrected_value.istitle():
                self.feedback_data["user_preferences"]["title_format"] = "Prefer title case"
        
        elif field == "volume_issue":
            # Learn volume format preferences
            if "Volume" in corrected_value and "Issue" in corrected_value:
                self.feedback_data["user_preferences"]["volume_format"] = "Use 'Volume X, Issue Y' format"
            elif "Vol." in corrected_value and "No." in corrected_value:
                self.feedback_data["user_preferences"]["volume_format"] = "Use 'Vol. X, No. Y' format"
    
    def get_user_preferences(self):
        """Get current user preferences for fine-tuning"""
        return self.feedback_data["user_preferences"]
    
    def get_suggestion(self, field, value):
        """Get suggestion based on previous corrections"""
        if field in self.feedback_data["patterns"]:
            pattern_key = value.lower()[:50] if value else "empty"
            if pattern_key in self.feedback_data["patterns"][field]:
                return self.feedback_data["patterns"][field][pattern_key]
        return None
    
    def get_stats(self):
        """Get feedback statistics"""
        total_corrections = len(self.feedback_data["corrections"])
        fields_corrected = set(c["field"] for c in self.feedback_data["corrections"])
        return {
            "total_corrections": total_corrections,
            "fields_corrected": list(fields_corrected),
            "patterns_learned": sum(len(patterns) for patterns in self.feedback_data["patterns"].values())
        }

class InteractiveDataChecker:
    """Main interactive data checker class"""
    
    def __init__(self, raw_data_folder=None):
        if raw_data_folder is None:
            # Use data/raw folder in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            raw_data_folder = os.path.join(project_root, "data", "raw")
        self.raw_data_folder = raw_data_folder
        self.memory = FeedbackMemory()
        # Initialize pipeline with user preferences for fine-tuning
        user_preferences = self.memory.get_user_preferences()
        self.pipeline = PDFMetadataPipeline(user_preferences)
        self.processed_files = []
        self.results = []
        
        # Create raw_data folder if it doesn't exist
        os.makedirs(raw_data_folder, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def find_pdf_files(self):
        """Find all PDF files in raw_data folder"""
        pdf_files = []
        for root, dirs, files in os.walk(self.raw_data_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return sorted(pdf_files)
    
    def display_metadata(self, metadata, filename):
        """Display extracted metadata in a nice format"""
        print(f"\n{'='*60}")
        print(f"📄 FILE: {filename}")
        print(f"{'='*60}")
        
        fields = [
            ("Title", "title"),
            ("Date", "pub_date"), 
            ("Description", "description"),
            ("Volume/Issue", "volume_issue")
        ]
        
        for display_name, field_key in fields:
            value = metadata.get(field_key, "Not found")
            suggestion = self.memory.get_suggestion(field_key, value)
            
            print(f"\n🔹 {display_name}:")
            print(f"   {value}")
            
            if suggestion and suggestion != value:
                print(f"   💡 Suggestion (from memory): {suggestion}")
    
    def get_user_feedback(self, metadata, filename):
        """Get user feedback and corrections"""
        print(f"\n{'─'*60}")
        print("🔧 FEEDBACK & CORRECTIONS")
        print("Enter 'c' to correct a field, 's' to skip, 'q' to quit")
        
        while True:
            choice = input("\nYour choice (c/s/q): ").lower().strip()
            
            if choice == 'q':
                return False  # Quit
            elif choice == 's':
                return True   # Skip to next file
            elif choice == 'c':
                self.handle_corrections(metadata, filename)
                return True
            else:
                print("❌ Invalid choice. Please enter 'c', 's', or 'q'")
    
    def handle_corrections(self, metadata, filename):
        """Handle user corrections"""
        fields = {
            "1": ("title", "Title"),
            "2": ("pub_date", "Date"), 
            "3": ("description", "Description"),
            "4": ("volume_issue", "Volume/Issue")
        }
        
        print("\nWhich field would you like to correct?")
        for key, (field_key, display_name) in fields.items():
            current_value = metadata.get(field_key, "Not found")
            print(f"{key}. {display_name}: {current_value[:100]}...")
        
        field_choice = input("\nEnter field number (1-4): ").strip()
        
        if field_choice in fields:
            field_key, display_name = fields[field_choice]
            current_value = metadata.get(field_key, "")
            
            print(f"\nCurrent {display_name}: {current_value}")
            new_value = input(f"Enter correct {display_name} (or press Enter to skip): ").strip()
            
            if new_value:
                # Update metadata
                metadata[field_key] = new_value
                
                # Save to memory and update fine-tuning
                context = f"File: {filename}"
                self.memory.add_correction(filename, field_key, current_value, new_value, context)
                
                # Refresh pipeline with updated preferences
                user_preferences = self.memory.get_user_preferences()
                self.pipeline = PDFMetadataPipeline(user_preferences)
                
                print(f"✅ {display_name} updated and fine-tuning applied!")
            else:
                print("⏭️  Skipped correction")
        else:
            print("❌ Invalid field number")
    
    def process_single_file(self, file_path):
        """Process a single PDF file"""
        filename = os.path.basename(file_path)
        print(f"\n🔄 Processing: {filename}")
        
        # Extract text
        text = self.extract_text_from_pdf(file_path)
        if text.startswith("Error"):
            print(f"❌ Failed to extract text: {text}")
            return None
        
        # Process through pipeline with target date range
        try:
            target_date = getattr(self, 'target_date_range', None)
            result = self.pipeline.process_pdf(text, target_date)
            
            if result.success:
                metadata = result.data.copy()
                
                # Apply memory suggestions
                for field_key in ["title", "pub_date", "abstract", "volume_issue"]:
                    current_value = metadata.get(field_key, "")
                    suggestion = self.memory.get_suggestion(field_key, current_value)
                    if suggestion and suggestion != current_value:
                        metadata[f"{field_key}_suggested"] = suggestion
                
                return {
                    "filename": filename,
                    "file_path": file_path,
                    "metadata": metadata,
                    "warnings": result.warnings,
                    "text_length": len(text)
                }
            else:
                print(f"❌ Pipeline processing failed: {'; '.join(result.warnings)}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            return None
    
    def get_target_date_range(self):
        """Get target date range from user"""
        print("\n📅 DATE RANGE SPECIFICATION")
        print("=" * 50)
        print("Your files are organized by date ranges (e.g., 1977-78, 1979-80)")
        print("Specify the date range you want the system to look for in documents.")
        print("")
        
        while True:
            date_input = input("Enter target date range (e.g., '1977-78', '1979', 'June 1979'): ").strip()
            
            if not date_input:
                print("❌ Please enter a date range")
                continue
            
            # Confirm with user
            print(f"\n🎯 Target date range: {date_input}")
            confirm = input("Is this correct? (y/n): ").lower().strip()
            
            if confirm in ['y', 'yes']:
                return date_input
            elif confirm in ['n', 'no']:
                continue
            else:
                print("❌ Please enter 'y' or 'n'")
    
    def run_batch_processing(self):
        """Run the main batch processing loop"""
        print("🚀 PDF Batch Data Checker")
        print("=" * 50)
        
        # Get target date range from user
        target_date_range = self.get_target_date_range()
        
        # Store target date range for LLM extraction
        self.target_date_range = target_date_range
        
        # Find PDF files
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            print(f"❌ No PDF files found in '{self.raw_data_folder}' folder")
            print(f"💡 Add some PDF files to the '{self.raw_data_folder}' folder and try again")
            return
        
        print(f"📁 Found {len(pdf_files)} PDF files in '{self.raw_data_folder}'")
        
        # Show memory stats
        stats = self.memory.get_stats()
        if stats["total_corrections"] > 0:
            print(f"🧠 Memory: {stats['total_corrections']} corrections, {stats['patterns_learned']} patterns learned")
        
        # Show target date range
        print(f"🎯 Target date range: {target_date_range}")
        
        print("\n" + "="*60)
        
        # Process each file
        for i, file_path in enumerate(pdf_files, 1):
            print(f"\n📊 Progress: {i}/{len(pdf_files)}")
            
            result = self.process_single_file(file_path)
            if result:
                self.results.append(result)
                self.display_metadata(result["metadata"], result["filename"])
                
                # Get user feedback
                continue_processing = self.get_user_feedback(result["metadata"], result["filename"])
                if not continue_processing:
                    break
        
        # Final summary
        self.show_summary()
    
    def show_summary(self):
        """Show processing summary"""
        print(f"\n{'='*60}")
        print("📊 PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Files processed: {len(self.results)}")
        
        stats = self.memory.get_stats()
        print(f"🧠 Total corrections made: {stats['total_corrections']}")
        print(f"🎯 Patterns learned: {stats['patterns_learned']}")
        
        if stats["fields_corrected"]:
            print(f"📝 Fields corrected: {', '.join(stats['fields_corrected'])}")
        
        # Save results
        if self.results:
            output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"💾 Results saved to: {output_file}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        raw_data_folder = sys.argv[1]
    else:
        raw_data_folder = "raw_data"
    
    checker = InteractiveDataChecker(raw_data_folder)
    
    try:
        checker.run_batch_processing()
    except KeyboardInterrupt:
        print("\n\n⏹️  Processing interrupted by user")
        print("💾 All feedback has been saved to memory")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
