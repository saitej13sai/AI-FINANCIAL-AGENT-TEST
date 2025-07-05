import os
import requests

def send_email(to, subject, body, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    email_data = {
        "raw": encode_email(to, subject, body)
    }
    res = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers=headers,
        json=email_data
    )
    return res.status_code == 200

def encode_email(to, subject, body):
    import base64
    from email.mime.text import MIMEText
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw

def create_event(summary, start_time, end_time, attendees, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
        "attendees": [{"email": e} for e in attendees]
    }
    res = requests.post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers=headers,
        json=event
    )
    return res.status_code == 200

def add_note_to_hubspot(contact_id, note, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = "https://api.hubapi.com/crm/v3/objects/notes"
    payload = {
        "properties": {
            "hs_note_body": note
        },
        "associations": [
            {
                "to": {"id": contact_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 280}]
            }
        ]
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code == 201
