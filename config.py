import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")    # Free tier available
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")  # Free tier available

MODEL = "llama-3.1-8b-instant"        # use for all research steps
FAST_MODEL = "llama-3.1-8b-instant"   # classification
REPORT_MODEL = "llama-3.3-70b-versatile"  # only for final report # For quick classification tasks

MAX_RESEARCH_ITERATIONS = 15
MIN_RESEARCH_ITERATIONS = 5