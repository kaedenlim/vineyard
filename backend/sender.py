import os
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

# Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "email-smtp.ap-southeast-2.amazonaws.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "kaedenlim3@gmail.com")

# FastAPI setup
app = FastAPI()

# Request schema
class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    message: str

# Email sending function
def send_email(to_email: str, subject: str, body: str) -> bool:
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# Route for sending emails
@app.post("/send-email")
def send_email_endpoint(email: EmailRequest):
    success = send_email(email.to, email.subject, email.message)
    if not success:
        raise HTTPException(status_code=500, detail="Email failed to send")
    return {"message": "✅ Email sent successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sender:app", host="0.0.0.0", port=8001, reload=True)
