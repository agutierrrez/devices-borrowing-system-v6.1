import os
import smtplib
from email.message import EmailMessage


def send_email(to_address, subject, body):
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    from_addr = os.environ.get('SMTP_FROM', smtp_user)

    if not smtp_host or not smtp_user or not smtp_pass:
        # SMTP not configured; mock by printing and returning False
        print('SMTP not configured. Mock send to:', to_address)
        print('Subject:', subject)
        print(body)
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_address
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)
    return True
