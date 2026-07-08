from predict import predict_status
import json

def load_data():
    with open("data.json") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
from database import get_db
from flask import session
from database import init_db
init_db()
from flask import Flask, render_template, request, redirect, url_for, flash
from logic import load_data, save_data
import matplotlib
matplotlib.use('Agg')   
import matplotlib.pyplot as plt
app=Flask(__name__)
app.secret_key="attendwise-secret"

@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]
    data = load_data()
    
    if user not in data["users"]:
       session.clear()
       return redirect(url_for("login"))
     

    if user not in data["users"]:
     data["users"][user] = {
        "target": 75,
        "subjects": []
    }
    save_data(data)

    if "target" not in data["users"][user]:
        data["users"][user]["target"] = 75
        save_data(data)

    target = data["users"][user]["target"]

    return render_template("home.html", target=target)

@app.route("/add", methods=["GET", "POST"])
def add_page():
    if "user" not in session:
     return redirect(url_for("login"))
    user = session["user"]
    data = load_data()

    # values to remember
    old_subject = ""
    old_classes = ""
    old_importance = "medium"

    if request.method == "POST":
        old_subject = request.form.get("subject", "").strip()
        old_classes = request.form.get("classes", "").strip()
        old_importance = request.form.get("importance", "medium")

        subject = old_subject.upper()

        # validate classes
        if not old_classes.isdigit() or not (1 <= int(old_classes) <= 10):
            flash("Please enter valid no of classes (1-10)", "error")
            return render_template("add.html",
                                   subject=old_subject,
                                   classes=old_classes,
                                   importance=old_importance)

        classes = int(old_classes)

        user = session["user"]

# ensure user exists
        if user not in data["users"]:
         data["users"][user] = {
         "subjects": {},
         "target": 75
}
# duplicate check (NOW SAFE)
        if subject in data["users"][user]["subjects"]:
         flash("Subject already exists", "error")
         return render_template("add.html",
                           subject=old_subject,
                           classes=old_classes,
                           importance=old_importance)

# add subject
        data["users"][user]["subjects"][subject] = {
          "attended": 0,
          "total": 0,
          "classes_per_week": classes,
          "importance": old_importance
}

        save_data(data)
        flash("Subject added successfully", "success")
        return redirect(url_for("add_page"))

    return render_template("add.html",
                           subject=old_subject,
                           classes=old_classes,
                           importance=old_importance)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            db.commit()
            data = load_data()

            if "users" not in data:
             data["users"] = {}

            data["users"][username] = {
             "target": 75,
             "subjects": {}
                }

            save_data(data)
            flash("Registered successfully!", "success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists!", "error")

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if not user:
            flash("Account not found! Please register first","error")
        elif user["password"]!=password:
            flash("Invalid credentials", "error")
        else:
           session["user"]=username
           return redirect(url_for("home"))
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
@app.route("/update", methods=["GET", "POST"])
def update_page():
    if "user" not in session:
        return redirect(url_for("login"))

    data = load_data()
    user = session["user"]
    if "target" not in data["users"][user]:
     data["users"][user]["target"] = 75
     save_data(data)
    subjects = list(data["users"].get(user, {}).get("subjects", {}).keys())
    selected_subject = None

    if request.method == "POST":
        selected_subject = request.form.get("subject")
        status = request.form.get("status")

        if selected_subject in data["users"][user]["subjects"]:
            data["users"][user]["subjects"][selected_subject]["total"] += 1

            if status == "present":
                data["users"][user]["subjects"][selected_subject]["attended"] += 1
                flash(f"Marked PRESENT for {selected_subject}", "success")
            else:
                flash(f"Marked ABSENT for {selected_subject}", "error")

            save_data(data)

    return render_template("update.html",
                           subjects=subjects,
                           selected_subject=selected_subject)
@app.route("/view")
def view_page():
    if "user" not in session:
     return redirect(url_for("login"))
    user = session["user"]
    data = load_data()
    if "target" not in data["users"][user]:
     data["users"][user]["target"] = 75
     save_data(data)
   

    total_attended = 0
    total_classes = 0

    report = []

    user=session["user"]
    subjects=data["users"].get(user,{}).get("subjects",{})

    for name, info in subjects.items():
        attended = info["attended"]
        total = info["total"]

        percent = (attended / total * 100) if total > 0 else 0

        total_attended += attended
        total_classes += total

        report.append({
            "name": name,
            "attended": attended,
            "total": total,
            "percent": round(percent, 2)
        })

    overall = (total_attended / total_classes * 100) if total_classes > 0 else 0

    return render_template("view.html", report=report, overall=round(overall,2))


# def get_decision(attended, total, importance, target):
#     if total == 0:
#         return "No Data"

#     percentage = (attended / total) * 100

#     # importance effect
#     if importance.lower() == "high":
#         percentage -= 5
#     elif importance.lower() == "low":
#         percentage += 5

