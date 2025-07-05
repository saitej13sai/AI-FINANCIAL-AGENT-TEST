from fastapi import APIRouter, Request
import os
import requests
from utils.rag import search_similar_documents
from utils.tools import send_email, create_event, add_note_to_hubspot

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@router.post("")
async def chat(req: Request):
    body = await req.json()
    prompt = body.get("message", "")
    user_email = body.get("email", "demo@agent.com")
    access_token = body.get("access_token", "")  # OAuth token needed for tools

    # Step 1: RAG context
    context_docs = search_similar_documents(prompt, user_email)
    context_text = "\n\n".join(context_docs)

    # Step 2: Create prompt
    tool_instruction = f"""
You are an AI assistant for financial advisors. Based on the user’s question, determine if you should:
1. Send an email (tool: send_email(to, subject, body))
2. Create a meeting (tool: create_event(summary, start_time, end_time, attendees))
3. Add a note to HubSpot (tool: add_note_to_hubspot(contact_id, note))

If not sure, just answer the question normally.
Context:
{context_text}

User’s question: {prompt}
Respond with only what you want to say to the user. If a tool needs to be called, include a line like:
TOOL: send_email("abc@example.com", "Subject", "Message body")
"""

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY,
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": tool_instruction}
                ]
            }
        ]
    }

    try:
        res = requests.post(GEMINI_URL, headers=headers, json=data)
        res_json = res.json()
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        print("AI raw output:", text)

        # TOOL CALL PARSING
        if "TOOL:" in text:
            lines = text.split("TOOL:")
            ai_message = lines[0].strip()
            tool_command = lines[1].strip()

            try:
                if "send_email" in tool_command:
                    eval("send_email" + tool_command.split("send_email")[1].strip())
                    ai_message += "\n✅ Email sent successfully."
                elif "create_event" in tool_command:
                    eval("create_event" + tool_command.split("create_event")[1].strip())
                    ai_message += "\n✅ Meeting scheduled successfully."
                elif "add_note_to_hubspot" in tool_command:
                    eval("add_note_to_hubspot" + tool_command.split("add_note_to_hubspot")[1].strip())
                    ai_message += "\n✅ Note added to HubSpot."
                else:
                    ai_message += "\n⚠️ Unknown tool command."
            except Exception as tool_err:
                ai_message += f"\n❌ Tool execution failed: {tool_err}"

            return {"response": ai_message}

        return {"response": text}

    except Exception as e:
        return {"response": f"❌ Error: {str(e)}"}
@router.post("/instructions")
async def store_instruction(req: Request):
    import psycopg2
    body = await req.json()
    user_email = body["email"]
    instruction = body["instruction"]

    conn = psycopg2.connect(os.getenv("DB_URL"))
    cur = conn.cursor()
    cur.execute("INSERT INTO instructions (user_email, instruction) VALUES (%s, %s)", (user_email, instruction))
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Instruction saved"}
