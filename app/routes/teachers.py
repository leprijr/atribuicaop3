import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.models import Teacher, Subject, TeacherSubject
from app.forms import TeacherForm, TeacherSubjectForm, ClassificationImportForm
from app import db
from app.utils.file_parser import parse_classification_file

bp = Blueprint('teachers', __name__)


@bp.route('/')
@login_required
def list_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template('teachers/list.html', teachers=teachers)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        teacher = Teacher(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            registration_number=form.registration_number.data
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Professor cadastrado com sucesso!', 'success')
        return redirect(url_for('teachers.list_teachers'))
    return render_template('teachers/form.html', form=form, title='Novo Professor')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    teacher = db.session.get(Teacher, id)
    if not teacher:
        flash('Professor não encontrado.', 'danger')
        return redirect(url_for('teachers.list_teachers'))
    form = TeacherForm(obj=teacher)
    if form.validate_on_submit():
        form.populate_obj(teacher)
        db.session.commit()
        flash('Professor atualizado com sucesso!', 'success')
        return redirect(url_for('teachers.list_teachers'))
    return render_template('teachers/form.html', form=form, title='Editar Professor')


@bp.route('/delete/<int:id>')
@login_required
def delete_teacher(id):
    teacher = db.session.get(Teacher, id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        flash('Professor excluído com sucesso!', 'success')
    else:
        flash('Professor não encontrado.', 'danger')
    return redirect(url_for('teachers.list_teachers'))


@bp.route('/subjects/<int:id>', methods=['GET', 'POST'])
@login_required
def manage_subjects(id):
    teacher = db.session.get(Teacher, id)
    if not teacher:
        flash('Professor não encontrado.', 'danger')
        return redirect(url_for('teachers.list_teachers'))

    form = TeacherSubjectForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.order_by(Subject.name).all()]

    if form.validate_on_submit():
        existing = TeacherSubject.query.filter_by(
            teacher_id=id, subject_id=form.subject_id.data
        ).first()
        if existing:
            existing.classification = form.classification.data
        else:
            ts = TeacherSubject(
                teacher_id=id,
                subject_id=form.subject_id.data,
                classification=form.classification.data or 0
            )
            db.session.add(ts)
        db.session.commit()
        flash('Disciplina vinculada com sucesso!', 'success')
        return redirect(url_for('teachers.manage_subjects', id=id))

    subjects = TeacherSubject.query.filter_by(teacher_id=id).all()
    return render_template('teachers/subjects.html', teacher=teacher, subjects=subjects, form=form)


@bp.route('/subjects/remove/<int:id>')
@login_required
def remove_subject(id):
    ts = db.session.get(TeacherSubject, id)
    if ts:
        teacher_id = ts.teacher_id
        db.session.delete(ts)
        db.session.commit()
        flash('Disciplina removida do professor.', 'success')
        return redirect(url_for('teachers.manage_subjects', id=teacher_id))
    flash('Vínculo não encontrado.', 'danger')
    return redirect(url_for('teachers.list_teachers'))


@bp.route('/classifications/import', methods=['GET', 'POST'])
@login_required
def import_classifications():
    form = ClassificationImportForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'classifications', filename)
        f.save(upload_path)

        try:
            result = parse_classification_file(upload_path)
            imported = 0
            errors = []
            for row in result:
                teacher = Teacher.query.filter_by(name=row['teacher']).first()
                if not teacher:
                    teacher = Teacher(name=row['teacher'])
                    db.session.add(teacher)
                    db.session.flush()

                subject = Subject.query.filter_by(name=row['subject']).first()
                if not subject:
                    subject = Subject(name=row['subject'])
                    db.session.add(subject)
                    db.session.flush()

                existing = TeacherSubject.query.filter_by(
                    teacher_id=teacher.id, subject_id=subject.id
                ).first()
                if existing:
                    existing.classification = row['classification']
                else:
                    ts = TeacherSubject(
                        teacher_id=teacher.id,
                        subject_id=subject.id,
                        classification=row['classification']
                    )
                    db.session.add(ts)
                imported += 1
            db.session.commit()
            flash(f'Importação concluída! {imported} registros processados.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
        finally:
            if os.path.exists(upload_path):
                os.remove(upload_path)

        return redirect(url_for('teachers.list_teachers'))

    return render_template('teachers/import_classifications.html', form=form)
