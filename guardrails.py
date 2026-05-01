import re
import sqlparse


BLOCKED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "PRAGMA", "ATTACH", "DETACH"
}

def clean_sql(sql: str) -> str:
    sql = sql.strip()

    # Remove markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()

    # Remove common junk lines
    lines = sql.splitlines()
    cleaned_lines = []

    for line in lines:
        line_strip = line.strip().lower()

        if (
            "select query" in line_strip
            or "sql query" in line_strip
            or "here is" in line_strip
        ):
            continue

        cleaned_lines.append(line)

    sql = "\n".join(cleaned_lines).strip()

    # Extract SELECT statement (semicolon optional)
    match = re.search(r"(SELECT[\s\S]+)", sql, re.IGNORECASE)

    if not match:
        raise ValueError("No valid SELECT statement found.")

    sql = match.group(1).strip()

    # Ensure only ONE statement (cut after first ;)
    if ";" in sql:
        sql = sql.split(";")[0]

    # Add semicolon back
    sql = sql.strip() + ";"

    return sql

def fix_common_sql_issues(sql: str) -> str:
    """
    Fix common LLM SQL mistakes
    """

    # Fix AS.Department → e.Department
    sql = re.sub(r"\bAS\.Department\b", "e.Department", sql, flags=re.IGNORECASE)

    # Fix Employee AS e → Employee e (optional cleanup)
    sql = re.sub(r"\bEmployee\s+AS\s+(\w+)", r"Employee \1", sql, flags=re.IGNORECASE)

    # Fix duplicate WHERE
    sql = re.sub(r"\bWHERE\s+WHERE\b", "WHERE", sql, flags=re.IGNORECASE)

    # Fix accidental "AND AND"
    sql = re.sub(r"\bAND\s+AND\b", "AND", sql, flags=re.IGNORECASE)

    sql = re.sub(r"c\.CertificationName\s*=\s*'AWS'", "c.CertificationName LIKE '%AWS%'", sql, flags=re.IGNORECASE)

    return sql

def validate_sql(sql: str) -> None:
    parsed = sqlparse.parse(sql)

    if not parsed:
        raise ValueError("Could not parse generated SQL.")

    statement = parsed[0]

    if statement.get_type() != "SELECT":
        raise ValueError("Only SELECT queries are allowed.")

    upper_sql = sql.upper()

    for keyword in BLOCKED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise ValueError(f"Blocked unsafe SQL keyword: {keyword}")

    if ";" in sql.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")

    if "EMPLOYEE" not in upper_sql:
        raise ValueError("Query must include Employee table.")


def enforce_department_guardrail(sql: str, department: str) -> str:
    sql = sql.strip().rstrip(";")

    # Detect alias (e.g., Employee e)
    alias_match = re.search(r"\bEmployee\s+(\w+)", sql, re.IGNORECASE)
    alias = alias_match.group(1) if alias_match else "Employee"

    dept_column = f"{alias}.Department"

    # Already filtered
    if re.search(rf"{dept_column}\s*=", sql, re.IGNORECASE):
        return sql + ";"

    # Inject condition
    if re.search(r"\bWHERE\b", sql, re.IGNORECASE):
        sql = re.sub(
            r"\bWHERE\b",
            f"WHERE {dept_column} = '{department}' AND ",
            sql,
            flags=re.IGNORECASE,
        )
    else:
        match = re.search(r"\b(ORDER BY|GROUP BY|LIMIT)\b", sql, re.IGNORECASE)
        if match:
            idx = match.start()
            sql = sql[:idx] + f" WHERE {dept_column} = '{department}' " + sql[idx:]
        else:
            sql += f" WHERE {dept_column} = '{department}'"

    return sql + ";"