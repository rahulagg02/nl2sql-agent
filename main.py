import random
import datetime
from dotenv import load_dotenv
from tabulate import tabulate

from db import Database
from nl_to_sql import generate_sql
from guardrails import (
    clean_sql,
    validate_sql,
    enforce_department_guardrail,
    fix_common_sql_issues,
)


DEPARTMENTS = ["Sales", "Marketing", "Engineering"]


def detect_department(question, default_department):
    q = question.lower()

    if "marketing" in q:
        return "Marketing"
    elif "engineering" in q:
        return "Engineering"
    elif "sales" in q:
        return "Sales"

    return default_department


def print_results(columns, rows):
    if not rows:
        print("No results found for this department.")
        print("Try querying a different role or department.")
        return

    print(tabulate(rows, headers=columns, tablefmt="grid"))


def main():
    load_dotenv()

    selected_department = random.choice(DEPARTMENTS)
    print(f"[INFO] Default department selected: {selected_department}")
    print("[INFO] Queries will be restricted to a department.")
    print("Type 'exit' or 'quit' to stop.\n")

    print("Try questions like:")
    print("- Who are software engineers?")
    print("- Who are software engineers in marketing?")
    print("- What is the average salary?")
    print("- Which employees have AWS certification?\n")

    db = Database("employees.db")

    try:
        while True:
            question = input("Ask a question: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            if not question:
                print("Please enter a question.")
                continue

            print(f"\n[INFO] Interpreting question: {question}")

            # Detect department dynamically
            effective_department = detect_department(question, selected_department)
            print(f"[INFO] Department filter applied: {effective_department}")

            print(f"[LOG] {datetime.datetime.now()} | Query: {question}")

            try:
                # Retry logic
                for attempt in range(3):
                    try:
                        raw_sql = generate_sql(question, effective_department)

                        sql = clean_sql(raw_sql)
                        sql = fix_common_sql_issues(sql)
                        validate_sql(sql)

                        guarded_sql = enforce_department_guardrail(sql, effective_department)
                        break
                    except Exception as e:
                        if attempt == 1:
                            raise e
                        print("[WARN] Retrying query generation...")

                print("\n[DEBUG] Generated SQL:")
                print(guarded_sql)

                print("[INFO] Applying safety filters...")

                try:
                    columns, rows = db.execute_query(guarded_sql)
                except Exception:
                    print("Query execution failed. Please try rephrasing.")
                    continue

                print_results(columns, rows)
                print()

            except Exception as e:
                print(f"Sorry, I could not process that question safely: {e}\n")

    except KeyboardInterrupt:
        print("\nGoodbye! 👋")


if __name__ == "__main__":
    main()