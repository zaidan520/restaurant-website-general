import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import logging

def send_confirmation_email(data: dict, code: str, pdf_bytes: bytes):
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    sender_email = os.getenv("SENDER_EMAIL", "noreply@restaurantplatform.com")
    
    recipient = data["email"]
    subject = f"Your Table Reservation Confirmation - {code}"
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    
    body = f"""Hi {data['name']},

Thank you for your reservation.

Here are your booking details:
Reservation Code: {code}
Date: {data['date']}
Time: {data['time']}
Party Size: {data['party_size']}

We look forward to serving you!
"""
    msg.attach(MIMEText(body, "plain"))
    
    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=f"reservation_{code}.pdf")
    msg.attach(attachment)
    
    try:
        if not smtp_username and smtp_server == "localhost":
            logging.info(f"[EMAIL SIMULATOR] Sending email to {recipient}")
            print(f"\n--- EMAIL SIMULATOR ---\nSent to: {recipient}\nSubject: {subject}\nBody:\n{body}\n-----------------------\n")
            return
            
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_username and smtp_password:
                server.starttls()
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
            logging.info(f"Email sent successfully to {recipient}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        print(f"\n--- EMAIL SIMULATOR (FALLBACK) ---\nSent to: {recipient}\nSubject: {subject}\nBody:\n{body}\n-----------------------\n")
