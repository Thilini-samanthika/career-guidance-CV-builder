from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')  # open login page as homepage

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/build_cv')
def build_cv():
    return render_template('cvbuilder.html')

if __name__ == '__main__':
    app.run(debug=True)
