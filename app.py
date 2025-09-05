# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
import os
print("DEBUG: MAIL_PASSWORD =", os.environ.get("MAIL_PASSWORD"))
print("DEBUG: FROM_EMAIL =", os.environ.get("SENDGRID_FROM_EMAIL"))
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_mail import Mail, Message

import sqlite3
from werkzeug.utils import secure_filename
from config import Config
import csv
from flask import Response
import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from collections import Counter
import datetime
import hashlib
import re
from datetime import datetime
import requests

app = Flask(__name__)
app.config.from_object(Config)

# ✅ Gmail SMTP configuration
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True") == "True",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME"))
)

mail = Mail(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# DB Setup
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Complaints table
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT,
        matric TEXT,
        phone TEXT,
        email TEXT,
        location TEXT,
        description TEXT,
        incident_date TEXT,
        photo_filename TEXT,
        resolved INTEGER DEFAULT 0
    )''')
    # Try to add resolved column if it doesn't exist (for existing DBs)
    try:
        c.execute('ALTER TABLE complaints ADD COLUMN resolved INTEGER DEFAULT 0')
    except Exception:
        pass
    # Admins table
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )''')
    # Add a default full admin if none exists
    c.execute('SELECT COUNT(*) FROM admins')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)',
                  ('admin', hash_password('RUNSA2025'), 'full'))
    # Attachments table
    c.execute('''CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER,
        filename TEXT,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id)
    )''')
    conn.commit()
    conn.close()

init_db()

# Removed the hard-coded secret key - now using from config
# ADMIN_USERNAME and ADMIN_PASSWORD variables removed as they're unused

import requests

