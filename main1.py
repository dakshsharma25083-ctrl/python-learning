import sqlite3

# Connect to database (file ban jayegi automatically)
conn = sqlite3.connect("marksheet.db")
cur = conn.cursor()

# Create table  h gg   
cur.execute("""
    CREATE TABLE IF NOT EXISTS students ( 
        roll_no INTEGER PRIMARY KEY,
        name TEXT NOT NULL
        english INTEGER,
        math INTEGER,
        science INTEGER,
        urdu INTEGER,   
        computer INTEGER
    )
""")
conn.commit()                


# Function: Calculate grade
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "F"



conn.close()