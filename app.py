from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('/app/database.db')  # Adjust path for container volume
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    user TEXT,
                    date TEXT,
                    category TEXT,
                    amount REAL)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect('/app/database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists. Try another."
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('/app/database.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (user,))
        result = c.fetchone()
        conn.close()
        if result and check_password_hash(result[0], pwd):
            session['username'] = user
            return redirect(url_for('expenses'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    today = datetime.today()
    month = today.month
    year = today.year
    days = range(1, 32)
    categories = ['Food', 'Electricity', 'Rent', 'Wifi', 'Others']

    if request.method == 'POST':
        conn = sqlite3.connect('/app/database.db')
        c = conn.cursor()
        for day in days:
            for cat in categories:
                key = f"{day}_{cat}"
                val = request.form.get(key)
                if val:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    c.execute("INSERT INTO expenses (user, date, category, amount) VALUES (?, ?, ?, ?)",
                              (username, date_str, cat, float(val)))
        conn.commit()
        conn.close()
        return redirect(url_for('expenses'))

    return render_template('expenses.html', days=days, categories=categories)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
