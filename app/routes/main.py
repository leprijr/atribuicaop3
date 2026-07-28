from flask import Blueprint, render_template
from flask_login import login_required
from app.models import School, ClassGroup, Teacher, Subject, Assignment, User

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def dashboard():
    stats = {
        'schools': School.query.count(),
        'classes': ClassGroup.query.count(),
        'teachers': Teacher.query.count(),
        'subjects': Subject.query.count(),
        'assignments': Assignment.query.count(),
        'users': User.query.count(),
    }
    recent_assignments = Assignment.query.order_by(Assignment.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', stats=stats, recent_assignments=recent_assignments)
