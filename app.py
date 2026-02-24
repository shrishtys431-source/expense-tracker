from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        amount = float(request.form["amount"])
        category = request.form["category"]

        cursor.execute(
            "INSERT INTO expenses (title, amount, category) VALUES (?, ?, ?)",
            (title, amount, category)
        )
        conn.commit()
        return redirect("/")

    search = request.args.get("search")
    sort = request.args.get("sort")

    query = "SELECT * FROM expenses"

    if search:
        query += f" WHERE title LIKE '%{search}%'"

    if sort == "high":
        query += " ORDER BY amount DESC"
    elif sort == "low":
        query += " ORDER BY amount ASC"

    cursor.execute(query)
    expenses = cursor.fetchall()

    total = sum(e[2] for e in expenses)

    # Category totals
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_totals = cursor.fetchall()

    conn.close()

    return render_template("index.html",
                           expenses=expenses,
                           total=total,
                           category_totals=category_totals)

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    new_title = request.form["title"]
    new_amount = float(request.form["amount"])
    new_category = request.form["category"]

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE expenses
        SET title=?, amount=?, category=?
        WHERE id=?
    """, (new_title, new_amount, new_category, id))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)