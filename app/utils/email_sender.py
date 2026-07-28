import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from app.models import AppSetting


def _get_mail_config():
    config = {}
    for s in AppSetting.query.all():
        config[s.key] = s.value
    return config


def send_report_email(recipient, subject, message, pdf_bytes):
    cfg = _get_mail_config()
    smtp_server = cfg.get('mail_server', '')
    smtp_port = int(cfg.get('mail_port', 587))
    smtp_user = cfg.get('mail_username', '')
    smtp_pass = cfg.get('mail_password', '')
    smtp_tls = cfg.get('mail_use_tls', '1') == '1'
    sender = cfg.get('mail_default_sender', smtp_user)

    if not smtp_server or not smtp_user:
        raise ValueError('Servidor SMTP não configurado. Acesse Configurações para definir.')

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    if message:
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

    attachment = MIMEBase('application', 'pdf')
    attachment.set_payload(pdf_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header(
        'Content-Disposition',
        'attachment',
        filename='relatorio_atribuicao.pdf'
    )
    msg.attach(attachment)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls() if smtp_tls else None
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
