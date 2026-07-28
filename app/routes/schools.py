from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import School
from app.forms import SchoolForm
from app import db

bp = Blueprint('schools', __name__)


@bp.route('/')
@login_required
def list_schools():
    schools = School.query.order_by(School.name).all()
    return render_template('schools/list.html', schools=schools)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_school():
    form = SchoolForm()
    if form.validate_on_submit():
        school = School(
            name=form.name.data,
            code=form.code.data,
            address=form.address.data,
            phone=form.phone.data
        )
        db.session.add(school)
        db.session.commit()
        flash('Escola cadastrada com sucesso!', 'success')
        return redirect(url_for('schools.list_schools'))
    return render_template('schools/form.html', form=form, title='Nova Escola')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_school(id):
    school = db.session.get(School, id)
    if not school:
        flash('Escola não encontrada.', 'danger')
        return redirect(url_for('schools.list_schools'))
    form = SchoolForm(obj=school)
    if form.validate_on_submit():
        form.populate_obj(school)
        db.session.commit()
        flash('Escola atualizada com sucesso!', 'success')
        return redirect(url_for('schools.list_schools'))
    return render_template('schools/form.html', form=form, title='Editar Escola')


@bp.route('/delete/<int:id>')
@login_required
def delete_school(id):
    school = db.session.get(School, id)
    if school:
        db.session.delete(school)
        db.session.commit()
        flash('Escola excluída com sucesso!', 'success')
    else:
        flash('Escola não encontrada.', 'danger')
    return redirect(url_for('schools.list_schools'))
