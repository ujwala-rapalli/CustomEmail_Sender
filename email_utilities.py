# import smtplib
# from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

# def send_email(contact_name, email_address, email_subject, email_body):
#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#             message = f"Subject: {email_subject}\n\n{email_body}"
#             server.sendmail(EMAIL_ADDRESS, email_address, message)
#         print(f"Email sent to {email_address}")
#     except Exception as e:
#         print(f"Failed to send email to {email_address}: {e}")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(contact_name, email_address, email_subject, email_body, email_id):
    try:
        # Tracking pixel URL
        tracking_url = f"http://127.0.0.1:5000/track/{email_id}.png"  # Replace with your domain in production
        content_with_tracking = f"{email_body}<br><img src='{tracking_url}' alt='' style='display:none;'>"

        # Set up the MIME message
        message = MIMEMultipart()
        message['From'] = EMAIL_ADDRESS
        message['To'] = email_address
        message['Subject'] = email_subject

        # Attach the HTML body
        body = MIMEText(content_with_tracking, 'html', 'utf-8')  # Use 'html' for HTML content
        message.attach(body)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email_address, message.as_string())

        print(f"Email sent to {email_address}")
        return "Delivered"

    except Exception as e:
        print(f"Failed to send email to {email_address}: {e}")
        return "Failed"
 
