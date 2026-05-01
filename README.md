# NL2SQL Data Agent – Take Home Submission (Dayforce)
## Submission Overview
This Project implements a Natural Language to SQL (NL2SQL) system with strong emphasis on:
- Guardrails and access control
- Robust handling of LLM outputs
- Accurate SQL generation and execution
The solution reflects how real-world AI data agents are built - treating the LLM as an untrusted component and enforcing correctness through validation and safety layers.
---
## Overview
This application allows users to query an employee database using natural language.  
The system translates user queries into SQL, executes them on a SQLite database and returns results in a structured format.
---
## Features
- Natural language → SQL query generation
- Executes queries on a SQLite database (`employees.db`)
- **Strict department-level guardrail enforcement**
- Handles ambiguous queries (e.g., certification names like AWS/Azure)
- SQL validation and safety filtering
- Retry mechanism for LLM failures
- SQL normalization and extraction from imperfect outputs
- Supports:
  - Employee queries
  - Certifications
  - Benefits
  - Aggregations (AVG, COUNT)
  - Ranking queries (highest, top)
  - Date-based filtering
---
## Architecture
### 1. `main.py`
- Entry point of the application
- Handles user input loop
- Detects department from user queries
- Orchestrates query generation → validation → execution
---
### 2. `nl_to_sql.py`
- Uses an LLM (via Ollama) to convert natural language into SQL
- Uses strict prompt rules to enforce:
  - SELECT-only queries
  - Correct schema usage
  - Proper joins and filters
---
### 3. `guardrails.py`
- Core safety layer (critical component)
- Responsibilities:
  - Clean and normalize LLM output
  - Extract valid SQL statements
  - Enforce SELECT-only queries
  - Prevent multiple statements
  - Apply department-level filtering
  - Fix common LLM-generated SQL errors
---
### 4. `db.py`
- Handles SQLite connection and query execution
---
## Guardrail Enforcement
At startup, the system:
1. Randomly selects one department:
   - Sales
   - Marketing
   - Engineering
2. Logs it to the console:

[INFO] Default department selected: Engineering

3. Enforces this constraint on all queries:
- Only data from the selected department is accessible
- Cross-department data leakage is strictly prevented
Additionally:
- If a user explicitly specifies a department in their query, it is safely applied as an override.
---
## Handling LLM Imperfections
LLMs are not always reliable, so this system treats them as **untrusted**.
### Techniques implemented:
### SQL Normalization
- Removes unwanted text like:
- “SELECT query:”
- “Here is the SQL”
### SQL Extraction
- Extracts the first valid SELECT statement
- Handles missing semicolons
### Auto-Correction
- Fixes common issues:
- Invalid aliasing (`AS.Department`)
- Duplicate WHERE conditions
- Syntax inconsistencies
### Retry Logic
- Retries SQL generation when validation fails
---
## Query Examples

Who are software engineers?
Which employees have AWS certification?
What is the average salary?
Who has the highest remaining benefits balance?
List employees who started after 2023 and have AWS certification

---
## Example Output

Ask a question: Which employees have AWS certification in engineering?

[INFO] Department filter applied: Engineering

[DEBUG] Generated SQL:
SELECT e.Name, e.Department, c.CertificationName
FROM Employee e
JOIN Certification c ON e.EmployeeId = c.EmployeeId
WHERE c.CertificationName LIKE ‘%AWS%’
AND e.Department = ‘Engineering’;

```text
+-------------------+--------------+-------------------------+
| Name              | Department   | CertificationName       |
+-------------------+--------------+-------------------------+
| Scott Lee         | Engineering  | AWS Developer Associate |
| Jacob Nelson      | Engineering  | AWS Solutions Architect |
...
```
---
## Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/rahulagg02/nl2sql-agent.git
cd nl2sql-agent
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   
```

3. Install dependencies
```bash
pip install -r requirements.txt
pip install ollama
```

4. Install and run Ollama (LLM)

Download Ollama:
https://ollama.com

Pull the model:
```bash
ollama pull llama3

# Terminal 1 - Start Ollama

ollama serve
```
# Terminal 2 - Run the app
5. Run the application
```bash
source venv/bin/activate
python main.py
```

## AI Tools Used

* ChatGPT - architecture design, debugging, prompt engineering
* Ollama - local LLM for NL → SQL generation

## AI tools were used to:

* Accelerate development
* Improve robustness and edge-case handling
* Explore failure scenarios and fixes

⸻

## Design Decisions & Tradeoffs:

## Guardrails over flexibility

* Strict filtering ensures security but limits unrestricted querying

## LLM treated as untrusted

* All outputs are validated and sanitized before execution

## Fuzzy matching for certifications

* Uses LIKE '%value%' for realistic querying (e.g., AWS certifications)

## Lightweight architecture

* No heavy frameworks used
* Focused on clarity, control and correctness

⸻

## Assumptions

* Certification queries use fuzzy matching (LIKE)
* Dates are stored as strings (YYYY-MM-DD)
* Each employee belongs to one department

⸻

## Demo Readiness

This application is ready for live demo and supports:

* Real-time query handling
* SQL explanation via debug logs
* Guardrail enforcement demonstration
* Error handling and recovery

⸻

## Summary

This system demonstrates:

* Strong NL → SQL capabilities
* Robust handling of LLM limitations
* Secure query execution with enforced guardrails
* Clean and modular architecture
