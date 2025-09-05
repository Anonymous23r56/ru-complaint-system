import smtplib
import os

smtp_server = "smtp.gmail.com"
port = 587  # TLS port
sender_email = "samuelolokor228@gmail.com"
password = "wxdh wydd gdjs rzrz"  # Your Gmail App Password
receiver_email = "samuelolokor228@gmail.com"

try:
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_email, password)
    message = """Subject: Test Email via Gmail SMTP

This is a test email from Python using Gmail SMTP."""
    server.sendmail(sender_email, receiver_email, message)
    print("✅ Email sent successfully via Gmail!")
except Exception as e:
    print("❌ Error:", e)
finally:
    try:
        server.quit()
    except:
        pass
