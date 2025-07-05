import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("DB_URL")


def connect_db():
    return psycopg2.connect(DB_URL)


def fetch_gmail_threads(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=label:INBOX"
    res = requests.get(url, headers=headers).json()
    emails = []

    for msg in res.get("messages", [])[:10]:  # Fetch only latest 10 emails
        msg_data = requests.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
            headers=headers
        ).json()
        snippet = msg_data.get("snippet", "")
        emails.append(snippet)

    return emails


def search_similar_documents(query, user_email, top_k=5):
    # Embed the query using Gemini API
    url = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": query}]}
    }

    res = requests.post(url, headers=headers, json=data)
    res_json = res.json()
    query_embedding = res_json['embedding']['values']

    # Query PostgreSQL using pgvector for similarity search
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT content, metadata
        FROM documents
        WHERE user_email = %s
        ORDER BY embedding <#> %s
        LIMIT %s
    """, (user_email, query_embedding, top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [row[0] for row in rows]

