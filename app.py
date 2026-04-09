from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_123'

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            password TEXT NOT NULL
        )
    ''')
    
    # ... existing tables ...
    
    # Create doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            availability TEXT,
            bio TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            medication_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT,
            duration TEXT,
            instructions TEXT,
            date_prescribed TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            reason TEXT
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            doctor_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Sent',
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ All database tables checked/created successfully!")
# Make sure to call init_db()
init_db()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                     (name, email, phone, password))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('Email already registered!')
        except Exception as e:
            flash(f'Error: {str(e)}')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        print(f"Login attempt - Username: '{username}', Password: '{password}'")

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Try to find user by username OR email
        cur.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?", 
                   (username, username, password))
        user = cur.fetchone()
        conn.close()

        print(f"Database result: {user}")

        if user:
            session['username'] = user[1]  # username is at index 1
            session['user_id'] = user[0]   # id is at index 0
            print("✅ Login successful")
            return redirect(url_for('dashboard'))
        else:
            print("❌ Invalid credentials")
            return render_template('login.html', error="Invalid username/email or password. Please try again.")
    
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        doctor = request.form.get('doctor')
        date = request.form.get('date')
        time = request.form.get('time')
        reason = request.form.get('reason')
        username = session['username']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO appointments (username, doctor, date, time, reason) VALUES (?, ?, ?, ?, ?)",
                    (username, doctor, date, time, reason))
        conn.commit()
        conn.close()

        flash('Appointment booked successfully!')
        return redirect(url_for('view_appointments'))
    
    return render_template('book.html')

@app.route('/prescriptions')
def prescriptions():
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prescriptions WHERE username=?", (username,))
        prescriptions = cursor.fetchall()
        conn.close()
        return render_template('prescriptions.html', prescriptions=prescriptions)
    else:
        return redirect(url_for('login'))

@app.route('/prescriptions')
def view_prescriptions():

    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM prescriptions WHERE username = ? ORDER BY date_prescribed DESC", (username,))
    prescriptions = cur.fetchall()
    conn.close()
    
    return render_template('prescriptions.html', prescriptions=prescriptions)

@app.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = session['username']
        patient_name = request.form['patient_name']
        doctor_name = request.form['doctor_name']
        medication_name = request.form['medication_name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        duration = request.form['duration']
        instructions = request.form['instructions']
        date_prescribed = request.form['date_prescribed']
        
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('''INSERT INTO prescriptions 
                      (username, patient_name, doctor_name, medication_name, dosage, frequency, duration, instructions, date_prescribed) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (username, patient_name, doctor_name, medication_name, dosage, frequency, duration, instructions, date_prescribed))
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_prescriptions'))
    
    return render_template('add_prescription.html')

@app.route('/delete_prescription/<int:prescription_id>')
def delete_prescription(prescription_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_prescriptions'))

@app.route('/appointments')
def view_appointments():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments WHERE username = ? ORDER BY date, time", (username,))
    appointments = cur.fetchall()
    conn.close()
    
    return render_template('appointments.html', appointments=appointments)

@app.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_appointments'))

@app.route('/profile')
def view_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    if request.method == 'POST':
        new_username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        
        try:
            # Update user profile
            cur.execute("UPDATE users SET username = ?, email = ?, phone = ? WHERE username = ?", 
                       (new_username, email, phone, username))
            conn.commit()
            
            # Update session with new username
            session['username'] = new_username
            
            flash('Profile updated successfully!')
            return redirect(url_for('view_profile'))
            
        except sqlite3.IntegrityError:
            flash('Username or email already exists! Please choose different ones.')
        except Exception as e:
            flash(f'Error updating profile: {str(e)}')
    
    # Get current user data for the form
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    
    return render_template('edit_profile.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        
        # Verify current password
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, current_password))
        user = cur.fetchone()
        
        if not user:
            flash('Current password is incorrect!')
        elif new_password != confirm_password:
            flash('New passwords do not match!')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters long!')
        else:
            # Update password
            cur.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            conn.commit()
            flash('Password changed successfully!')
        
        conn.close()
        return redirect(url_for('view_profile'))
    
    return render_template('change_password.html')

def add_sample_doctors():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check if doctors already exist
    c.execute("SELECT COUNT(*) FROM doctors")
    count = c.fetchone()[0]
    
    if count == 0:
        sample_doctors = [
            ('Dr. Sarah Johnson', 'Cardiology', 's.johnson@healthcare.com', '+1-555-0101', 'Mon-Fri: 9AM-5PM', 'Senior Cardiologist with 15 years of experience specializing in heart diseases.'),
            ('Dr. Michael Chen', 'Pediatrics', 'm.chen@healthcare.com', '+1-555-0102', 'Mon-Sat: 8AM-4PM', 'Pediatrician dedicated to children healthcare and wellness.'),
            ('Dr. Emily Davis', 'Dermatology', 'e.davis@healthcare.com', '+1-555-0103', 'Tue-Thu: 10AM-6PM', 'Skin care specialist with expertise in cosmetic and medical dermatology.'),
            ('Dr. Robert Wilson', 'Orthopedics', 'r.wilson@healthcare.com', '+1-555-0104', 'Mon-Wed-Fri: 9AM-5PM', 'Orthopedic surgeon specializing in joint replacement and sports injuries.'),
            ('Dr. Lisa Martinez', 'Psychiatry', 'l.martinez@healthcare.com', '+1-555-0105', 'Mon-Thu: 9AM-4PM', 'Psychiatrist focusing on mental health and wellness therapy.')
        ]
        
        c.executemany('''
            INSERT INTO doctors (name, specialty, email, phone, availability, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_doctors)
        
        conn.commit()
        print("✅ Sample doctors added successfully!")
    
    conn.close()

# Call this after init_db()
init_db()
add_sample_doctors()

@app.route('/contact_doctor')
def contact_doctor():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # Get all doctors
    cur.execute("SELECT * FROM doctors ORDER BY specialty, name")
    doctors = cur.fetchall()
    
    # Get user's recent messages
    cur.execute('''
        SELECT m.*, d.name as doctor_name 
        FROM messages m 
        JOIN doctors d ON m.doctor_id = d.id 
        WHERE m.username = ? 
        ORDER BY m.timestamp DESC 
        LIMIT 5
    ''', (session['username'],))
    recent_messages = cur.fetchall()
    
    conn.close()
    
    return render_template('contact_doctor.html', 
                         doctors=doctors, 
                         recent_messages=recent_messages)

@app.route('/send_message/<int:doctor_id>', methods=['GET', 'POST'])
def send_message(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    # Get doctor details
    cur.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cur.fetchone()
    
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        username = session['username']
        
        # Insert message
        cur.execute('''
            INSERT INTO messages (username, doctor_id, subject, message)
            VALUES (?, ?, ?, ?)
        ''', (username, doctor_id, subject, message))
        
        conn.commit()
        conn.close()
        
        flash('Message sent successfully! The doctor will respond within 24 hours.')
        return redirect(url_for('contact_doctor'))
    
    conn.close()
    return render_template('send_message.html', doctor=doctor)

@app.route('/message_history')
def message_history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    cur.execute('''
        SELECT m.*, d.name as doctor_name, d.specialty
        FROM messages m 
        JOIN doctors d ON m.doctor_id = d.id 
        WHERE m.username = ? 
        ORDER BY m.timestamp DESC
    ''', (username,))
    messages = cur.fetchall()
    
    conn.close()
    
    return render_template('message_history.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)

