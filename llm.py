import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()  # reads your .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing. Copy .env.example to .env and add your key.")

model = init_chat_model(
    "groq:openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
)
