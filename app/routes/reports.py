import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, Response, flash, redirect, url_for, send_file
from flask_login import login_required
from app.models import Assignment, Teacher, ClassGroup, Subject, School
from app.forms import ReportFilterForm, EmailForm
from app import db
from app.utils.report_generator import generate_report_pdf, get_report_data
from app.utils.email_sender import send_report_email

bp = Blueprint('reports', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportFilterForm()
    form.teacher_id.choices = [(0, 'Todos')] + [(t.id, t.name) for t in Teacher.query.order_by(Teacher.name).all()]
    form.class_id.choices = [(0, 'Todos')] + [(c.id, f'{c.school.name} - {c.name}') for c in ClassGroup.query.order_by(ClassGroup.name).all()]
    form.school_id.choices = [(0, 'Todos')] + [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    form.subject_id.choices = [(0, 'Todas')] + [(s.id, s.name) for s in Subject.query.order_by(Subject.name).all()]

    report_data = None
    if form.validate_on_submit():
        report_data = get_report_data(
            report_type=form.report_type.data,
            teacher_id=form.teacher_id.data,
            class_id=form.class_id.data,
            school_id=form.school_id.data,
            period=form.period.data,
            subject_id=form.subject_id.data,
            year=form.year.data
        )
    return render_template('reports/reports.html', form=form, report_data=report_data)


@bp.route('/export/pdf', methods=['POST'])
@login_required
def export_pdf():
    report_type = request.form.get('report_type')
    teacher_id = request.form.get('teacher_id', 0, type=int)
    class_id = request.form.get('class_id', 0, type=int)
    school_id = request.form.get('school_id', 0, type=int)
    period = request.form.get('period', '')
    subject_id = request.form.get('subject_id', 0, type=int)
    year = request.form.get('year', type=int)

    data = get_report_data(report_type, teacher_id, class_id, school_id, period, subject_id, year)
    pdf_bytes = generate_report_pdf(data)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'relatorio_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@bp.route('/export/csv', methods=['POST'])
@login_required
def export_csv():
    report_type = request.form.get('report_type')
    teacher_id = request.form.get('teacher_id', 0, type=int)
    class_id = request.form.get('class_id', 0, type=int)
    school_id = request.form.get('school_id', 0, type=int)
    period = request.form.get('period', '')
    subject_id = request.form.get('subject_id', 0, type=int)
    year = request.form.get('year', type=int)

    data = get_report_data(report_type, teacher_id, class_id, school_id, period, subject_id, year)

    output = io.StringIO()
    writer = csv.writer(output)
    if data.get('headers'):
        writer.writerow(data['headers'])
    for row in data.get('rows', []):
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=relatorio_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )


@bp.route('/email', methods=['POST'])
@login_required
def email_report():
    recipient = request.form.get('recipient')
    subject = request.form.get('subject')
    message = request.form.get('message', '')
    report_type = request.form.get('email_report_type')
    teacher_id = request.form.get('email_teacher_id', 0, type=int)
    class_id = request.form.get('email_class_id', 0, type=int)
    school_id = request.form.get('email_school_id', 0, type=int)
    period = request.form.get('email_period', '')
    subject_id_val = request.form.get('email_subject_id', 0, type=int)
    year = request.form.get('email_year', type=int)

    if not recipient or not subject:
        flash('Destinatário e assunto são obrigatórios.', 'danger')
        return redirect(url_for('reports.reports'))

    data = get_report_data(report_type, teacher_id, class_id, school_id, period, subject_id_val, year)
    pdf_bytes = generate_report_pdf(data)

    try:
        send_report_email(recipient, subject, message, pdf_bytes)
        flash('Relatório enviado por e-mail com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar e-mail: {str(e)}', 'danger')

    return redirect(url_for('reports.reports'))
