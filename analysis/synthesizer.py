from groq import Groq
from config import GROQ_API_KEY, MODEL, REPORT_MODEL
from analysis.calculator import compute_financial_summary
import datetime

client = Groq(api_key=GROQ_API_KEY)

def generate_report(query: str, sector: str, raw_findings: str) -> str:
    prompt = f"""You are a senior financial analyst. 
Based on the research findings below, write a comprehensive professional report.

Original query: {query}
Sector: {sector}
Research date: {datetime.date.today()}

RAW RESEARCH FINDINGS:
{raw_findings[:8000]}

Write a structured report with these sections:
1. Executive Summary (3-4 key insights)
2. Market Overview
3. Key Players & Performance
4. Trend Analysis
5. Financial Metrics (use the exact numbers from findings — do not invent data)
6. Regulatory & Risk Factors
7. Investment Outlook
8. Conclusion

Rules:
- Only use facts from the research findings
- Flag any data uncertainty explicitly
- Keep financial figures exact — no rounding unless specified
- Use markdown formatting"""

    response = client.chat.completions.create(
        model=REPORT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.2   # Low temp for factual accuracy
    )
    return response.choices[0].message.content

def save_report(report: str, query: str) -> str:
    """Save report as markdown file."""
    import re, os
    safe_name = re.sub(r'[^a-z0-9]+', '_', query.lower())[:50]
    filename = f"outputs/{safe_name}_{datetime.date.today()}.md"
    os.makedirs("outputs", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Report\n**Query:** {query}\n\n{report}")
    return filename