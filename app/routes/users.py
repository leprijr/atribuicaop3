from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import User
from app.forms import UserForm
from app import db

bp = Blueprint('users', __name__)


@bp.route('/')
@login_required
def list_users():
    users = User.query.order_by(User.username).all()
    return render_template('users/list.html', users=users)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        if not form.password.data:
            flash('Senha é obrigatória para novo usuário.', 'danger')
            return render_template('users/form.html', form=form, title='Novo Usuário')
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', form=form, title='Novo Usuário')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = db.session.get(User, id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('users.list_users'))
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', form=form, title='Editar Usuário')


@bp.route('/delete/<int:id>')
@login_required
def delete_user(id):
    user = db.session.get(User, id)
    if user and user.username == 'admin':
        flash('Não é possível excluir o usuário admin.', 'danger')
        return redirect(url_for('users.list_users'))
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Usuário excluído com sucesso!', 'success')
    else:
        flash('Usuário não encontrado.', 'danger')
    return redirect(url_for('users.list_users'))
