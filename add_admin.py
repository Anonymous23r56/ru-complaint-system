import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- EDIT THESE VALUES ---
username = "Samuel"         # Change to the desired username
password = "roloke213#"     # Change to the desired password
role = "full"               # Use "full" for full admin, "viewer" for view-only

# --- DO NOT EDIT BELOW ---
conn = sqlite3.connect('database.db')
c = conn.cursor()
try:
    c.execute(
        "INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role)
    )
    conn.commit()
    print(f"Admin '{username}' added successfully with role '{role}'.")
except sqlite3.IntegrityError:
    print(f"Username '{username}' already exists.")
finally:
    conn.close()