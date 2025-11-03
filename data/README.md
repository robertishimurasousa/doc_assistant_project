# Sample Data Files

This directory contains sample documents for testing the Document Assistant.

## Files Overview

### 1. sales_report_q1_2024.txt
**Type**: Text Report
**Size**: ~3 KB
**Content**: Comprehensive Q1 2024 sales report including:
- Monthly performance breakdown (January, February, March)
- Revenue and units sold
- Customer acquisition metrics
- Regional performance analysis
- Product category breakdown
- Key findings and recommendations

**Use Cases**:
- Q&A queries: "What was the total Q1 revenue?"
- Calculations: "Calculate the average monthly sales"
- Summarization: "Summarize the Q1 sales performance"

### 2. team_structure.txt
**Type**: Text Document
**Size**: ~2.5 KB
**Content**: Company team structure and information:
- Leadership team (CTO)
- Engineering department members
- Active projects with budgets and status
- Team statistics and performance metrics
- Skills matrix
- Hiring plans

**Use Cases**:
- Q&A queries: "Who is the CTO?" or "What projects are in progress?"
- Calculations: "What is the total project budget?"
- Summarization: "Summarize the team structure"

### 3. financial_overview.txt
**Type**: Text Report
**Size**: ~5 KB
**Content**: Detailed financial information for 2024:
- Q1 and Q2 revenue/expense breakdown
- Profitability analysis and margins
- Cash flow statement
- Balance sheet snapshot
- Key financial ratios
- Budget vs. actual comparison
- Financial goals and investment plans

**Use Cases**:
- Q&A queries: "What is the profit margin?" or "What was Q1 profit?"
- Calculations: "Calculate the debt-to-equity ratio"
- Summarization: "Summarize the financial health"

### 4. product_catalog.json
**Type**: JSON Data
**Size**: ~3 KB
**Content**: Product catalog with structured data:
- 5 products with detailed specifications
- Pricing models (one-time, monthly, hourly)
- Product categories and revenue breakdown
- Pricing tiers (Starter, Professional, Enterprise)
- Promotions and customer segments

**Use Cases**:
- Q&A queries: "What products are available?" or "What is the price of Enterprise License?"
- Calculations: "What is the total revenue from cloud services?"
- Summarization: "Summarize the product offerings"

### 5. customer_feedback.csv
**Type**: CSV Data
**Size**: ~2 KB
**Content**: Customer feedback and ratings:
- 20 customer feedback entries
- Product ratings (1-5 stars)
- Feedback text and sentiment analysis
- Categories: positive, neutral, negative

**Use Cases**:
- Q&A queries: "What are customers saying about Cloud Services?"
- Calculations: "Calculate the average rating for each product"
- Summarization: "Summarize customer sentiment"

## Data Statistics

| File | Type | Lines | Size | Documents Loaded |
|------|------|-------|------|------------------|
| sales_report_q1_2024.txt | Text | ~80 | 3 KB | 1 |
| team_structure.txt | Text | ~120 | 2.5 KB | 1 |
| financial_overview.txt | Text | ~220 | 5 KB | 1 |
| product_catalog.json | JSON | ~150 | 3 KB | 1 |
| customer_feedback.csv | CSV | ~21 | 2 KB | 1 |
| **Total** | - | **~590** | **~15.5 KB** | **5** |

## Usage Examples

### Load all data files:
```python
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./data", llm=llm)
count = assistant.load_documents()
print(f"Loaded {count} documents")
```

### Query the data:
```python
# Q&A Intent
response = assistant.query("What was the total Q1 revenue?")

# Calculation Intent
response = assistant.query("Calculate the average monthly sales for Q1")

# Summarization Intent
response = assistant.query("Summarize the team structure")
```

### Use with Jupyter Notebook:
```bash
cd notebooks
jupyter notebook document_assistant_demo.ipynb
```

## Data Refresh

These are sample files created for testing purposes. To use your own data:

1. Remove or backup existing files
2. Add your own `.txt`, `.md`, `.json`, or `.csv` files
3. Reload documents in the assistant

## Supported Formats

- **Text files** (`.txt`, `.md`): Plain text documents, reports, documentation
- **JSON files** (`.json`): Structured data with nested objects
- **CSV files** (`.csv`): Tabular data with headers

## Notes

- All financial figures are fictional and for demonstration purposes
- Company and employee names are fictional
- Data is designed to showcase different query types and agent capabilities
- File size is optimized for quick loading and testing
