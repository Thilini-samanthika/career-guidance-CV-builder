from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from .. import db
from ..models import Job, Applicant
import os, uuid
from werkzeug.utils import secure_filename

jobs_bp = Blueprint('jobs', __name__, template_folder='../templates')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@jobs_bp.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(company_id=current_user.id).all()
    return render_template('company_dashboard.html', jobs=jobs)

@jobs_bp.route('/job/new', methods=['GET','POST'])
@login_required
def new_job():
    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            flash("Title required","danger"); return redirect(url_for('jobs.new_job'))
        j = Job(title=title, location=request.form.get('location'), requirements=request.form.get('requirements'), company_id=current_user.id)
        db.session.add(j); db.session.commit()
        flash("Job posted","success"); return redirect(url_for('jobs.dashboard'))
    return render_template('new_job.html')

@jobs_bp.route('/job/<int:job_id>/applicants')
@login_required
def view_applicants(job_id):
    job = Job.query.get_or_404(job_id)
    if job.company_id != current_user.id:
        abort(403)
    applicants = Applicant.query.filter_by(job_id=job_id).all()
    return render_template('applicants_list.html', job=job, applicants=applicants)

@jobs_bp.route('/applicant/<int:applicant_id>')
@login_required
def applicant_profile(applicant_id):
    appl = Applicant.query.get_or_404(applicant_id)
    job = Job.query.get(appl.job_id)
    if job.company_id != current_user.id:
        abort(403)
    return render_template('applicant_profile.html', applicant=appl)

@jobs_bp.route('/download_cv/<int:applicant_id>')
@login_required
def download_cv(applicant_id):
    appl = Applicant.query.get_or_404(applicant_id)
    job = Job.query.get(appl.job_id)
    if job.company_id != current_user.id:
        abort(403)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], appl.cv_file, as_attachment=True)
