import sqlite3
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)


# Function to establish a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Initialize Database with Multiple Users (Run Once)
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create 'users' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Insert multiple users (Passwords are ignored for authentication)
    users = [
        ('admin', 'admin123'),
        ('user1', 'password1'),
        ('user2', 'password2'),
        ('hacker', 'letmein'),
    ]

    try:
        cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users)
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ignore errors if users already exist

    conn.close()


# Run database initialization
initialize_db()


# Vulnerable Login Page (Bypasses Password Check)
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Ignored for authentication

        conn = get_db_connection()
        cursor = conn.cursor()

        # 🚨 SQL Injection Vulnerability - No parameterized queries
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            # Authentication bypass - Password is ignored
            return redirect(url_for('home', username=username))
        else:
            error = "Invalid credentials"

    # XSS Vulnerability - Error message is directly injected
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Page</title>
        </head>
        <body>
            <h2>Login</h2>
            <form method="post">
                <label>Username:</label>
                <input type="text" name="username" required><br>

                <label>Password:</label>
                <input type="password" name="password" required><br>

                <input type="submit" value="Login">
            </form>
            <p style="color:red;">{{ error }}</p>  <!-- 🚨 XSS Risk -->
        </body>
        </html>
    ''', error=error)


# Insecure Home Page
@app.route('/home')
def home():
    username = request.args.get('username', 'Guest')

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home Page</title>
        </head>
        <body>
            <h2>Welcome, {{ username }}!</h2>  <!-- XSS Risk -->
            <p>You have successfully logged in.</p>
            <a href="{{ url_for('login') }}">Logout</a>
        </body>
        </html>
    ''', username=username)


if __name__ == '__main__':
    app.run(debug=True)
