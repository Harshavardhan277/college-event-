import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Use absolute path to ensure .env is loaded correctly
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)

def test_email():
    username = os.environ.get("MAIL_USERNAME")
    password = os.environ.get("MAIL_PASSWORD")
    # Forcing IPv4 address to bypass local DNS resolution issues
    server = "142.250.150.108" 
    port = 587
    
    print(f"Testing SMTP with:")
    print(f"  Server IP (Gmail): {server}")
    print(f"  Port: {port}")
    print(f"  User: {username}")
    print(f"  Password: {'*' * len(password) if password else 'None'}")
    
    msg = EmailMessage()
    msg.set_content("Test email from CEAM diagnostic script (IPv4 Direct).")
    msg['Subject'] = "CEAM SMTP Test"
    msg['From'] = username
    msg['To'] = username  # Send to self

    try:
        print("\nConnecting to server...")
        # Note: Using localhost name in HELO to be safe
        with smtplib.SMTP(server, port, local_hostname='localhost') as smtp:
            smtp.set_debuglevel(1)
            print("Sending EHLO...")
            smtp.ehlo()
            print("Starting TLS...")
            smtp.starttls()
            print("Logging in...")
            smtp.login(username, password)
            print("Sending message...")
            smtp.send_message(msg)
            print("\nSUCCESS! SMTP is working correctly.")
    except Exception as e:
        print(f"\nFAILURE! SMTP error: {e}")

if __name__ == "__main__":
    test_email()
