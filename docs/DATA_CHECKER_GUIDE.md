# Interactive Data Checker Guide

## 🎯 What This Does

The `data_checker.py` script processes all PDFs in your `raw_data` folder and lets you:
- **Review** extracted metadata (title, date, abstract, volume/issue)
- **Correct** any mistakes interactively
- **Teach** the system what you want - it remembers your corrections
- **Improve** over time - future runs get smarter based on your feedback

## 🚀 How to Use

### Step 1: Add Your PDFs
```bash
# Put all your PDF files in the raw_data folder
cp your_pdfs/*.pdf raw_data/
```

### Step 2: Run the Data Checker
```bash
python3 data_checker.py
```

### Step 3: Interactive Review Process
For each PDF, you'll see:
1. **Extracted metadata** displayed clearly
2. **Memory suggestions** (if the system learned from previous corrections)
3. **Options to:**
   - `c` = Correct any field
   - `s` = Skip to next file  
   - `q` = Quit processing

### Step 4: Make Corrections
When you choose `c` to correct:
1. Select which field to fix (1-4)
2. Enter the correct value
3. The system **remembers** your correction for future files

## 🧠 Learning System

### How It Learns
- **Remembers corrections:** If you fix "Vol 5" to "Volume 5", it learns this pattern
- **Suggests improvements:** Next time it sees "Vol 6", it suggests "Volume 6"
- **Builds patterns:** Learns your preferences for titles, dates, abstracts, etc.

### Memory File
- All learning is saved in `feedback_memory.json`
- Contains your correction patterns and preferences
- Gets smarter with each correction you make

## 📊 Example Session

```
🚀 PDF Batch Data Checker
==================================================
📁 Found 5 PDF files in 'raw_data'
🧠 Memory: 12 corrections, 8 patterns learned

============================================================
📄 FILE: research_paper.pdf
============================================================

🔹 Title:
   Effects of Climate Change on Agriculture
   💡 Suggestion (from memory): Effects of Climate Change on Agricultural Productivity

🔹 Date:
   March 2023

🔹 Abstract:
   This study examines how rising temperatures affect crop yields...

🔹 Volume/Issue:
   Vol. 15, No. 3
   💡 Suggestion (from memory): Volume 15, Issue 3

────────────────────────────────────────────────────────────
🔧 FEEDBACK & CORRECTIONS
Enter 'c' to correct a field, 's' to skip, 'q' to quit

Your choice (c/s/q): c

Which field would you like to correct?
1. Title: Effects of Climate Change on Agriculture
2. Date: March 2023
3. Abstract: This study examines how rising temperatures...
4. Volume/Issue: Vol. 15, No. 3

Enter field number (1-4): 4
Current Volume/Issue: Vol. 15, No. 3
Enter correct Volume/Issue: Volume 15, Issue 3
✅ Volume/Issue updated and saved to memory!
✅ Learned: volume_issue correction saved to memory
```

## 📁 File Structure

```
ocr3.0/
├── data_checker.py          # Main interactive script
├── raw_data/               # Put your PDFs here
│   ├── paper1.pdf
│   ├── paper2.pdf
│   └── ...
├── feedback_memory.json    # Learning/memory file (auto-created)
└── batch_results_*.json    # Processing results (auto-created)
```

## 🎛️ Advanced Usage

### Custom Raw Data Folder
```bash
python3 data_checker.py /path/to/your/pdfs
```

### View Memory Stats
The script shows you:
- How many corrections you've made
- How many patterns it has learned
- Which fields you've corrected most

### Batch Results
After processing, you get:
- JSON file with all extracted metadata
- Summary of corrections made
- Updated memory for future runs

## 💡 Pro Tips

1. **Start small:** Process a few PDFs first to train the system
2. **Be consistent:** Use the same format for corrections (helps learning)
3. **Review suggestions:** The system gets better at suggesting corrections
4. **Backup memory:** Save `feedback_memory.json` - it contains all your training

## 🔧 Troubleshooting

- **No PDFs found:** Make sure PDFs are in the `raw_data` folder
- **Processing errors:** Check that PDFs aren't corrupted or password-protected
- **Memory issues:** Delete `feedback_memory.json` to reset learning (if needed)

The system learns YOUR preferences and gets better with each correction you make!
