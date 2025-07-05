import os
import sys
import time
import psycopg2

# ✅ Add current directory to sys.path so utils/ can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.rag import fetch_gmail_threads  # Poll Gmail inbox
from utils.tools import send_email, add_note_to_hubspot  # Tool functions

DB_URL = os.getenv("DB_URL")


def poll_for_triggers():
    print("\U0001F501 Starting polling agent...")

    while True:
        try:
            print("\U0001F575️ Checking for new instructions...")

            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("SELECT user_email, instruction FROM instructions")
            instructions = cur.fetchall()

            for user_email, instruction in instructions:
                print(f"⚡ Handling instruction for {user_email}: {instruction}")

                # ✅ Get Gmail token from user_tokens table
                cur.execute("SELECT google_access_token FROM user_tokens WHERE user_email = %s", (user_email,))
                row = cur.fetchone()
                if not row:
                    print(f"❌ No Gmail token found for {user_email}")
                    continue

                gmail_token = row[0]

                if "summarize recent gmail" in instruction.lower():
                    print(f"✉️ Summarizing recent Gmail emails for {user_email}...")
                    emails = fetch_gmail_threads(gmail_token)

                    # Basic summary: just join top 3 emails (customize with LLM later)
                    summary = "\n".join(emails[:3]) if emails else "No recent emails found."
                    print(f"📬 Summary:\n{summary}")

                    # Optionally send to HubSpot or email back
                    # send_email(user_email, "Your Gmail Summary", summary)
                    # add_note_to_hubspot(user_email, summary)

            cur.close()
            conn.close()

        except Exception as e:
            print(f"❌ Error in polling: {str(e)}")

        time.sleep(60)  # ⏱️ Poll every 60 seconds


if __name__ == "__main__":
    poll_for_triggers()
