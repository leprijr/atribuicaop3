import os
from flask import current_app
from app.models import AppSetting


def inject_settings():
    settings = {}
    try:
        rows = AppSetting.query.all()
        for row in rows:
            settings[row.key] = row.value
    except Exception:
        pass

    logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logo', 'logo.png')
    favicon_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'favicon', 'favicon.ico')

    settings['logo_exists'] = os.path.exists(logo_path)
    settings['favicon_exists'] = os.path.exists(favicon_path)
    settings['app_name'] = settings.get('app_name', 'Sistema de Atribuição P3')

    return dict(settings=settings)
