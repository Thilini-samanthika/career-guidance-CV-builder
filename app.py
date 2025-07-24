from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Temporary in-memory storage (you can later connect to MySQL or SQLite)
users_db = {}
cv_storage = {}

# ---------------------------------------
@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        if email in users_db:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))

        users_db[email] = {
            'fullname': fullname,
            'email': email,
            'password': generate_password_hash(password)
        }

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_db.get(email)
        if user and check_password_hash(user['password'], password):
            session['user_email'] = user['email']
            session['user_name'] = user['fullname']
            flash(f'Welcome, {user["fullname"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash("Please login to access the dashboard.", "warning")
        return redirect(url_for('login'))

    return render_template('dashboard.html', user_name=session['user_name'])

# ---------------------------------------
@app.route('/build_cv', methods=['GET'])
def build_cv():
    if 'user_email' not in session:
        flash("Please login to build your CV.", "warning")
        return redirect(url_for('login'))

    return render_template('build_cv.html')

# ---------------------------------------
@app.route('/submit_cv', methods=['POST'])
def submit_cv():
    if 'user_email' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    # Get form data
    cv_data = {
        'fullname': request.form['fullname'],
        'email': request.form['email'],
        'phone': request.form.get('phone', ''),
        'linkedin': request.form.get('linkedin', ''),
        'education': request.form.get('education', ''),
        'skills': request.form.get('skills', ''),
        'template': request.form.get('template', 'modern')
    }

    # Save CV data in memory
    cv_storage[session['user_email']] = cv_data

    flash("CV submitted successfully! (PDF generation coming soon)", "success")
    return redirect(url_for('dashboard'))

# ---------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# ---------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

