from flask_mail import Mail, Message

mail = Mail()


def send_email(to_emails, subject, html_content, sender=None):
    msg = Message(
        subject=subject,
        recipients=to_emails if isinstance(to_emails, list) else [to_emails],
        body=html_content
        )
    if sender:
        msg.sender = sender

    mail.send(msg)
