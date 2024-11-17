# Custom Email-Sending Application with Dashboard

## Overview
This project is a **custom email-sending application** designed to streamline personalized email campaigns. It incorporates advanced scheduling, real-time tracking, and analytics, while leveraging an AI-based language model for dynamic content generation. The solution is designed to be intuitive, scalable, and reliable, meeting modern email communication needs.

## Features
1. **Data Integration**: Supports reading data from CSV files for email personalization.
2. **Dynamic Content Generation**: Customizes email content using prompts and AI-generated content (LLM integration with Google Gemini API).
3. **Email Account Connectivity**: Easily connect email accounts via SMTP configurations.
4. **Real-Time Analytics**:
   - Monitor sent, pending, scheduled, and failed emails.
   - Track email open rates with embedded tracking pixels.
5. **Email Scheduling**:
   - Send emails immediately, at a specific time, or in batches.
   - Throttling support to adhere to ESP limits.
6. **User-Friendly Dashboard**: Intuitive interface for managing email campaigns and viewing analytics.

---

## Setup and Installation

### Prerequisites
- Python 3.9+
- Git
- Virtual Environment (recommended)
- Access to SMTP credentials for email sending
- Google API key for AI content generation

### Installation
1. Clone the repository:
   ```bash
      git clone https://github.com/ujwala-rapalli/CustomEmail_Sender.git
   cd CustomEmail_Sender

   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the root directory with the following:
     ```
     EMAIL_ADDRESS=your-email@example.com
     EMAIL_PASSWORD=your-password
     SMTP_SERVER=smtp.your-email-provider.com
     SMTP_PORT=587
     GOOGLE_API_KEY=your-google-api-key
     ```

5. Initialize the database:
   ```bash
   python app.py
   ```

---

## Usage Instructions

1. **Run the Application**:
   ```bash
   python app.py
   ```
   Access the dashboard at `http://127.0.0.1:5000`.

2. **Login/Register**:
   - Register as a new user.
   - Log in to access the dashboard.

3. **Upload CSV and Configure Campaign**:
   - Navigate to the dashboard.
   - Upload a CSV file with columns like `Contact_Name`, `Company_Name`, and `Email_Address`.
   - Enter an email prompt to generate personalized content.

4. **Schedule Emails**:
   - Choose a scheduling option:
     - Send Now
     - Specific Time
     - Batch Scheduling
   - Configure throttling limits if required.

5. **Monitor Campaign**:
   - Track email statuses (sent, scheduled, failed, opened) in real-time on the dashboard.
   - View analytics and adjust campaigns as needed.

---

## Code Structure
```
project-root/
│
├── app.py                # Main application file
├── email_utilities.py    # Email sending and tracking functions
├── templates/            # HTML templates for Flask
├── static/               # Static files (CSS, JS)
├── forms.py              # Flask-WTF forms for user input
├── config.py             # Configuration file for app settings
├── uploads/              # Directory for uploaded CSV files
├── venv/                 # Virtual environment
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

---

## Key Technologies
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Bootstrap)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Email Sending**: SMTP Integration
- **AI**: Google Gemini API for email content generation
- **Task Scheduling**: APScheduler
- **Tracking**: Pixel-based email open tracking

---

## Future Enhancements
- Add Google Sheets integration.
- Expand analytics with detailed reporting.
- Implement OAuth for more secure email account connections.
- Introduce multi-language support.

---

## Demo Video
[https://youtu.be/lvNjxjH5XCk]

---


Feel free to reach out for any questions or clarifications regarding the project.
