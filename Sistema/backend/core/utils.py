# Sistema/backend/core/utils.py

import smtplib
from email.mime.text import MIMEText
from .models import NotificationLog, ConfiguracaoInicial
import requests

def send_email(to_email, subject, body):
    """
    Envia e-mail usando configurações de ConfiguracaoInicial.
    Registra em NotificationLog.
    """
    try:
        config = ConfiguracaoInicial.objects.get(pk=1)
    except ConfiguracaoInicial.DoesNotExist:
        NotificationLog.objects.create(
            type='EMAIL',
            to=to_email,
            subject=subject,
            body=body,
            success=False,
            error_message='Configuração de SMTP não encontrada.'
        )
        return False

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = config.smtp_user
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10)
        if config.smtp_use_tls:
            server.starttls()
        server.login(config.smtp_user, config.smtp_password)
        server.sendmail(config.smtp_user, [to_email], msg.as_string())
        server.quit()
        NotificationLog.objects.create(
            type='EMAIL',
            to=to_email,
            subject=subject,
            body=body,
            success=True
        )
        return True
    except Exception as e:
        NotificationLog.objects.create(
            type='EMAIL',
            to=to_email,
            subject=subject,
            body=body,
            success=False,
            error_message=str(e)
        )
        return False


def send_whatsapp(phone_number, message):
    """
    Envia mensagem via API WhatsApp usando configurações de ConfiguracaoInicial.
    Registra em NotificationLog.
    Assumimos que `whatsapp_api_url` aceita POST JSON: {'to': phone_number, 'message': message, 'api_key': '...'}
    """
    try:
        config = ConfiguracaoInicial.objects.get(pk=1)
    except ConfiguracaoInicial.DoesNotExist:
        NotificationLog.objects.create(
            type='WHATSAPP',
            to=phone_number,
            subject=message[:50],
            body=message,
            success=False,
            error_message='Configuração WhatsApp não encontrada.'
        )
        return False

    payload = {
        'to': phone_number,
        'message': message,
        'api_key': config.whatsapp_api_key
    }
    try:
        resp = requests.post(config.whatsapp_api_url, json=payload, timeout=10)
        if resp.status_code == 200:
            NotificationLog.objects.create(
                type='WHATSAPP',
                to=phone_number,
                subject=message[:50],
                body=message,
                success=True
            )
            return True
        else:
            error_msg = f'API retornou {resp.status_code}: {resp.text}'
            NotificationLog.objects.create(
                type='WHATSAPP',
                to=phone_number,
                subject=message[:50],
                body=message,
                success=False,
                error_message=error_msg
            )
            return False
    except Exception as e:
        NotificationLog.objects.create(
            type='WHATSAPP',
            to=phone_number,
            subject=message[:50],
            body=message,
            success=False,
            error_message=str(e)
        )
        return False
