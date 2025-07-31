#!/usr/bin/env python3
"""
Launcher script for the Interactive Data Checker
This script maintains backward compatibility while using the new organized folder structure
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the actual data checker
from utils.data_checker import InteractiveDataChecker

if __name__ == "__main__":
    # Allow custom raw_data folder via command line
    if len(sys.argv) > 1:
        raw_data_folder = sys.argv[1]
    else:
        raw_data_folder = None  # Will use default data/raw folder
    
    checker = InteractiveDataChecker(raw_data_folder)
    
    try:
        checker.run_batch_processing()
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        print("💾 All feedback has been saved to memory")
