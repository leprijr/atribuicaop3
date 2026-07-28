from datetime import datetime
from app.models import Assignment, Teacher, ClassGroup, Subject, School
from app import db


def get_report_data(report_type, teacher_id=None, class_id=None, school_id=None,
                    period=None, subject_id=None, year=None):
    query = Assignment.query

    if teacher_id and teacher_id != 0:
        query = query.filter_by(teacher_id=teacher_id)
    if class_id and class_id != 0:
        query = query.filter_by(class_id=class_id)
    if school_id and school_id != 0:
        school_classes = ClassGroup.query.filter_by(school_id=school_id).all()
        class_ids = [c.id for c in school_classes]
        query = query.filter(Assignment.class_id.in_(class_ids))
    if period:
        query = query.filter_by(period=period)
    if subject_id and subject_id != 0:
        query = query.filter_by(subject_id=subject_id)
    if year:
        query = query.filter_by(year=year)

    assignments = query.order_by(Assignment.year.desc(), Assignment.created_at.desc()).all()

    if report_type == 'teacher':
        return _group_by_teacher(assignments)
    elif report_type == 'class':
        return _group_by_class(assignments)
    elif report_type == 'school':
        return _group_by_school(assignments)
    elif report_type == 'period':
        return _group_by_period(assignments)
    elif report_type == 'subject':
        return _group_by_subject(assignments)
    else:
        return _complete_report(assignments)


def _group_by_teacher(assignments):
    headers = ['Professor', 'Disciplina', 'Escola', 'Turma', 'Período', 'Ano']
    rows = []
    for a in assignments:
        rows.append([
            a.teacher.name,
            a.subject.name,
            a.class_group.school.name,
            a.class_group.name,
            _period_label(a.period or a.class_group.period),
            a.year
        ])
    rows.sort(key=lambda r: r[0])
    return {'title': 'Relatório por Professor', 'headers': headers, 'rows': rows, 'type': 'teacher'}


def _group_by_class(assignments):
    headers = ['Escola', 'Turma', 'Período', 'Disciplina', 'Professor', 'Ano']
    rows = []
    for a in assignments:
        rows.append([
            a.class_group.school.name,
            a.class_group.name,
            _period_label(a.period or a.class_group.period),
            a.subject.name,
            a.teacher.name,
            a.year
        ])
    rows.sort(key=lambda r: (r[0], r[1]))
    return {'title': 'Relatório por Turma', 'headers': headers, 'rows': rows, 'type': 'class'}


def _group_by_school(assignments):
    headers = ['Escola', 'Turma', 'Período', 'Disciplina', 'Professor', 'Ano']
    rows = []
    for a in assignments:
        rows.append([
            a.class_group.school.name,
            a.class_group.name,
            _period_label(a.period or a.class_group.period),
            a.subject.name,
            a.teacher.name,
            a.year
        ])
    rows.sort(key=lambda r: (r[0], r[2], r[1]))
    return {'title': 'Relatório por Escola', 'headers': headers, 'rows': rows, 'type': 'school'}


def _group_by_period(assignments):
    headers = ['Período', 'Escola', 'Turma', 'Disciplina', 'Professor', 'Ano']
    rows = []
    for a in assignments:
        rows.append([
            _period_label(a.period or a.class_group.period),
            a.class_group.school.name,
            a.class_group.name,
            a.subject.name,
            a.teacher.name,
            a.year
        ])
    rows.sort(key=lambda r: r[0])
    return {'title': 'Relatório por Período', 'headers': headers, 'rows': rows, 'type': 'period'}


def _group_by_subject(assignments):
    headers = ['Disciplina', 'Professor', 'Escola', 'Turma', 'Período', 'Ano']
    rows = []
    for a in assignments:
        rows.append([
            a.subject.name,
            a.teacher.name,
            a.class_group.school.name,
            a.class_group.name,
            _period_label(a.period or a.class_group.period),
            a.year
        ])
    rows.sort(key=lambda r: r[0])
    return {'title': 'Relatório por Disciplina', 'headers': headers, 'rows': rows, 'type': 'subject'}


def _complete_report(assignments):
    headers = ['Professor', 'Disciplina', 'Escola', 'Turma', 'Período', 'Ano', 'Data Atribuição']
    rows = []
    for a in assignments:
        rows.append([
            a.teacher.name,
            a.subject.name,
            a.class_group.school.name,
            a.class_group.name,
            _period_label(a.period or a.class_group.period),
            a.year,
            a.created_at.strftime('%d/%m/%Y %H:%M') if a.created_at else ''
        ])
    rows.sort(key=lambda r: (r[0], r[2], r[3]))
    return {'title': 'Relatório Completo de Atribuições', 'headers': headers, 'rows': rows, 'type': 'complete'}


def _period_label(period):
    labels = {'manha': 'Manhã', 'tarde': 'Tarde', 'noite': 'Noite'}
    return labels.get(period, period)


def generate_report_pdf(data):
    from weasyprint import HTML
    from flask import render_template

    html = render_template('reports/pdf_template.html', data=data, generated_at=datetime.now())
    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
