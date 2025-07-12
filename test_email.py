import smtplib

smtp_server = "smtp.gmail.com"
port = 587
sender_email = "samuelolokor228@gmail.com"
password = 'ruuf obmt fqwr xidn'  # Your app password
receiver_email = "samuelolokor228@gmail.com"  # Send to yourself for testing

try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    message = "Subject: Test Email\n\nThis is a test email from Python."
    server.sendmail(sender_email, receiver_email, message)
    print("Email sent successfully!")
except Exception as e:
    print("Error:", e)
finally:
    try:
       server.quit()
    except:
       pass 