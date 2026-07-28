from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Assignment, Teacher, ClassGroup, Subject, TeacherSubject, School
from app.forms import AssignmentForm, AutoAssignForm
from app import db

bp = Blueprint('assignments', __name__)


@bp.route('/')
@login_required
def list_assignments():
    year = request.args.get('year', type=int)
    query = Assignment.query
    if year:
        query = query.filter_by(year=year)
    assignments = query.order_by(Assignment.year.desc(), Assignment.created_at.desc()).all()
    years = db.session.query(Assignment.year).distinct().order_by(Assignment.year.desc()).all()
    return render_template('assignments/list.html', assignments=assignments, years=[y[0] for y in years])


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_assignment():
    form = AssignmentForm()
    form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.order_by(Teacher.name).all()]
    form.class_id.choices = [(c.id, f'{c.school.name} - {c.name} ({c.period})') for c in ClassGroup.query.order_by(ClassGroup.name).all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.order_by(Subject.name).all()]

    if form.validate_on_submit():
        existing = Assignment.query.filter_by(
            teacher_id=form.teacher_id.data,
            class_id=form.class_id.data,
            subject_id=form.subject_id.data,
            year=form.year.data or Assignment.year.default.arg
        ).first()
        if existing:
            flash('Esta atribuição já existe!', 'warning')
            return redirect(url_for('assignments.list_assignments'))

        assignment = Assignment(
            teacher_id=form.teacher_id.data,
            class_id=form.class_id.data,
            subject_id=form.subject_id.data,
            period=form.period.data,
            year=form.year.data or Assignment.year.default.arg,
            created_by=current_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Atribuição registrada com sucesso!', 'success')
        return redirect(url_for('assignments.list_assignments'))
    return render_template('assignments/form.html', form=form, title='Nova Atribuição')


@bp.route('/delete/<int:id>')
@login_required
def delete_assignment(id):
    assignment = db.session.get(Assignment, id)
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        flash('Atribuição removida com sucesso!', 'success')
    else:
        flash('Atribuição não encontrada.', 'danger')
    return redirect(url_for('assignments.list_assignments'))


@bp.route('/auto', methods=['GET', 'POST'])
@login_required
def auto_assign():
    form = AutoAssignForm()
    if form.validate_on_submit():
        year = form.year.data
        assignments_created = _run_auto_assign(year)
        flash(f'Atribuição automática concluída! {assignments_created} atribuições criadas.', 'success')
        return redirect(url_for('assignments.list_assignments'))
    return render_template('assignments/auto.html', form=form)


def _run_auto_assign(year):
    Assignment.query.filter_by(year=year).delete()
    db.session.commit()

    classes = ClassGroup.query.filter_by(year=year, is_active=True).all()
    count = 0

    for cls in classes:
        subjects_with_teachers = {}
        all_ts = TeacherSubject.query.all()
        for ts in all_ts:
            subj = ts.subject_id
            if subj not in subjects_with_teachers:
                subjects_with_teachers[subj] = []
            subjects_with_teachers[subj].append(ts)

        for subj_id, ts_list in subjects_with_teachers.items():
            sorted_teachers = sorted(ts_list, key=lambda x: x.classification, reverse=True)

            for ts in sorted_teachers:
                already_assigned = Assignment.query.filter_by(
                    teacher_id=ts.teacher_id, class_id=cls.id, year=year
                ).first()
                if not already_assigned:
                    assignment = Assignment(
                        teacher_id=ts.teacher_id,
                        class_id=cls.id,
                        subject_id=subj_id,
                        period=cls.period,
                        year=year,
                        created_by=current_user.id
                    )
                    db.session.add(assignment)
                    count += 1
                    break

    db.session.commit()
    return count


@bp.route('/api/teachers-by-subject/<int:subject_id>')
@login_required
def api_teachers_by_subject(subject_id):
    ts_list = TeacherSubject.query.filter_by(subject_id=subject_id).all()
    result = [{
        'id': ts.teacher.id,
        'name': ts.teacher.name,
        'classification': ts.classification
    } for ts in ts_list]
    return jsonify(result)


@bp.route('/api/classes-by-school/<int:school_id>')
@login_required
def api_classes_by_school(school_id):
    classes = ClassGroup.query.filter_by(school_id=school_id).all()
    result = [{
        'id': c.id,
        'name': f'{c.name} ({c.period})',
        'period': c.period
    } for c in classes]
    return jsonify(result)
