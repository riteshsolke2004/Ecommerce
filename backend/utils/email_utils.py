from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
        return email
    except Exception:
        return None

def send_reset_email(to_email, token):
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"
    msg = Message(
        subject="Reset Your Password",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[to_email],
        html=f"""
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_url}">{reset_url}</a>
            <p>This link expires in 1 hour.</p>
        """
    )
    mail.send(msg)
