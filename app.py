from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ================== APP CONFIG ==================
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "pm_internship_secure_key"
DB_NAME = "database.db"

# ================== DB CONNECTION ==================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ================== DB INIT ==================
def init_db():
    db = get_db()

    # USERS
    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # USER PROFILE
    db.execute("""
    CREATE TABLE IF NOT EXISTS user_profile(
        user_id INTEGER,
        mobile TEXT,
        dob TEXT,
        gender TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        qualification TEXT,
        degree TEXT,
        specialization TEXT,
        college TEXT,
        passing_year TEXT,
        cgpa TEXT
    )
    """)

    # USER EXPERIENCE
    db.execute("""
    CREATE TABLE IF NOT EXISTS user_experience(
        user_id INTEGER,
        pm_domain TEXT,
        company_type TEXT,
        duration TEXT,
        skills TEXT,
        linkedin TEXT,
        portfolio TEXT,
        role_focus TEXT,
        tools TEXT,
        mode TEXT,
        stipend TEXT
    )
    """)

    # INTERNSHIPS
    db.execute("""
    CREATE TABLE IF NOT EXISTS internships(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        role TEXT,
        domain TEXT,
        skills TEXT,
        mode TEXT,
        duration TEXT,
        company_type TEXT,
        stipend TEXT,
        apply_link TEXT
    )
    """)

    # Ensure apply_link column exists (safe upgrade)
    columns = db.execute("PRAGMA table_info(internships)").fetchall()
    column_names = [col["name"] for col in columns]
    if "apply_link" not in column_names:
        db.execute("ALTER TABLE internships ADD COLUMN apply_link TEXT")

    # Insert dataset only once
    count = db.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
    if count == 0:
        internships = [
            ("Zoho","PM Intern","SaaS","excel,sql,user research","Remote","3 Months","Startup","Paid","https://careers.zoho.com/"),
            ("Freshworks","Associate PM","SaaS","jira,roadmap,sql","Hybrid","6 Months","MNC","Paid","https://careers.freshworks.com/"),
            ("Byjus","Product Intern","EdTech","market analysis,excel","On-site","6 Months","Startup","Paid","https://byjus.com/careers/"),
            ("Razorpay","PM Intern","FinTech","sql,analytics","Remote","3 Months","Startup","Paid","https://razorpay.com/jobs/"),
            ("Paytm","APM Intern","FinTech","user research,excel","Hybrid","6 Months","MNC","Paid","https://paytm.com/careers/"),
            ("Swiggy","Product Ops Intern","E-commerce","ops,data analysis","On-site","3 Months","Startup","Paid","https://careers.swiggy.com/"),
            ("Amazon","Product Analyst","E-commerce","sql,tableau","Hybrid","6 Months","MNC","Paid","https://amazon.jobs/"),
            ("Meesho","PM Intern","E-commerce","user research,figma","Remote","3 Months","Startup","Paid","https://careers.meesho.com/"),
            ("Unacademy","Product Intern","EdTech","market research","Remote","1 Month","Startup","Unpaid","https://unacademy.com/careers"),
            ("Coursera","PM Intern","EdTech","data analysis","Remote","3 Months","MNC","Paid","https://careers.coursera.com/"),
            ("Infosys","Product Analyst","Tech Product","excel,sql","On-site","6 Months","MNC","Paid","https://www.infosys.com/careers/"),
            ("TCS","PMO Intern","Tech Product","documentation","On-site","3 Months","MNC","Paid","https://www.tcs.com/careers"),
            ("NIC","Digital Product Intern","Government / PSU","excel","On-site","6 Months","Government / PSU","Paid","https://www.nic.in/careers/"),
            ("UIDAI","Product Research Intern","Government / PSU","research","On-site","3 Months","Government / PSU","Paid","https://uidai.gov.in/en/about-uidai/careers.html"),
            ("Flipkart","PM Intern","E-commerce","roadmap planning","Hybrid","6 Months","MNC","Paid","https://www.flipkartcareers.com/"),
            ("PhonePe","APM Intern","FinTech","sql,data analysis","Remote","3 Months","Startup","Paid","https://www.phonepe.com/careers/"),
            ("Cred","Product Strategy Intern","FinTech","business strategy","Hybrid","3 Months","Startup","Paid","https://cred.club/careers"),
            ("Zomato","Product Intern","E-commerce","market analysis","On-site","3 Months","Startup","Paid","https://www.zomato.com/careers"),
            ("Microsoft","PM Intern","Tech Product","data,research","Hybrid","6 Months","MNC","Paid","https://careers.microsoft.com/"),
            ("Google","Associate PM Intern","Tech Product","user research","Hybrid","6 Months","MNC","Paid","https://careers.google.com/")
        ]

        db.executemany("""
        INSERT INTO internships(company,role,domain,skills,mode,duration,company_type,stipend,apply_link)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, internships)

    db.commit()
    db.close()

init_db()

# ================== ROUTES ==================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (
                request.form["name"],
                request.form["email"],
                generate_password_hash(request.form["password"])
            )
        )
        db.commit()
        db.close()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (request.form["email"],)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            return redirect(url_for("user_details"))
        return "Invalid login"
    return render_template("login.html")

@app.route("/user_details", methods=["GET","POST"])
def user_details():
    if request.method == "POST":
        db = get_db()
        db.execute("""
        INSERT INTO user_profile VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            session["user_id"],
            request.form["mobile"],
            request.form["dob"],
            request.form["gender"],
            request.form["city"],
            request.form["state"],
            request.form["country"],
            request.form["qualification"],
            request.form["degree"],
            request.form["specialization"],
            request.form["college"],
            request.form["passing_year"],
            request.form["cgpa"]
        ))
        db.commit()
        db.close()
        return redirect(url_for("user_experience"))
    return render_template("user_details.html")

@app.route("/user_experience", methods=["GET","POST"])
def user_experience():
    if request.method == "POST":
        db = get_db()
        db.execute("""
        INSERT INTO user_experience VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            session["user_id"],
            request.form["pm_domain"],
            request.form["company_type"],
            request.form["duration"],
            request.form["skills"],
            request.form["linkedin"],
            request.form["portfolio"],
            request.form["role_focus"],
            request.form["tools"],
            request.form["mode"],
            request.form["stipend"]
        ))
        db.commit()
        db.close()
        return redirect(url_for("results"))
    return render_template("user_experience.html")

@app.route("/results")
def results():
    db = get_db()

    user = db.execute(
        "SELECT * FROM user_experience WHERE user_id=? ORDER BY rowid DESC LIMIT 1",
        (session["user_id"],)
    ).fetchone()

    internships = db.execute("SELECT * FROM internships").fetchall()
    results = []

    user_skills = set(s.strip().lower() for s in user["skills"].split(","))

    for i in internships:
        score = 0
        intern_skills = set(s.strip().lower() for s in i["skills"].split(","))

        if i["domain"] == user["pm_domain"]:
            score += 5

        score += len(user_skills & intern_skills) * 3

        if i["company_type"] == user["company_type"]:
            score += 2

        if i["duration"] == user["duration"]:
            score += 2

        if i["mode"] == user["mode"]:
            score += 2

        if user["stipend"] == "Any":
            score += 1
        elif i["stipend"] == user["stipend"]:
            score += 2

        if user["role_focus"].lower() in i["role"].lower():
            score += 2

        if score > 0:
            results.append({"intern": i, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)
    db.close()

    return render_template("results.html", internships=results[:3])

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["email"] == "sudhan2006@gmail.com" and request.form["password"] == "sudhan2006":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        return "Invalid Admin"
    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    db.close()
    return render_template("admin_dashboard.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)