#     # decision logic
#     if percentage < 60:
#         return "Must Attend 🚨"
#     elif percentage < target:
#         return "Attend ⚠️"
#     else:
#         return "Can Skip 😎"
@app.route("/skip")
def skip():
    if "user" not in session:
     return redirect(url_for("login"))
    user = session["user"]
    decisions = []
    data = load_data()
    if "target" not in data["users"][user]:
     data["users"][user]["target"] = 75
     save_data(data)
    required = data["users"][user]["target"]

    # ===== LOOP THROUGH SUBJECTS =====
    
    user=session["user"]
    subjects=data["users"].get(user,{}).get("subjects",{})

    for name, info in subjects.items():
        attended = info["attended"]
        total = info["total"]
        importance = info.get("importance", "Medium")

        # ===== CURRENT PERCENT =====
        percentage = (attended / total * 100) if total > 0 else 0

        # ===== SAFE BUNKS =====
        safe_bunks = 0
        temp_attended = attended
        temp_total = total

        while True:
            temp_total += 1
            new_percent = (temp_attended / temp_total) * 100

            if new_percent < required:
                break

            safe_bunks += 1

        # ===== NEEDED CLASSES =====
        needed_classes = 0
        temp_attended = attended
        temp_total = total

        while True:
            temp_attended += 1
            temp_total += 1

            new_percent = (temp_attended / temp_total) * 100
            needed_classes += 1

            if new_percent >= required:
                break

        # ===== FUTURE (AFTER SKIP) =====
        future_total = total + 1
        future_percentage = (attended / future_total * 100) if total > 0 else 0
        # 🔮 Skip next 2 classes
        future_skip2 = (
            attended / (total + 2) * 100
        ) if total > 0 else 0

# 📚 Attend next 2 classes
        future_attend2 = (
            (attended + 2) / (total + 2) * 100
        ) if total > 0 else 0
        # ===== STATUS =====
       

       # convert importance
        imp_map = {"low": 1, "medium": 2, "high": 3}
        importance_num = imp_map.get(importance.lower(), 1)

        priority_score=(
          (100-percentage)+
          (imp_map.get(importance,2)*10)
       )


        reason = []

        if percentage < 50:
         reason.append("📉 Very low attendance")

        if percentage < required:
         reason.append("🎯 Below target attendance")

        if importance.lower() == "high":
         reason.append("🔥 High importance subject")

        if needed_classes > 5:
         reason.append(f"📚 Need {needed_classes} classes to recover")

# simple trend (for now)
        if percentage >= required:
         trend = 1      # improving / safe
        elif percentage < 60:
         trend = -1     # danger
        else:
         trend = 0      # neutral  

        decision = predict_status(
         percentage,
         info.get("classes_per_week", 3),
         importance_num,
         trend,
         future_percentage
    )
        # 🔥 ML decides status now
        if decision == "Danger":
         warning = "Danger 🚨"
        elif decision == "Risk":
         warning = "Risk ⚠️"
        else:
         warning = "Safe 👍"
        # ===== STORE =====
        if safe_bunks > 0:
         smart_advice = f"😎 Safe Bunks: {safe_bunks}"

        elif needed_classes <= 2:
         smart_advice = f"👍 Need Classes: {needed_classes}"

        elif needed_classes <= 5:
         smart_advice = f"📚 Recovery Needed ({needed_classes})"

        else:
         smart_advice = f"🚨 Critical Zone ({needed_classes})"


        decisions.append({
    "subject": name,
    "percentage": round(percentage, 2),
    "importance": importance,
    "advice": smart_advice,
    "after_skip": round(future_percentage, 2),
    "status": warning,
    "safe_bunks": safe_bunks,
    "needed_classes": needed_classes,
    "future_skip2": round(future_skip2, 2),
    "future_attend2": round(future_attend2, 2),
    "priority_score":priority_score,
    "reason":reason,
})

    # ===== GRAPH =====
    names = [d["subject"] for d in decisions]
    percentages = [d["percentage"] for d in decisions]

    plt.figure(figsize=(10, 5))
    plt.bar(names, percentages)
    plt.xlabel("Subjects")
    plt.ylabel("Attendance %")
    plt.title("Attendance Overview")
    plt.savefig("static/graph.png")
    plt.close()

    # ===== OVERALL =====
    total_attended = sum(info["attended"] for info in data["users"][user]["subjects"].values())
    total_classes = sum(info["total"] for info in data["users"][user]["subjects"].values())

    overall_percent = (total_attended / total_classes * 100) if total_classes > 0 else 0

    future_overall = (
        total_attended / (total_classes + len(subjects)) * 100
    ) if total_classes > 0 else 0

    # ===== MESSAGE =====
    if future_overall >= required:
        overall_message = "You may skip college today 😎"
        bunk_msg = "You can skip next class 😎"
    else:
        overall_message = "Better attend college today 📚"
        bunk_msg = "Better attend next class 📚"

    print("ML INPUT:", percentage, importance_num, total)
    print("ML OUTPUT:", decision)

    priority_subjects=sorted(
       decisions,
       key=lambda x:x["priority_score"],
       reverse=True
    )[:3]
    return render_template(
        "skip.html",
        decisions=decisions,
        priority_subjects=priority_subjects,
        overall=round(overall_percent, 2),
        message=overall_message,
        bunk_msg=bunk_msg
    )

@app.route("/delete/<subject>", methods=["POST"])
def delete_subject(subject):
    if "user" not in session:
        return redirect(url_for("login"))

    data = load_data()
    user = session["user"]

    if subject in data["users"].get(user, {}).get("subjects", {}):
        del data["users"][user]["subjects"][subject]
        save_data(data)

    return redirect(url_for("view_page"))
@app.route("/set_target", methods=["GET", "POST"])
def set_target():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]
    data = load_data()

    if request.method == "POST":
        target = int(request.form["target"])

        if 40 <= target <= 100:
            data["users"][user]["target"] = target
            save_data(data)
            flash("Target updated!", "success")
            return redirect(url_for("home"))
        else:
            flash("Enter value between 40-100", "error")

    return render_template("set_target.html")
if __name__ == "__main__":
    app.run(debug=True)


