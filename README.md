# Financial Deep Research Agent

An AI-powered deep research system for Indian IT and Pharma sectors.
Built with Groq LLaMA 3.3, Tavily, yfinance, and ChromaDB.

## Features
- Multi-step adaptive research (5–18 steps based on query complexity)
- Sector-specific agents for IT and Pharma
- Live web search + financial API + RAG document retrieval
- Professional report generation with download
- Beautiful Streamlit UI with research history

## Sectors Covered
- IT Services: TCS, Infosys, Wipro, HCL, LTIMindtree
- Pharmaceuticals: Sun Pharma, Cipla, Dr Reddys, Biocon, Divis Labs

## Setup

1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Create .env file with your API keys:
   GROQ_API_KEY=your_key
   TAVILY_API_KEY=your_key
   ALPHA_VANTAGE_KEY=your_key
4. Run the Streamlit UI:
   streamlit run app.py

## Architecture
- Orchestrator: Query classification and research planning
- Sector Agents: IT and Pharma specialized research agents
- Research Tools: Web search, financial APIs, RAG retrieval
- Analysis: Programmatic financial calculations
- Synthesizer: LLM-powered report generation

## Sample Queries
- "Analyze TCS financial performance FY26"
- "Compare Infosys vs Wipro vs HCL 2025"
- "Sun Pharma biosimilar growth strategy"
- "Indian IT sector trends and outlook 2026"
