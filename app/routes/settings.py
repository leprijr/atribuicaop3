import os
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.models import School, ClassGroup, Subject, Teacher, Assignment, User, AppSetting
from app.forms import SettingsForm
from app import db

bp = Blueprint('settings', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()

    settings_data = {}
    for s in AppSetting.query.all():
        settings_data[s.key] = s.value

    if form.validate_on_submit():
        if form.app_name.data:
            _set_setting('app_name', form.app_name.data)

        if form.logo.data:
            logo_file = form.logo.data
            ext = logo_file.filename.rsplit('.', 1)[1].lower() if '.' in logo_file.filename else 'png'
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logo', f'logo.{ext}')
            logo_file.save(logo_path)
            _set_setting('logo_ext', ext)
            flash('Logotipo atualizado com sucesso!', 'success')

        if form.favicon.data:
            fav_file = form.favicon.data
            ext = fav_file.filename.rsplit('.', 1)[1].lower() if '.' in fav_file.filename else 'ico'
            fav_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'favicon', f'favicon.{ext}')
            fav_file.save(fav_path)
            _set_setting('favicon_ext', ext)
            flash('Favicon atualizado com sucesso!', 'success')

        if form.mail_server.data:
            _set_setting('mail_server', form.mail_server.data)
        if form.mail_port.data:
            _set_setting('mail_port', str(form.mail_port.data))
        _set_setting('mail_use_tls', '1' if form.mail_use_tls.data else '0')
        if form.mail_username.data:
            _set_setting('mail_username', form.mail_username.data)
        if form.mail_password.data:
            _set_setting('mail_password', form.mail_password.data)
        if form.mail_default_sender.data:
            _set_setting('mail_default_sender', form.mail_default_sender.data)

        db.session.commit()
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('settings.settings'))

    form.app_name.data = settings_data.get('app_name', 'Sistema de Atribuição P3')
    form.mail_server.data = settings_data.get('mail_server', '')
    form.mail_port.data = settings_data.get('mail_port', 587, type=int) if settings_data.get('mail_port') else None
    form.mail_use_tls.data = settings_data.get('mail_use_tls', '1') == '1'
    form.mail_username.data = settings_data.get('mail_username', '')
    form.mail_default_sender.data = settings_data.get('mail_default_sender', '')

    return render_template('settings/settings.html', form=form)


def _set_setting(key, value):
    s = AppSetting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        s = AppSetting(key=key, value=value)
        db.session.add(s)


@bp.route('/subjects')
@login_required
def list_subjects():
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('settings/subjects.html', subjects=subjects, form=None)


@bp.route('/subjects/new', methods=['GET', 'POST'])
@login_required
def new_subject():
    from app.forms import SubjectForm
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data, code=form.code.data)
        db.session.add(subject)
        db.session.commit()
        flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('settings.list_subjects'))
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('settings/subjects.html', subjects=subjects, form=form)


@bp.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    from app.forms import SubjectForm
    subject = db.session.get(Subject, id)
    if not subject:
        flash('Disciplina não encontrada.', 'danger')
        return redirect(url_for('settings.list_subjects'))
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        form.populate_obj(subject)
        db.session.commit()
        flash('Disciplina atualizada com sucesso!', 'success')
        return redirect(url_for('settings.list_subjects'))
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('settings/subjects.html', subjects=subjects, form=form, edit_id=id)


@bp.route('/subjects/delete/<int:id>')
@login_required
def delete_subject(id):
    subject = db.session.get(Subject, id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash('Disciplina excluída com sucesso!', 'success')
    else:
        flash('Disciplina não encontrada.', 'danger')
    return redirect(url_for('settings.list_subjects'))
