# SCHEMA_CONTEXT = """
# SQLite database schema:

# Employee(
#   EmployeeId INTEGER PRIMARY KEY,
#   Name TEXT NOT NULL,
#   Department TEXT NOT NULL, -- Sales, Marketing, Engineering
#   Role TEXT NOT NULL,
#   EmploymentStartDate TEXT NOT NULL, -- YYYY-MM-DD
#   SalaryAmount REAL NOT NULL,
#   YearlyBonusAmount REAL
# )

# Certification(
#   CertificationId INTEGER PRIMARY KEY,
#   EmployeeId INTEGER NOT NULL,
#   CertificationName TEXT NOT NULL,
#   DateAchieved TEXT NOT NULL,
#   FOREIGN KEY(EmployeeId) REFERENCES Employee(EmployeeId)
# )

# Benefits(
#   BenefitId INTEGER PRIMARY KEY,
#   EmployeeId INTEGER NOT NULL,
#   BenefitsPackage TEXT NOT NULL,
#   RemainingBalance REAL NOT NULL,
#   FOREIGN KEY(EmployeeId) REFERENCES Employee(EmployeeId)
# )

# Relationships:
# - Certification.EmployeeId joins to Employee.EmployeeId
# - Benefits.EmployeeId joins to Employee.EmployeeId
# """


SCHEMA_CONTEXT = """
Employee(EmployeeId, Name, Department, Role, EmploymentStartDate, SalaryAmount, YearlyBonusAmount)

Certification(CertificationId, EmployeeId, CertificationName, DateAchieved)

Benefits(BenefitId, EmployeeId, BenefitsPackage, RemainingBalance)

Relationships:
- Certification.EmployeeId → Employee.EmployeeId
- Benefits.EmployeeId → Employee.EmployeeId
"""