# RU Complaint System

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A robust, modern, and user-centric complaint management platform built for Redeemer’s University.  
Empowering students to be heard, and admins to respond efficiently.

---

## ✨ Features

- **Seamless Student Experience:**  
  Intuitive, mobile-friendly complaint form with real-time validation and support for multiple file attachments.

- **Powerful Admin Dashboard:**  
  Secure login, role-based access (full admin/viewer), analytics dashboard, and bulk actions for efficient complaint management.

- **Smart Notifications:**  
  Instant email alerts to all admins when a new complaint is submitted.

- **Advanced Export:**  
  Export filtered complaints as CSV or PDF—perfect for reporting and record-keeping.

- **Dark Mode:**  
  Accessible, eye-friendly interface with a single click.

- **Data Integrity:**  
  Double-layered input validation (frontend & backend) ensures only quality data is stored.

- **Modern Tech Stack:**  
  Built with Flask, Bootstrap 5, Chart.js, and more.

---

## 🚦 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```sh
git clone https://github.com/YourUsername/ru-complaint-system.git
cd ru-complaint-system
pip install -r requirements.txt
```

### Configuration

- Edit `config.py` with your email credentials (Gmail + app password recommended).

### Run the App

```sh
python app.py
```
Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

---

## 🔐 Admin Access

- **Default Admin Username:** `admin`
- **Default Password:** `RUNSA2025`
- Add more admins with different roles using the provided script.

---

## 🛠️ Tech Stack

- **Backend:** Flask, Flask-Mail, SQLite, ReportLab
- **Frontend:** Bootstrap 5, Chart.js, HTML5, CSS3, JavaScript
- **Other:** Responsive design, dark mode, secure file uploads

---

## 📈 Why This Project?

- **For Students:**  
  A simple, transparent way to report issues and track complaint status.

- **For Admins:**  
  A powerful, data-driven tool to manage, resolve, and analyze complaints—improving campus life.

---

## 🤝 Contributing

We welcome contributions!  
Open an issue or submit a pull request to help make this system even better.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> Built with ❤️ and Python by Samuel Olokor & contributors. 