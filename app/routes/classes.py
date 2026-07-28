from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import ClassGroup, School
from app.forms import ClassGroupForm
from app import db

bp = Blueprint('classes', __name__)


@bp.route('/')
@login_required
def list_classes():
    school_id = request.args.get('school_id', type=int)
    query = ClassGroup.query
    if school_id:
        query = query.filter_by(school_id=school_id)
    classes = query.order_by(ClassGroup.school_id, ClassGroup.name).all()
    schools = School.query.order_by(School.name).all()
    return render_template('classes/list.html', classes=classes, schools=schools, selected_school=school_id)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_class():
    form = ClassGroupForm()
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        cls = ClassGroup(
            name=form.name.data,
            school_id=form.school_id.data,
            period=form.period.data,
            year=form.year.data or ClassGroup.year.default.arg,
            grade=form.grade.data
        )
        db.session.add(cls)
        db.session.commit()
        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('classes.list_classes'))
    return render_template('classes/form.html', form=form, title='Nova Turma')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_class(id):
    cls = db.session.get(ClassGroup, id)
    if not cls:
        flash('Turma não encontrada.', 'danger')
        return redirect(url_for('classes.list_classes'))
    form = ClassGroupForm(obj=cls)
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    if form.validate_on_submit():
        form.populate_obj(cls)
        db.session.commit()
        flash('Turma atualizada com sucesso!', 'success')
        return redirect(url_for('classes.list_classes'))
    return render_template('classes/form.html', form=form, title='Editar Turma')


@bp.route('/delete/<int:id>')
@login_required
def delete_class(id):
    cls = db.session.get(ClassGroup, id)
    if cls:
        db.session.delete(cls)
        db.session.commit()
        flash('Turma excluída com sucesso!', 'success')
    else:
        flash('Turma não encontrada.', 'danger')
    return redirect(url_for('classes.list_classes'))
