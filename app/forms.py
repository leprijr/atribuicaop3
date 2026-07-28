from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, FileField as WTFileField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from wtforms import TextAreaField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])


class UserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[Optional(), Email()])
    password = PasswordField('Senha', validators=[Optional(), Length(6, 128)])
    role = SelectField('Perfil', choices=[('admin', 'Administrador'), ('manager', 'Gestor')], validators=[DataRequired()])
    is_active = BooleanField('Ativo')


class SchoolForm(FlaskForm):
    name = StringField('Nome da Escola', validators=[DataRequired(), Length(1, 200)])
    code = StringField('Código', validators=[Optional(), Length(0, 20)])
    address = StringField('Endereço', validators=[Optional(), Length(0, 300)])
    phone = StringField('Telefone', validators=[Optional(), Length(0, 20)])


class ClassGroupForm(FlaskForm):
    name = StringField('Nome da Turma', validators=[DataRequired(), Length(1, 100)])
    school_id = SelectField('Escola', coerce=int, validators=[DataRequired()])
    period = SelectField('Período', choices=[
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite')
    ], validators=[DataRequired()])
    year = IntegerField('Ano', validators=[Optional()])
    grade = StringField('Série', validators=[Optional(), Length(0, 50)])


class SubjectForm(FlaskForm):
    name = StringField('Nome da Disciplina', validators=[DataRequired(), Length(1, 100)])
    code = StringField('Código', validators=[Optional(), Length(0, 20)])


class TeacherForm(FlaskForm):
    name = StringField('Nome do Professor', validators=[DataRequired(), Length(1, 200)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Telefone', validators=[Optional(), Length(0, 20)])
    registration_number = StringField('Matrícula', validators=[Optional(), Length(0, 50)])


class TeacherSubjectForm(FlaskForm):
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    classification = FloatField('Classificação', validators=[Optional(), NumberRange(0, 100)])


class ClassificationImportForm(FlaskForm):
    file = FileField('Arquivo (PDF, DOC, DOCX, XLSX, CSV)', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'xlsx', 'csv'], 'Formatos permitidos: PDF, DOC, DOCX, XLSX, CSV')
    ])


class AssignmentForm(FlaskForm):
    teacher_id = SelectField('Professor', coerce=int, validators=[DataRequired()])
    class_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    period = SelectField('Período', choices=[
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite')
    ], validators=[DataRequired()])
    year = IntegerField('Ano', validators=[Optional()])


class AutoAssignForm(FlaskForm):
    year = IntegerField('Ano', validators=[DataRequired()])
    submit = SubmitField('Executar Atribuição Automática')


class ReportFilterForm(FlaskForm):
    report_type = SelectField('Tipo de Relatório', choices=[
        ('teacher', 'Por Professor'),
        ('class', 'Por Turma'),
        ('school', 'Por Escola'),
        ('period', 'Por Período'),
        ('subject', 'Por Disciplina'),
        ('complete', 'Completo')
    ], validators=[DataRequired()])
    teacher_id = SelectField('Professor', coerce=int, validators=[Optional()])
    class_id = SelectField('Turma', coerce=int, validators=[Optional()])
    school_id = SelectField('Escola', coerce=int, validators=[Optional()])
    period = SelectField('Período', choices=[
        ('', 'Todos'),
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite')
    ], validators=[Optional()])
    subject_id = SelectField('Disciplina', coerce=int, validators=[Optional()])
    year = IntegerField('Ano', validators=[Optional()])


class SettingsForm(FlaskForm):
    app_name = StringField('Nome do Sistema', validators=[Optional(), Length(0, 200)])
    logo = FileField('Logotipo (PNG, JPG)', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Apenas imagens')])
    favicon = FileField('Favicon (ICO, PNG)', validators=[FileAllowed(['ico', 'png'], 'Apenas ICO ou PNG')])
    mail_server = StringField('Servidor SMTP', validators=[Optional()])
    mail_port = IntegerField('Porta SMTP', validators=[Optional()])
    mail_use_tls = BooleanField('Usar TLS')
    mail_username = StringField('Usuário SMTP', validators=[Optional()])
    mail_password = PasswordField('Senha SMTP', validators=[Optional()])
    mail_default_sender = StringField('Remetente Padrão', validators=[Optional(), Email()])


class EmailForm(FlaskForm):
    recipient = StringField('Destinatário', validators=[DataRequired(), Email()])
    subject = StringField('Assunto', validators=[DataRequired(), Length(1, 200)])
    message = TextAreaField('Mensagem', validators=[Optional()])
