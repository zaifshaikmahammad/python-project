import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(recipient, otp):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("MAIL_FROM")
    sender_name = os.getenv("MAIL_FROM_NAME", "Personal Expense Tracker")

    if not api_key or not sender_email:
        raise RuntimeError("Brevo email configuration is missing.")

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    data = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": recipient
            }
        ],
        "subject": "Personal Expense Tracker - Email Verification",
        "htmlContent": f"""
        <html>
        <body>
            <h2>Welcome to Personal Expense Tracker!</h2>
            <p>Your email verification OTP is:</p>
            <h1>{otp}</h1>
            <p>This OTP expires in 10 minutes.</p>
            <p>Please do not share this code with anyone.</p>
        </body>
        </html>
        """
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=20
    )

    if response.status_code not in (200, 201, 202):
        raise RuntimeError(
            f"Brevo email sending failed: {response.text}"
        )

    return response.json()