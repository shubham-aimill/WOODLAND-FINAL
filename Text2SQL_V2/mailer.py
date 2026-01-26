import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Initialize settings
load_dotenv()
def setup_logger():
    """
    Sets up a logger with a console handler.
    """
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set minimum log level

    # Prevent adding multiple handlers if setup_logger is called multiple times
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Handler log level

        # Create formatter for log messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger
logger = setup_logger()



# --- CONFIGURATION ---
# 1. You MUST add this new variable to your Render Dashboard/Environment
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# 2. This MUST be your verified email address from SendGrid (shubham.sahu@aimill.in)
FROM_EMAIL = os.getenv("MAIL_USERNAME")

# 3. Recipient list from environment (e.g., "user1@gmail.com, user2@work.com")
ALERT_EMAILS_STR = os.getenv("ALERT_EMAILS", "")
ALERT_EMAILS = [e.strip() for e in ALERT_EMAILS_STR.split(",") if e.strip()]

def send_success_email(subject, body):
    """
    Sends a success email using the SendGrid Web API.
    This bypasses Render's SMTP port blocking.
    """
    if not ALERT_EMAILS:
        logger.warning("⚠️ ALERT_EMAILS not configured. Skipping email.")
        return

    if not SENDGRID_API_KEY:
        logger.error("❌ SENDGRID_API_KEY is missing from environment variables!")
        return

    # Create the Mail object
    # Using html_content because your LLM generates HTML tags like <b> and <h3>
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=ALERT_EMAILS,
        subject=subject,
        html_content=body 
    )

    try:
        # Connect to SendGrid via API Client
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Success check (SendGrid returns 202 Accepted for successful queuing)
        if response.status_code in [200, 201, 202]:
            logger.info(f"✅ Email sent successfully to: {', '.join(ALERT_EMAILS)}")
        else:
            logger.warning(f"⚠️ SendGrid API returned unexpected status: {response.status_code}")

    except Exception as e:
        # Log error with f-string to prevent formatting crashes
        logger.error(f"❌ SendGrid API failed to send: {e}")

if __name__ == "__main__":
    # Local Test: Run this file directly to verify your API key
    print("Testing SendGrid configuration...")
    send_test_body = "<h3>Success</h3><p>Your <b>Text2SQL</b> mailer is working!</p>"
    send_success_email("Local Test: SendGrid API", send_test_body)