import ollama
from schema import SCHEMA_CONTEXT


def generate_sql(question: str, department: str) -> str:
    prompt = f"""
You are an expert SQLite SQL generator.

Your task:
Convert the user's natural language question into a SAFE and VALID SQLite SELECT query.

{SCHEMA_CONTEXT}

STRICT RULES:
1. ONLY generate SELECT queries.
2. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE.
3. ALWAYS use alias 'e' for Employee table.
4. ALWAYS reference department as e.Department.
5. ALWAYS include filter: e.Department = '{department}' in WHERE clause.
6. ALWAYS include e.Department in SELECT output.
7. Use joins when needed:
   - Certification c ON e.EmployeeId = c.EmployeeId
   - Benefits b ON e.EmployeeId = b.EmployeeId
8. Use correct SQL syntax for SQLite.
9. Do NOT wrap query in ``` or markdown.
10. Output ONLY the SQL query.
11. Do NOT use "AS.Department". Always use e.Department.
12. For certification filters, ALWAYS use LIKE '%value%' instead of exact match.
   Example:
   c.CertificationName LIKE '%AWS%'
   c.CertificationName LIKE '%Azure%'
13. When querying certifications, ALWAYS include c.CertificationName in SELECT.
14. When filtering by role, use exact match:
   e.Role = 'Software Engineer'
15. For aggregation queries:
   - Use proper SQL aggregation functions (AVG, COUNT, SUM, etc.)
   - Do NOT include unnecessary columns in SELECT.
16. For ranking queries (e.g., highest, top, maximum):
   - Use ORDER BY <column> DESC
   - Use LIMIT 1

17. For date filters:
   - Use format: 'YYYY-MM-DD'
   - Example:
     e.EmploymentStartDate > '2023-01-01'

18. Always ensure valid SQL structure:
   SELECT ...
   FROM ...
   JOIN ... (if needed)
   WHERE ...
   ORDER BY ... (if needed)
   LIMIT ... (if needed)

19. Avoid duplicate conditions like:
   WHERE e.Department = 'X' AND e.Department = 'X'

20. Ensure all column references use correct table aliases:
   - e for Employee
   - c for Certification
   - b for Benefits

EXAMPLES:

User: Who are software engineers?
SQL:
SELECT e.Name, e.Role, e.Department
FROM Employee e
WHERE e.Role = 'Software Engineer'
AND e.Department = '{department}';

User: What is the average salary?
SQL:
SELECT AVG(e.SalaryAmount) AS avg_salary
FROM Employee e
WHERE e.Department = '{department}';

User: Which employees have AWS certification?
SQL:
SELECT e.Name, e.Department, c.CertificationName
FROM Employee e
JOIN Certification c ON e.EmployeeId = c.EmployeeId
WHERE c.CertificationName LIKE '%AWS%'
AND e.Department = '{department}';

User Question:
{question}

SQL:
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response["message"]["content"].strip()

    # Clean markdown if present
    response_text = response_text.replace("```sql", "").replace("```", "").strip()

    # Remove "SQL:" prefix if present
    lines = response_text.split("\n")
    sql_lines = [line for line in lines if not line.lower().startswith("sql")]
    final_sql = "\n".join(sql_lines).strip()

    return final_sql