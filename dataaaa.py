import sqlite3
import os

DB_FILE = "dataaa.db"


def connect_db():
    connection = sqlite3.connect(DB_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            class INTEGER,
            course TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
        """
    )
    connection.commit()
    return connection



def get_subjects(class_number, course=None):
    if 1 <= class_number <= 10:
        return ["Math", "Science", "English", "Social Studies", "Hindi", "Sanskrit"]
    if class_number in (11, 12):
        normalized = (course or "").strip().upper()
        if normalized == "PCM":
            return ["Math", "Physics", "Chemistry", "English", "Hindi"]
        if normalized == "PCB":
            return ["Physics", "Chemistry", "Biology", "English", "Hindi"]
        if normalized == "COMMERCE":
            return ["Accounts", "Business Studies", "Economics", "English", "Hindi"]
        if normalized == "ARTS":
            return ["History", "Geography", "Political Science", "English", "Hindi"]
    return []



def input_int(prompt, min_value=None, max_value=None):
    while True:
        value = input(prompt).strip()
        if not value:
            print("Please enter a value.")
            continue
        if not value.isdigit():
            print("Please enter a valid number.")
            continue
        number = int(value)
        if min_value is not None and number < min_value:
            print(f"Please enter a value >= {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Please enter a value <= {max_value}.")
            continue
        return number



def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")



def choose_course():
    valid_courses = ["PCM", "PCB", "Commerce", "Arts"]
    while True:
        course = input_nonempty("Enter course for class 11-12 (PCM/PCB/Commerce/Arts): ")
        if course.upper() in [c.upper() for c in valid_courses]:
            return course.title() if course.lower() != "pcm" and course.lower() != "pcb" else course.upper()
        print("Invalid course. Choose PCM, PCB, Commerce or Arts.")



def add_student(connection):
    print("\n=== Add New Student ===")
    first_name = input_nonempty("First name: ")
    last_name = input_nonempty("Last name: ")
    class_number = input_int("Class (1-12): ", 1, 12)
    course = None
    if class_number in (11, 12):
        course = choose_course()

    subjects = get_subjects(class_number, course)
    if not subjects:
        print("Could not determine subjects for this class/course.")
        return

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO students (first_name, last_name, class, course) VALUES (?, ?, ?, ?)",
        (first_name, last_name, class_number, course),
    )
    student_id = cursor.lastrowid

    for subject in subjects:
        marks = input_int(f"Marks for {subject} (0-100): ", 0, 100)
        cursor.execute(
            "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)",
            (student_id, subject, marks),
        )

    connection.commit()
    print("Student and marksheet saved successfully.")



def list_students(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT id, first_name, last_name, class, course FROM students ORDER BY id")
    rows = cursor.fetchall()
    if not rows:
        print("\nNo students found.")
        return

    print("\n=== Student List ===")
    print(f"{'ID':<4} {'Name':<25} {'Class':<6} {'Course':<10}")
    print("-" * 50)
    for student_id, first_name, last_name, class_number, course in rows:
        name = f"{first_name} {last_name}"
        print(f"{student_id:<4} {name:<25} {class_number:<6} {course or '-':<10}")



def view_student_details(connection):
    student_id = input_int("Enter student ID to view: ", 1)
    cursor = connection.cursor()
    cursor.execute("SELECT first_name, last_name, class, course FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        print("Student not found.")
        return

    first_name, last_name, class_number, course = student
    cursor.execute(
        "SELECT subject, marks FROM marks WHERE student_id = ? ORDER BY id",
        (student_id,),
    )
    marks = cursor.fetchall()

    print("\n=== Student Details ===")
    print(f"ID       : {student_id}")
    print(f"Name     : {first_name} {last_name}")
    print(f"Class    : {class_number}")
    print(f"Course   : {course or '-'}")
    print("\nMarksheet:")
    if not marks:
        print("  No marks recorded.")
        return

    total = 0
    print(f"{'Subject':<20} {'Marks':>5}")
    print("-" * 28)
    for subject, mark in marks:
        print(f"{subject:<20} {mark:>5}")
        total += mark
    average = total / len(marks)
    status = "Pass" if all(mark >= 35 for _, mark in marks) else "Fail"
    print("-" * 28)
    print(f"Total    : {total}")
    print(f"Average  : {average:.2f}")
    print(f"Status   : {status}")



def edit_student(connection):
    student_id = input_int("Enter student ID to edit: ", 1)
    cursor = connection.cursor()
    cursor.execute("SELECT first_name, last_name, class, course FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        print("Student not found.")
        return

    first_name, last_name, class_number, course = student
    print("\nLeave blank to keep the current value.")

    new_first_name = input(f"First name [{first_name}]: ").strip() or first_name
    new_last_name = input(f"Last name [{last_name}]: ").strip() or last_name

    class_input = input(f"Class [{class_number}]: ").strip()
    if class_input:
        try:
            new_class_number = int(class_input)
            if new_class_number < 1 or new_class_number > 12:
                print("Invalid class. Keeping existing class.")
                new_class_number = class_number
        except ValueError:
            print("Invalid class input. Keeping existing class.")
            new_class_number = class_number
    else:
        new_class_number = class_number

    new_course = course
    if new_class_number in (11, 12):
        course_input = input(f"Course [{course or 'None'}]: ").strip()
        if course_input:
            normalized = course_input.title() if course_input.lower() not in ("pcm", "pcb") else course_input.upper()
            if normalized.upper() in ("PCM", "PCB", "COMMERCE", "ARTS"):
                new_course = normalized
            else:
                print("Invalid course. Keeping existing course.")
        elif not course:
            new_course = choose_course()
    else:
        new_course = None

    if new_class_number != class_number or new_course != course:
        print("Class or course changed. Marks may need to be updated based on the new subject list.")
        rebuild = input("Do you want to rebuild the marksheet now? (y/n): ").strip().lower()
        if rebuild == "y":
            cursor.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
            subjects = get_subjects(new_class_number, new_course)
            for subject in subjects:
                marks = input_int(f"Marks for {subject} (0-100): ", 0, 100)
                cursor.execute(
                    "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)",
                    (student_id, subject, marks),
                )

    cursor.execute(
        "UPDATE students SET first_name = ?, last_name = ?, class = ?, course = ? WHERE id = ?",
        (new_first_name, new_last_name, new_class_number, new_course, student_id),
    )
    connection.commit()
    print("Student record updated.")



def edit_marks(connection):
    student_id = input_int("Enter student ID to edit marks: ", 1)
    cursor = connection.cursor()
    cursor.execute("SELECT first_name, last_name FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        print("Student not found.")
        return

    cursor.execute("SELECT id, subject, marks FROM marks WHERE student_id = ? ORDER BY id", (student_id,))
    rows = cursor.fetchall()
    if not rows:
        print("No marks available to edit.")
        return

    print(f"\nEditing marks for {student[0]} {student[1]}")
    for mark_id, subject, current_mark in rows:
        prompt = f"{subject} [{current_mark}]: "
        entry = input(prompt).strip()
        if entry:
            if not entry.isdigit() or not (0 <= int(entry) <= 100):
                print("Invalid mark. Keeping current value.")
                continue
            cursor.execute("UPDATE marks SET marks = ? WHERE id = ?", (int(entry), mark_id))

    connection.commit()
    print("Marks updated successfully.")



def delete_student(connection):
    student_id = input_int("Enter student ID to delete: ", 1)
    cursor = connection.cursor()
    cursor.execute("SELECT first_name, last_name FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        print("Student not found.")
        return

    confirm = input(f"Are you sure you want to delete {student[0]} {student[1]}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Deletion canceled.")
        return

    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    connection.commit()
    print("Student deleted.")



def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")



def print_menu():
    print("\n=== Marksheet Manager ===")
    print("1. Add student and marksheet")
    print("2. View all students")
    print("3. View student details")
    print("4. Edit student information")
    print("5. Edit student marks")
    print("6. Delete student")
    print("7. Exit")



def main():
    connection = init_db()
    try:
        while True:
            print_menu()
            choice = input("Choose an option (1-7): ").strip()
            if choice == "1":
                add_student(connection)
            elif choice == "2":
                list_students(connection)
            elif choice == "3":
                view_student_details(connection)
            elif choice == "4":
                edit_student(connection)
            elif choice == "5":
                edit_marks(connection)
            elif choice == "6":
                delete_student(connection)
            elif choice == "7":
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
    finally:
        connection.close()



if __name__ == "__main__":
    main()