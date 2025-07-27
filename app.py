from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail,Message

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# OAuth Blueprints
google_bp = make_google_blueprint(
    client_id="1035355435861-15ens4o1kc0sluhkvhdl0unc9htfc13q.apps.googleusercontent.com",
    client_secret="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",
    redirect_to="http://127.0.0.1:5000/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

facebook_bp = make_facebook_blueprint(
    client_id="YOUR_FACEBOOK_APP_ID",
    client_secret="YOUR_FACEBOOK_APP_SECRET",
    redirect_to="facebook_login"
)
app.register_blueprint(facebook_bp, url_prefix="/login")

# In-memory DB
users_db = {}
cv_storage = {}

# configure mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'

mail = Mail(app)

# --- Route for Forgot Password ---
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Check if email exists in users_db
        if email in users_db:
            # Send email
            token = generate_password_hash(email)  # You can use a proper token system
            reset_link = f'http://127.0.0.1:5000/reset-password/{token}'
            msg = Message('Reset Your Password',
                          sender='your_email@gmail.com',
                          recipients=[email])
            msg.body = f'Click the link below to reset your password:\n\n{reset_link}'
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email not found in our system.', 'danger')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')
# ------------------- ROUTES ----------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

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

@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "danger")
        return redirect(url_for('login'))

    user_info = resp.json()
    email = user_info["email"]
    name = user_info.get("name", email)

    if email not in users_db:
        users_db[email] = {
            'fullname': name,
            'email': email,
            'password': None
        }

    session['user_email'] = email
    session['user_name'] = name
    flash(f'Logged in with Google as {name}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/facebook')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))

    resp = facebook.get("/me?fields=name,email")
    if not resp.ok:
        flash("Failed to fetch user info from Facebook.", "danger")
        return redirect(url_for('login'))

    user_info = resp.json()
    email = user_info.get("email")
    name = user_info.get("name", email)

    if not email:
        flash("Facebook login failed: no email returned.", "danger")
        return redirect(url_for('login'))

    if email not in users_db:
        users_db[email] = {
            'fullname': name,
            'email': email,
            'password': None
        }

    session['user_email'] = email
    session['user_name'] = name
    flash(f'Logged in with Facebook as {name}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash("Please login to access the dashboard.", "warning")
        return redirect(url_for('login'))

    return render_template('dashboard.html', user_name=session['user_name'])

@app.route('/build_cv', methods=['GET'])
def build_cv():
    if 'user_email' not in session:
        flash("Please login to build your CV.", "warning")
        return redirect(url_for('login'))

    return render_template('build_cv.html')

@app.route('/submit_cv', methods=['POST'])
def submit_cv():
    if 'user_email' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    cv_data = {
        'fullname': request.form['fullname'],
        'email': request.form['email'],
        'phone': request.form.get('phone', ''),
        'linkedin': request.form.get('linkedin', ''),
        'education': request.form.get('education', ''),
        'skills': request.form.get('skills', ''),
        'template': request.form.get('template', 'modern')
    }

    cv_storage[session['user_email']] = cv_data
    flash("CV submitted successfully! (PDF generation coming soon)", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/reset-password/<token>', methods=['GET','POST'])
def reset_password(token):
    return f'This is a reset page.Token: {token}'

# ------------------- MAIN ----------------------

if __name__ == '__main__':
    app.run(debug=True)

