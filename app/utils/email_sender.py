import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_with_attachment(recipient_email, subject, body, attachment_path):
    """
    Envía un correo electrónico con un archivo adjunto.
    """
    # Credenciales de correo
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "joriolgo@gmail.com"
    sender_password = "uaty uegu jndh fjjj"

    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntar archivo
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(attachment_path)}",
    )
    msg.attach(part)

    # Enviar correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Correo enviado exitosamente a {recipient_email}")
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False