# 🚀 Quick Start - Run Notebook in 3 Minutes

## ⚡ Fastest Method

```bash
# 1. Check environment (OPTIONAL but recommended)
python3 tests/check_environment.py

# 2. Start Jupyter
jupyter notebook notebooks/document_assistant_demo.ipynb

# 3. In the browser that opens:
#    - Press: Shift + Enter on each cell
#    - Or: Menu "Cell" → "Run All"
```

**Done!** The notebook will run all tests automatically.

---

## 📋 Quick Checklist

Before running, verify:

```bash
# ✅ Python installed?
python3 --version
# Need: Python 3.8 or higher

# ✅ Dependencies installed?
pip install -r requirements.txt

# ✅ .env configured?
cat .env
# Should contain: OPENAI_API_KEY=your_key_here

# ✅ Sample data exists?
ls data/
# Should list: 5 files (.txt, .json, .csv)
```

---

## 🎯 3 Ways to Run

### Method 1: Jupyter Notebook (Classic)

```bash
jupyter notebook notebooks/document_assistant_demo.ipynb
```

**Advantages**:
- ✅ Familiar interface
- ✅ Works in any browser
- ✅ Easy to use

### Method 2: JupyterLab (Modern)

```bash
jupyter lab notebooks/document_assistant_demo.ipynb
```

**Advantages**:
- ✅ Modern interface
- ✅ More features
- ✅ Multiple notebooks

### Method 3: VS Code (IDE)

1. Open the file in VS Code
2. VS Code detects automatically
3. Click "Run All"

**Advantages**:
- ✅ Integrated with your IDE
- ✅ IntelliSense and debugging
- ✅ Integrated Git

---

## 🔧 If Jupyter Doesn't Work

### Alternative 1: Python Script

```bash
python3 tests/test_with_sample_data.py
```

Offers **exactly** the same functionality as the notebook!

### Alternative 2: Interactive CLI

```bash
python3 main.py ./data
```

Conversational interface - type queries directly.

---

## ❓ Common Problems

### "jupyter: command not found"

```bash
pip install jupyter notebook
```

### "Kernel error" or "Kernel dead"

```bash
pip install ipykernel
python3 -m ipykernel install --user
```

### "No module named 'src'"

The notebook has a cell that adds the project to the path. Run the first cell first!

### "OPENAI_API_KEY not found"

```bash
cp .env.example .env
# Edit .env and add your key
```

---

## 📊 What to Expect

When you run, you'll see:

```
==========================================================
  Document Assistant - Interactive Demo
==========================================================

✅ Imports successful
📁 Project root: /path/to/project

✅ LLM initialized successfully with Vocareum endpoint

📚 Loaded 5 documents from /path/to/data

📊 Statistics:
  - Session ID: abc-123-def
  - Documents: 5
  - Messages: 0

==========================================================
TEST 1: Q&A Intent - Information Retrieval
==========================================================

Query 1: What was the total Q1 sales revenue?
💬 Response: Based on the sales report, the total Q1 2024...
```

And so on for all 8 tests!

---

## ✅ Success Verification

If you see this at the end:

```
✅ All Tests Completed Successfully!

📊 Final Statistics:
Session ID: abc-123-def-456
Documents Loaded: 5
Total Messages: 28

🎉 Document Assistant Demo Complete!
```

**Congratulations!** Everything worked perfectly! 🎉

---

## 🎓 Useful Notebook Shortcuts

- `Shift + Enter`: Run current cell and go to next
- `Ctrl + Enter`: Run current cell
- `Alt + Enter`: Run and insert new cell
- `Esc`: Exit edit mode
- `M`: Change to Markdown
- `Y`: Change to Code
- `A`: Insert cell above
- `B`: Insert cell below
- `D D`: Delete cell (press D twice)

---

## 📚 More Information

- **Details**: [notebooks/RUNNING_NOTEBOOKS.md](notebooks/RUNNING_NOTEBOOKS.md)
- **Troubleshooting**: [notebooks/README.md](notebooks/README.md)
- **Documentation**: [README.md](README.md)

---

## 💡 Final Tip

If you just want to see the system working quickly without Jupyter:

```bash
python3 tests/test_with_sample_data.py
```

It's faster, simpler, and shows everything working! 🚀

---

**Estimated time**: 2-3 minutes for setup, 5-10 minutes to run all tests.

**Ready to start? Run:**

```bash
jupyter notebook notebooks/document_assistant_demo.ipynb
```