def send_email(to_email, subject, content):
    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = content
        mail.send(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print("❌ Email failed:", e)
        raise

    response = requests.post(url_for, headers=headers, json=data)

    # Debugging / feedback
    if response.status_code == 202:
        print(f"✅ Email sent successfully to {to_email}")
    else:
        print(f"❌ SendGrid API error {response.status_code}: {response.text}")

    return response.status_code


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT password_hash, role FROM admins WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        if row and hash_password(password) == row[0]:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_role'] = row[1]
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM complaints ORDER BY id DESC')
    complaints = c.fetchall()
    # Dashboard stats
    total = len(complaints)
    resolved = sum(1 for c in complaints if c[9] == 1)
    pending = total - resolved
    # Complaints per month (YYYY-MM)
    months = [c[7][:7] for c in complaints if c[7]]
    month_counts = Counter(months)
    month_labels = sorted(month_counts.keys())
    month_data = [month_counts[m] for m in month_labels]
    conn.close()
    return render_template('admin_panel.html', complaints=complaints, total=total, resolved=resolved, pending=pending, month_labels=month_labels, month_data=month_data)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Restrict actions based on role
@app.route('/admin/resolve/<int:complaint_id>', methods=['POST'])
def mark_resolved(complaint_id):
    if not session.get('admin_logged_in') or session.get('admin_role') != 'full':
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin_panel'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE complaints SET resolved = 1 WHERE id = ?', (complaint_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:complaint_id>', methods=['POST'])
def delete_complaint(complaint_id):
    if not session.get('admin_logged_in') or session.get('admin_role') != 'full':
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin_panel'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM complaints WHERE id = ?', (complaint_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/bulk_action', methods=['POST'])
def bulk_action():
    if not session.get('admin_logged_in') or session.get('admin_role') != 'full':
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin_panel'))
    ids = request.form.getlist('selected')
    action = request.form.get('action')
    if not ids:
        flash('No complaints selected.', 'warning')
        return redirect(url_for('admin_panel'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if action == 'resolve':
        c.executemany('UPDATE complaints SET resolved = 1 WHERE id = ?', [(i,) for i in ids])
        flash(f'{len(ids)} complaint(s) marked as resolved.', 'success')
    elif action == 'delete':
        c.executemany('DELETE FROM complaints WHERE id = ?', [(i,) for i in ids])
        flash(f'{len(ids)} complaint(s) deleted.', 'success')
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/download_csv')
def download_csv():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM complaints ORDER BY id DESC')
    complaints = c.fetchall()
    conn.close()
    def generate():
        header = ['ID', 'Full Name', 'Matric', 'Phone', 'Email', 'Location', 'Description', 'Date', 'Photo', 'Resolved']
        yield ','.join(header) + '\n'
        for c in complaints:
            row = [str(x) for x in c]
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=complaints.csv"})

@app.route('/admin/download_pdf')
def download_pdf():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM complaints ORDER BY id DESC')
    complaints = c.fetchall()
    conn.close()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    y = height - 40
    x_list = [40, 90, 180, 270, 360, 450, 540, 630, 720, 810, 900]
    headers = ['ID', 'Full Name', 'Matric', 'Phone', 'Email', 'Location', 'Description', 'Date', 'Photo', 'Resolved']
    for i, header in enumerate(headers):
        p.drawString(x_list[i], y, header)
    y -= 20
    for row in complaints:
        for i, item in enumerate(row):
            p.drawString(x_list[i], y, str(item))
        y -= 20
        if y < 40:
            p.showPage()
            y = height - 40
            for i, header in enumerate(headers):
                p.drawString(x_list[i], y, header)
            y -= 20
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='complaints.pdf', mimetype='application/pdf')

@app.route('/admin/complaint/<int:complaint_id>')
def admin_complaint_detail(complaint_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,))
    complaint = c.fetchone()
    conn.close()
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin_panel'))
    return render_template('admin_complaint_detail.html', complaint=complaint)

def get_attachments(complaint_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT filename FROM attachments WHERE complaint_id = ?', (complaint_id,))
    files = [row[0] for row in c.fetchall()]
    conn.close()
    return files

app.jinja_env.globals.update(get_attachments=get_attachments)

@app.route('/', methods=['GET', 'POST'])
def complaint_form():
    max_date = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        data = {
            'fullname': request.form['fullname'],
            'matric': request.form['matric'],
            'phone': request.form['phone'],
            'email': request.form['email'],
            'location': request.form['location'],
            'description': request.form['description'],
            'incident_date': request.form['incident_date'],
            'photo_filenames': []
        }

        # Handle multiple file uploads
        images = request.files.getlist('images[]')
        for image in images:
            if image and image.filename:
                if Config.allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    data['photo_filenames'].append(filename)
                else:
                    flash(f'File type not allowed: {image.filename}', 'warning')

        # Validation
        errors = []
        import re, sqlite3
        if not re.fullmatch(r'[A-Za-z ]{3,50}', data['fullname']):
            errors.append('Full name must be 3-50 letters and spaces only.')
        if not re.fullmatch(r'RUN/[A-Za-z]{3}/\d{2}/\d{4,6}', data['matric']):
            errors.append('Matric number must be in the format RUN/XXX/YY/12345.')
        if not re.fullmatch(r'\d{11}', data['phone']):
            errors.append('Phone number must be exactly 11 digits.')
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', data['email']):
            errors.append('Enter a valid email address.')
        if not (3 <= len(data['location']) <= 100):
            errors.append('Location must be 3-100 characters.')
        if not (5 <= len(data['description']) <= 500):
            errors.append('Description must be 5-500 characters.')
        try:
            incident_date = datetime.strptime(data['incident_date'], '%Y-%m-%d')
            if incident_date > datetime.now():
                errors.append('Date of incident cannot be in the future.')
        except Exception:
            errors.append('Invalid date format.')
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('complaint_form.html', max_date=max_date, **data)

        # Save to database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO complaints 
            (fullname, matric, phone, email, location, description, incident_date, photo_filename) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
                data['fullname'],
                data['matric'],
                data['phone'],
                data['email'],
                data['location'],
                data['description'],
                data['incident_date'],
                ','.join(data['photo_filenames'])  # Save filenames as comma-separated
            ))
        complaint_id = c.lastrowid
        conn.commit()

        # Save attachments records
        for filename in data['photo_filenames']:
            c.execute('INSERT INTO attachments (complaint_id, filename) VALUES (?, ?)', (complaint_id, filename))
        conn.commit()
        conn.close()

        # Send confirmation email to user
        try:
            user_body = f"""Dear {data['fullname']},

Your complaint has been received successfully. Here are the details:

Matric Number: {data['matric']}
Phone: {data['phone']}
Location: {data['location']}
Issue: {data['description']}
Date of Incident: {data['incident_date']}

We will address this issue as soon as possible.

Regards,
RUNSA Welfare 2025/2026
Redeemer's University
"""
            send_email(
                to_email=data['email'],
                subject="Complaint Received - Redeemer's University",
                content=user_body
            )
        except Exception as e:
            print("Email failed:", e)
            flash('Complaint submitted but email confirmation failed.', 'warning')

        # Notify all admins
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('SELECT username FROM admins')
            admin_emails = [row[0] for row in c.fetchall() if '@' in row[0]]
            conn.close()

            if admin_emails:
                admin_body = f"""A new complaint has been submitted.

Student: {data['fullname']}  
Matric: {data['matric']}  

Login to the admin panel to view details.
"""
                for admin_email in admin_emails:
                    send_email(
                        to_email=admin_email,
                        subject="New Complaint Submitted - RU Complaint System",
                        content=admin_body
                    )
        except Exception as e:
            print("Admin notification failed:", e)

        return redirect(url_for('success'))

    return render_template('complaint_form.html', max_date=max_date)

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)