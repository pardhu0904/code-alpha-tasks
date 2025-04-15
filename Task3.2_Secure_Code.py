from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import bcrypt
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Create users table if not exists
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Register a default user (run once)
def register_default_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    username = "admin"
    password = "password123"

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is None:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password.decode('utf-8')))
        conn.commit()

    conn.close()


# Run database setup
create_users_table()
register_default_user()


# Login Route
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Secure parameterized query
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            stored_hashed_password = user['password']

            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                session['username'] = username
                print("✅ Login successful! Redirecting to /home")  # Debug log
                return redirect(url_for('home'))  # Redirect to home page
            else:
                error = "Invalid credentials. Please try again."
        else:
            error = "Invalid credentials. Please try again."

    return render_template_string('''
        <h2>Login</h2>
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
        <p style="color: red;">{{ error }}</p>
    ''', error=error)


# Home Page (after login)
@app.route('/home')
def home():
    if 'username' not in session:
        print("❌ Unauthorized access! Redirecting to login.")  # Debug log
        return redirect(url_for('login'))  # Redirect if not logged in
    return render_template_string('''
        <h2>Welcome, {{ session['username'] }}!</h2>
        <p>You have successfully logged in.</p>
        <a href="{{ url_for('logout') }}">Logout</a>
    ''')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    print("👋 Logged out successfully!")  # Debug log
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
