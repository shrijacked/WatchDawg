import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, attachment=None):
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_password"

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment:
        with open(attachment, "rb") as f:
            attach = MIMEText(f.read(), "base64")
            attach.add_header('Content-Disposition', 'attachment', filename="video.avi")
            msg.attach(attach)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email("Alert: Person Detected", "A person was detected for prolonged duration.")
