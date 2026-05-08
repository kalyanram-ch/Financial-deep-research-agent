from groq import Groq
from config import GROQ_API_KEY, FAST_MODEL

client = Groq(api_key=GROQ_API_KEY)

SECTORS = {
    "IT": ["software", "infosys", "tcs", "wipro", "tech mahindra", "hcl", 
           "IT services", "saas", "cloud", "semiconductor"],
    "PHARMA": ["pharma", "drug", "vaccine", "biotech", "cipla", "sun pharma",
               "biosimilar", "clinical trial", "fda", "dcgi"],
    "UNKNOWN": []
}

def classify_sector(query: str) -> str:
    prompt = f"""You are a financial query classifier. 
Classify this query into exactly one sector: IT, PHARMA, or UNKNOWN.
Only reply with the sector name, nothing else.

Query: {query}"""
    
    response = client.chat.completions.create(
        model=FAST_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )
    sector = response.choices[0].message.content.strip().upper()
    return sector if sector in SECTORS else "UNKNOWN"