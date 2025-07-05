# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chat  # ✅ make sure both exist

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register API routes
app.include_router(auth.router, prefix="/api/auth")
app.include_router(chat.router, prefix="/api/chat")

# ✅ Health check route
@app.get("/")
def root():
    return {"message": "Backend is working"}
