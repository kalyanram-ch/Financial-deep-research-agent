from groq import Groq
from config import GROQ_API_KEY, MODEL, MAX_RESEARCH_ITERATIONS, MIN_RESEARCH_ITERATIONS
from research.web_search import web_search
from research.rag import retrieve
from research.financial_api import get_stock_data
import json

client = Groq(api_key=GROQ_API_KEY)

class BaseFinancialAgent:
    def __init__(self, sector: str, sector_companies: dict):
        self.sector = sector
        self.sector_companies = sector_companies  # {name: ticker}
        self.research_memory = []  # Stores all findings
        self.queries_used = []
    
    def _get_next_action(self, original_query: str, findings_so_far: str) -> dict:
        prompt = f"""You are a deep financial research analyst for the {self.sector} sector.

Original research goal: {original_query}

What you've found so far:
{findings_so_far[-3000:]}

Queries already used: {self.queries_used[-10:]}

Decide the BEST next research action. Reply ONLY with valid JSON, no extra text:
{{
  "action": "web_search" | "financial_data" | "rag_search" | "done",
  "query": "exact search query to use",
  "reasoning": "why this will deepen the research",
  "ticker": "TICKER_SYMBOL (only if action is financial_data, else empty string)"
}}

STRICT RULES:
- First 2 steps MUST be web_search to get latest news
- Use financial_data only ONCE per ticker
- After financial_data, always follow up with web_search to find context
- Never repeat a query already used
- Use "done" only after at least 5 steps AND you have both news + financial data
- Mix your actions: web_search → financial_data → web_search → rag_search"""

        response = client.chat.completions.create(
             model=MODEL,
             messages=[{"role": "user", "content": prompt}],
             max_tokens=300,
             temperature=0.3
           )

        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        try:
          return json.loads(text)
        except:
          return {"action": "web_search", "query": original_query}
        
    def _assess_query_complexity(self, query: str) -> dict:
        """Ask the model how complex this query is and how many steps it needs."""
        prompt = f"""You are a financial research planner.

Assess the complexity of this research query: "{query}"

Reply ONLY with valid JSON, no extra text:
{{
  "complexity": "simple" | "moderate" | "complex",
  "min_steps": <number>,
  "max_steps": <number>,
  "reasoning": "one sentence explanation"
}}

- simple: single metric questions, stock price, PE ratio, basic facts → min 3, max 6 steps
- moderate: single company full analysis OR sector overview → min 7, max 11 steps
- complex: comparing multiple companies OR sector trends + company combined OR investment strategy → min 12, max 18 steps

Examples:
- "What is Wipro stock price" → simple (3-6 steps)
- "Analyze Infosys financial performance" → moderate (7-11 steps)
- "Compare TCS vs Infosys vs Wipro" → complex (12-18 steps)"""

        response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.1
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        try:
            result = json.loads(text)
            print(f"  Query complexity: {result['complexity']} "
              f"({result['min_steps']}-{result['max_steps']} steps) "
              f"— {result['reasoning']}")
            return result
        except:
            return {"complexity": "moderate", "min_steps": 7, "max_steps": 12}
    
    def run_research(self, query: str) -> str:
        """The core deep research loop with dynamic step count."""
        print(f"\n🔍 Starting deep research: {query}")

    # Assess complexity first
        complexity = self._assess_query_complexity(query)
        min_steps = complexity["min_steps"]
        max_steps = complexity["max_steps"]

        print(f"  Planning {min_steps}–{max_steps} research steps...\n")

        findings = []
        iteration = 0

        while iteration < max_steps:
            iteration += 1
            findings_text = "\n\n".join(
            [f"Finding {i+1}: {f}" for i, f in enumerate(findings)]
           )

            action = self._get_next_action(query, findings_text)
            print(f"  Step {iteration}: {action.get('action')} "
              f"— {action.get('query', '')}")

        # Only allow "done" after minimum steps reached
            if action["action"] == "done" and iteration >= min_steps:
                print(f"Research complete after {iteration} steps.")
                break

        # If model says done too early, force web_search
            if action["action"] == "done" and iteration < min_steps:
                action = {
                "action": "web_search",
                "query": f"{query} latest news analysis {iteration}",
                "reasoning": "Minimum steps not reached yet"
              }

        # Execute the chosen action
            result = ""
            if action["action"] == "web_search":
                search_query = action.get("query", query)
                self.queries_used.append(search_query)
                results = web_search(search_query)
                result = self._format_search_results(results)

            elif action["action"] == "financial_data":
                ticker = action.get("ticker", "").strip()
                if ticker:
                    data = get_stock_data(ticker)
                    result = (f"Financial data for {ticker}:\n"
                         f"{json.dumps(data, indent=2)}")
                else:
                    fallback_query = action.get("query", query)
                    self.queries_used.append(fallback_query)
                    results = web_search(fallback_query)
                    result = self._format_search_results(results)

            elif action["action"] == "rag_search":
                search_query = action.get("query", query)
                docs = retrieve(search_query)
                result = "Document findings:\n" + "\n---\n".join(docs)

            if result:
                findings.append(
                f"[{action['action']}] "
                f"Query: {action.get('query')}\n{result}"
            )

        return "\n\n".join(findings)
    
    def _format_search_results(self, results: list) -> str:
        formatted = []
        for r in results:
            formatted.append(f"Title: {r.get('title')}\n{r.get('content', '')[:500]}")
        return "\n\n".join(formatted)