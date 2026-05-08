from groq import Groq
from config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)

def generate_research_plan(query: str, sector: str) -> dict:
    prompt = f"""You are a senior financial research analyst.
A user wants: "{query}"
Sector: {sector}

Generate a structured research plan with:
1. Research objectives (3-5 bullet points)
2. Information sources to use (web search, financial data, documents)
3. Key companies/topics to investigate
4. Expected report sections
5. Estimated research steps (5-15)

Format your response as a clear, readable plan that a user can approve."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    plan_text = response.choices[0].message.content
    return {"query": query, "sector": sector, "plan": plan_text}