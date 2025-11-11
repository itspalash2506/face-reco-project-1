import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
whatsapp_from = os.getenv('TWILIO_WHATSAPP_NUMBER')

def send_whatsapp_notification(to_number, person_name, email):
    try:
        if not account_sid or not auth_token or not whatsapp_from:
            print("Twilio credentials not configured. Skipping WhatsApp notification.")
            return False

        client = Client(account_sid, auth_token)

        message_body = f"""
Face Recognition Alert!

Person Detected: {person_name}
Email: {email}
Time: Just now

This is an automated notification from your Face Recognition System.
"""

        message = client.messages.create(
            from_=f'whatsapp:{whatsapp_from}',
            body=message_body,
            to=f'whatsapp:{to_number}'
        )

        print(f"WhatsApp notification sent successfully. SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Error sending WhatsApp notification: {str(e)}")
        return False
