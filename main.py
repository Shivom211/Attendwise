from logic import load_data, save_data

def main():
    data = load_data()

    while True:
        print("\n--- AttendWise Menu ---")
        print("1. Add Subject")
        print("2. Update Attendance")
        print("3. View Attendance")
        print("4. Skip Decision")
        print("5. Update Required Attendance")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_subject(data)
        elif choice == "2":
            update_attendance(data)
        elif choice == "3":
            view_attendance(data)
        elif choice == "4":
            skip_decision(data)
        elif choice == "5":
            update_required_attendance(data)
        elif choice == "6":
            print("Exiting AttendWise. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

def add_subject(data):
    name = input("Enter subject name: ").strip().upper()

    if name in data["subjects"]:
        print("Subject already exists!")
        return

    importance = input("Importance (high/medium/low): ").strip().lower()
    if importance not in ["high", "medium", "low"]:
        print("Invalid importance level.")
        return

    try:
        classes_per_week = int(input("Classes per week: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    data["subjects"][name] = {
        "total_classes": 0,
        "attended_classes": 0,
        "importance": importance,
        "classes_per_week": classes_per_week
    }

    save_data(data)
    print(f"Subject '{name}' added successfully!")
def update_attendance(data):
    subjects = data["subjects"]

    if not subjects:
        print("No subjects found. Please add a subject first.")
        return

    print("\nAvailable subjects:")
    for name in subjects:
        print("-", name)

    subject_name = input("Enter subject name: ").strip().upper()

    if subject_name not in subjects:
        print("Subject not found.")
        return

    attended = input("Did you attend the class? (yes/no): ").strip().lower()

    subjects[subject_name]["total_classes"] += 1

    if attended == "yes":
        subjects[subject_name]["attended_classes"] += 1

    save_data(data)
    print(f"Attendance updated for {subject_name}.")
def view_attendance(data):
    subjects = data["subjects"]

    if not subjects:
        print("No subjects found.")
        return

    print("\n--- Subject-wise Attendance ---")
    total_attended = 0
    total_classes = 0

    for name, info in subjects.items():
        attended = info["attended_classes"]
        total = info["total_classes"]

        if total == 0:
            percent = 0
        else:
            percent = (attended / total) * 100

        print(f"{name}: {attended}/{total} classes ({percent:.2f}%)")

        total_attended += attended
        total_classes += total

    if total_classes == 0:
        overall_percent = 0
    else:
        overall_percent = (total_attended / total_classes) * 100

    print(f"\nOverall Attendance: {overall_percent:.2f}%")

def can_skip_next_class(subject, required_percent):
    attended = subject["attended_classes"]
    total = subject["total_classes"]

    
    if total == 0:
        return False, 0

   
    next_percent = (attended / (total + 1)) * 100
    can_skip = next_percent >= required_percent

    
    skip_count = 0
    temp_total = total

    while True:
        temp_total += 1
        percent = (attended / temp_total) * 100
        if percent >= required_percent:
            skip_count += 1
        else:
            break

    return can_skip, skip_count


def skip_decision(data):
    subjects = data["subjects"]
    required = data["settings"]["min_attendance_required"]

    if not subjects:
        print("No subjects available.")
        return

    print("\nAvailable subjects:")
    for name in subjects:
        print("-", name)

    subject_name = input("Enter subject name: ").strip().upper()

    if subject_name not in subjects:
        print("Subject not found.")
        return

    subject = subjects[subject_name]
    can_skip, skip_count = can_skip_next_class(subject, required)

    print(f"\nRequired attendance: {required}%")
    print(f"Current attendance: {subject['attended_classes']}/{subject['total_classes']}")

    if can_skip:
        print(f"✅ You CAN skip the next class.")
    else:
        print(f"❌ You should NOT skip the next class.")

    if skip_count==0:
        print("❌ You cannot skip any more classes safely.")
    else:
        print(f"You can skip{skip_count} more class(es)safely.")
    # Soft importance warning
    if subject["importance"] == "high" and can_skip:
        print("⚠️ Note: This is a HIGH importance subject. Skip only if necessary.")

def update_required_attendance(data):
    current=data["settings"]["min_attendance_required"]
    print(f"Current required attendance:{current}%")
    try:
        new_value=int(input("Enter new required percentage:"))
    except ValueError:
        print("Please enter a valid number.")
        return
    if new_value<=0 or new_value>100:
        print("Attendance percentage must be between 1 and 100.")
        return
    data["settings"]["min_attendance_required"]=new_value
    save_data(data)
    print(f"Required attendance updated to {new_value}%")


if __name__ == "__main__":
    main()
    