from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=True):
    # print(f'mail.MAIL_SERVER: {mail.app.config["MAIL_SERVER"]}')
    # print(f'mail.MAIL_PORT: {mail.app.config["MAIL_PORT"]}')
    # print(f'mail.MAIL_USE_TLS: {mail.app.config["MAIL_USE_TLS"]}')
    # print(f'mail.MAIL_USERNAME: {mail.app.config["MAIL_USERNAME"]}')
    # print(f'mail.MAIL_PASSWORD: {mail.app.config["MAIL_PASSWORD"]}')

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()
