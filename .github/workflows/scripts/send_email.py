import os
import sys
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def main():
    template_path = sys.argv[1] if len(sys.argv) > 1 else 'templates/tenant_email.html'
    
    # 1. Fetch SMTP Credentials & Config from Environment Variables
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    sender_email = os.environ.get("SENDER_EMAIL", smtp_user)
    recipient_email = os.environ.get("RECIPIENT_EMAIL")

    if not all([smtp_server, smtp_user, smtp_pass, recipient_email]):
        print("Error: Missing required SMTP environment variables.")
        sys.exit(1)

    # 2. Read the HTML template
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)

    # 3. Substitute variables dynamically
    template = Template(template_content)
    try:
        html_body = template.substitute(os.environ)
    except KeyError as e:
        print(f"Error: Missing required environment variable for template: {e}")
        sys.exit(1)

    # 4. Construct the Email Message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Deployment Update: {os.environ.get('ENVIRONMENT', 'Production')}"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Attach HTML content
    msg.attach(MIMEText(html_body, 'html'))

    # 5. Connect to SMTP Server and Send
    try:
        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls() # Secure the connection
        server.ehlo()
        
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        print(f"Email successfully sent to {recipient_email}")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Error: Authentication failed. Check your username and password.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to send email: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()