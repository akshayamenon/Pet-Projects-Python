from logger import *
import smtplib
from email.message import EmailMessage
def alert_api_down(api_name, response):
    """
    Alert when an API is down.
    """
    info(f"API {api_name} is down. Sending alert.")
    if response is None:    
        subject = f"Alert: {api_name} is down"
        message = f"The API {api_name} is not responding as expected.\nResponse Code: {response.status_code}\nResponse Text: {response.text}"
    
        send_email_alert()
        error(message)

def send_email_alert():
     # Usage
    subject = "Alert: Something happened!"
    body = "This is an alert notification sent from Python."
    to_email = "akshayamenon55555@gmail.com"
    from_email = "akshayamenon55555@gmail.com"
    # from_password = "your_app_password"  # For Gmail, use an App Password if 2FA enabled

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body)

   
    # Connect to Gmail SMTP server (use your SMTP server if different)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email)
        smtp.send_message(msg)


