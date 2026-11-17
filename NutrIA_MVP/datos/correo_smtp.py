"""Envío SMTP de Gmail compartido por recuperación y scripts de prueba."""

from email.message import EmailMessage
import os
from pathlib import Path
import smtplib
import ssl

from dotenv import load_dotenv


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ_PROYECTO / ".env")


def enviar_correo(destinatario, asunto, mensaje):
    remitente = os.getenv("NUTRIA_SMTP_EMAIL", "").strip()
    password_app = os.getenv("NUTRIA_SMTP_APP_PASSWORD", "").replace(" ", "").strip()
    if not remitente or not password_app:
        raise RuntimeError(
            f"Configura NUTRIA_SMTP_EMAIL y NUTRIA_SMTP_APP_PASSWORD en {RAIZ_PROYECTO / '.env'}."
        )
    if not destinatario or "@" not in destinatario:
        raise ValueError("El destinatario del correo no es válido.")

    correo = EmailMessage()
    correo["Subject"] = asunto
    correo["From"] = remitente
    correo["To"] = destinatario
    correo.set_content(mensaje)

    contexto = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as servidor:
        servidor.ehlo()
        servidor.starttls(context=contexto)
        servidor.ehlo()
        servidor.login(remitente, password_app)
        rechazados = servidor.send_message(correo)
        if rechazados:
            raise smtplib.SMTPRecipientsRefused(rechazados)
    return True
