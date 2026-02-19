import sqlite3

# Connect to database
connection = sqlite3.connect("data.db")
cursor = connection.cursor()

# Create table (if not exists)
table = """
CREATE TABLE IF NOT EXISTS Students(
    name VARCHAR(30),
    class VARCHAR(10),
    marks INT,
    company VARCHAR(30)
)
"""
cursor.execute(table)

# Insert records
cursor.execute("insert into Students values('Sijo', 'BTech', 75, 'JSW')")
cursor.execute("insert into Students values('Lijo', 'MTech', 69, 'TCS')")
cursor.execute("insert into Students values('Rijo', 'BSc', 79, 'WIPRO')")
cursor.execute("insert into Students values('Sibin', 'MSc', 89, 'INFOSYS')")
cursor.execute("insert into Students values('Dilsha', 'MCom', 99, 'Cyient')")

# Query records
print("Inserted Records:\n")

data = cursor.execute("select * from Students")

for row in data:
    print(row)

# Save changes and close
connection.commit()
connection.close()
