from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from ..models import Company
from .. import db, login_manager

company_bp = Blueprint('company', __name__, template_folder='../templates')

@login_manager.user_loader
def load_user(user_id):
    return Company.query.get(int(user_id))

@company_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pw = request.form.get('password')
        confirm = request.form.get('confirm')
        if not (name and email and pw and confirm):
            flash("All fields required","danger"); return redirect(url_for('company.register'))
        if pw != confirm:
            flash("Passwords do not match","danger"); return redirect(url_for('company.register'))
        if Company.query.filter_by(email=email).first():
            flash("Email already used","warning"); return redirect(url_for('company.register'))
        hashed = generate_password_hash(pw)
        c = Company(name=name, email=email, password=hashed, approved=False)
        db.session.add(c); db.session.commit()
        flash("Registered; wait for admin approval","success")
        return redirect(url_for('company.login'))
    return render_template('company_register.html')

@company_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pw = request.form.get('password')
        c = Company.query.filter_by(email=email).first()
        if c and check_password_hash(c.password, pw):
            if not c.approved:
                flash("Account awaiting admin approval","warning"); return redirect(url_for('company.login'))
            login_user(c)
            flash(f"Welcome {c.name}","success")
            return redirect(url_for('jobs.dashboard'))
        flash("Invalid credentials","danger"); return redirect(url_for('company.login'))
    return render_template('company_login.html')

@company_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out","info")
    return redirect(url_for('company.login'))
