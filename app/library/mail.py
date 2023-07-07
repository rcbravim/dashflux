import os

from sendgrid import Mail, SendGridAPIClient

api_key = os.getenv('SENDGRID_API_KEY')
default_sender = os.getenv('MAIL_DEFAULT_SENDER')


def send_email(to_emails, subject, html_content, sender=default_sender):
    message = Mail(
        from_email=sender,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return response
    except Exception as e:
        print(e)


if __name__ == "__main__":
    send_email(
        'raphael.bravim@gmail.com',
        'Sending with Twilio SendGrid is Fun',
        '<strong>and easy to do anywhere, even with Python</strong>'
    )
