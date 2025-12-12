import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
import os

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Reads from your .env file
SENDER_EMAIL = os.getenv("MAIL_USERNAME")
SENDER_PASSWORD = os.getenv("MAIL_PASSWORD")

# --- 1. EMAIL FUNCTION ---
def send_email_alert(to_email: str, threat_type: str, location: str, ip: str, is_safe: bool = False):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return

    try:
        # Dynamic Subject & Color
        if is_safe:
            subject = f"✅ New Login: SecureWatch Access Granted"
            color = "#05cd99" # Green
            status_text = "SUCCESS"
            intro = "A new login was detected on your account."
        else:
            subject = f"🚨 Security Alert: {threat_type}"
            color = "#d9534f" # Red
            status_text = "BLOCKED"
            intro = "Suspicious login attempt blocked."

        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <div style="padding: 20px; border: 1px solid #eee; border-radius: 10px;">
              <h2 style="color: {color};">SecureWatch Notification</h2>
              <p>{intro}</p>
              <ul>
                <li><strong>Result:</strong> {threat_type}</li>
                <li><strong>Location:</strong> {location}</li>
                <li><strong>IP:</strong> {ip}</li>
                <li><strong>Status:</strong> <span style="color:{color}; font-weight:bold;">{status_text}</span></li>
              </ul>
            </div>
          </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"❌ Email Failed: {e}")

# --- 2. PDF GENERATOR (Crash-Proof) ---
class ReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'SecureWatch AI - Forensic Incident Report', 0, 1, 'C')
        self.ln(10)

def generate_compliance_report(log_data: dict):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Helper to clean text (Remove Emojis to prevent crash)
    def clean(text):
        if not text: return ""
        # Encode to latin-1 to strip unknown characters, then decode back
        return text.encode('latin-1', 'ignore').decode('latin-1')

    # Content
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Incident ID: {clean(log_data['id'][:8])}", ln=1)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Timestamp: {clean(log_data['time'])}", ln=1)
    pdf.cell(200, 10, txt=f"Location: {clean(log_data['location'])}", ln=1)
    pdf.cell(200, 10, txt=f"IP Address: {clean(log_data['ip'])}", ln=1)
    
    # Verdict Highlight
    pdf.set_text_color(220, 53, 69) # Red color
    pdf.cell(200, 10, txt=f"Status: {clean(log_data['status'])}", ln=1)
    pdf.set_text_color(0, 0, 0) # Reset color
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="AI Analysis Summary:", ln=1)
    pdf.set_font("Arial", '', 11)
    
    # Multi-cell for long text
    summary = clean(log_data.get('ai_summary', 'No summary available.'))
    pdf.multi_cell(0, 8, txt=summary)
    
    filename = f"report_{log_data['id'][:8]}.pdf"
    # For Windows/Linux compatibility
    path = filename 
    pdf.output(path)
    return path