import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

def send_email(to_email, subject, body):
    try:
        # Set up the email
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach the email body
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SMTP server and send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)

        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# For testing purposes
if __name__ == "__main__":
    print(send_email("recipient-email@gmail.com", "Test Subject", "This is a test email body."))

