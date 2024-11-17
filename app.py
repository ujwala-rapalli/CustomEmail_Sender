
import os
import csv
from time import sleep
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from email_utilities import send_email  # Ensure email_utilities.py has the send_email function
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
import google.generativeai as genai 
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import pytz
import io
from concurrent.futures import ThreadPoolExecutor
 # Import Google Generative AI
ist_timezone = pytz.timezone('Asia/Kolkata')
scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
scheduler.start()

executor = ThreadPoolExecutor(max_workers=10)

# Initialize the Generative AI configuration
genai.configure(api_key="AIzaSyB3AnRnLyUHXvRUC3DQXPu5wP18vyedgwI")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to generate email text
# Function to generate email text with an explicit instruction
def generate_email(prompt):
    # Add instruction to avoid introducing additional placeholders
    instruction = (
        "Note: Please only use the placeholders provided in the prompt and do not introduce any additional placeholders,and need to generate dynamic email content that avoids showing placeholders (e.g., Contact_Name: John) and instead directly substitutes the values"
    )
    full_prompt = f"{prompt}\n\n{instruction}"

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(full_prompt)
    return response.text



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# EmailStatus model
class EmailStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(150), nullable=False)
    email_address = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    delivery_status = db.Column(db.String(50), default="N/A")
    opened = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# User loader
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    email_statuses = EmailStatus.query.order_by(EmailStatus.timestamp.desc()).all()

    ist_timezone = pytz.timezone('Asia/Kolkata')

    # Convert timestamps to IST and format them
    for email in email_statuses:
        if email.timestamp:
            # Convert UTC to IST
            email.local_timestamp = email.timestamp.astimezone(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
        else:
            email.local_timestamp = "N/A"

    return render_template('dashboard.html', email_statuses=email_statuses)



@app.route('/track/<int:email_id>.png')
def track_email(email_id):
    email_entry = EmailStatus.query.get(email_id)
    if email_entry and not email_entry.opened:
        email_entry.opened = True
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error updating opened status: {e}")
    return app.response_class(
        response=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B',
        status=200,
        mimetype='image/gif'
    )

@app.route('/email-status', methods=['GET'])
@login_required
def email_status():
    email_statuses = EmailStatus.query.all()
    data = [
        {
            "company_name": email.company_name,
            "email_address": email.email_address,
            "status": email.status,
            "delivery_status": email.delivery_status,
            "opened": "Yes" if email.opened else "No",
        }
        for email in email_statuses
    ]
    return jsonify(data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/send-emails', methods=['POST'])
@login_required
def send_emails():
    csv_file = request.files.get('csvFile')
    general_prompt = request.form.get('emailBody')
    schedule_option = request.form.get('scheduleOption')
    specific_time = request.form.get('specificTime')
    batch_interval = int(request.form.get('batchInterval', 60))
    emails_per_minute = int(request.form.get('emailsPerMinute', 10))

    if not csv_file or not general_prompt:
        flash("CSV file or email prompt is missing.")
        return redirect(url_for('index'))

    # Read the CSV file
    csv_file.stream.seek(0)
    reader = csv.DictReader(io.StringIO(csv_file.stream.read().decode("utf-8")))
    placeholders = reader.fieldnames
    delay_per_email = 60 / emails_per_minute  # Calculate delay based on throttling limit

    for i, row in enumerate(reader):
        # Extract information from CSV row
        company_name = row.get('Company_Name', 'Unknown Company')
        contact_name = row.get('Contact_Name', 'Valued Customer')
        email_address = row.get('Email_Address')

        if not email_address:
            print(f"Skipping row {i + 1}: Missing email address.")
            continue

        # Generate dynamic email content and subject
        dynamic_prompt = general_prompt + "\n\nInclude the following information:\n"
        dynamic_prompt += "\n".join(f"- {placeholder}: {row.get(placeholder, 'Not provided')}" for placeholder in placeholders)
        email_subject = generate_email(f"Create an email subject for: {dynamic_prompt}").strip()
        email_content = generate_email(dynamic_prompt).strip()

        # Append tracking pixel
        email_entry = EmailStatus(
            company_name=company_name,
            contact_name=contact_name,
            email_address=email_address,
            subject=email_subject,
            content=email_content,
            status="Pending",
            delivery_status="N/A",
            opened=False,
            timestamp=datetime.now(ist_timezone)
        )
        db.session.add(email_entry)
        db.session.commit()

        tracking_url = f"http://127.0.0.1:5000/track/{email_entry.id}.png"
        email_content += f'<img src="{tracking_url}" alt="Tracker" width="1" height="1">'
      
        if schedule_option == 'now':
            try:
                delivery_status = send_email(contact_name, email_address, email_subject, email_content, email_entry.id)
                email_entry.status = "Sent"
                email_entry.delivery_status = delivery_status
            except Exception as e:
                print(f"Error sending email to {email_address}: {e}")
                email_entry.status = "Failed"
            db.session.commit()
        elif schedule_option == 'specific_time' and specific_time:
            try:
                scheduled_time = datetime.strptime(specific_time, '%Y-%m-%d %H:%M:%S').astimezone(ist_timezone)
                scheduler.add_job(
                    send_email,
                    trigger=DateTrigger(run_date=scheduled_time),
                    args=[contact_name, email_address, email_subject, email_content,email_entry.id,]
                )
                email_entry.status = "Scheduled"
            except Exception as e:
                print(f"Error scheduling email for {email_address}: {e}")
            db.session.commit()
        elif schedule_option == 'batch':
            scheduled_time = datetime.now(ist_timezone) + timedelta(minutes=i * batch_interval)
            scheduler.add_job(
                send_email,
                trigger=DateTrigger(run_date=scheduled_time),
                args=[contact_name, email_address, email_subject, email_content,email_entry.id],
                misfire_grace_time=600 
            )
            email_entry.status = "Scheduled"
            db.session.commit()
# Throttling logic
        if i > 0 and i % emails_per_minute == 0:
            sleep(60)  # Wait a minute if the batch limit is reached
        else:
            sleep(delay_per_email)

    flash("Emails processed successfully with throttling!")
    return redirect(url_for('dashboard'))
def initialize_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    initialize_db()
    print("Database initialized!")
    app.run(debug=True)
