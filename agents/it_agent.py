from agents.base_agent import BaseFinancialAgent

IT_COMPANIES = {
    "Infosys": "INFY", "TCS": "TCS.NS", "Wipro": "WIT",
    "HCL Tech": "HCLTECH.NS", "Tech Mahindra": "TECHM.NS",
    "LTIMindtree": "LTIM.NS"
}

class ITSectorAgent(BaseFinancialAgent):
    def __init__(self):
        super().__init__("IT Services", IT_COMPANIES)
        # Add IT-specific context to research
        self.sector_context = """
Focus areas for IT sector research:
- AI/automation impact on revenue and headcount
- Deal wins, client ramp-ups/ramp-downs
- Margin pressure from wage inflation
- US/Europe demand environment
- Cloud migration projects pipeline
- Attrition rates and talent costs"""
    
    def run_research(self, query: str) -> str:
        # Prepend sector context to query for better results
        enriched_query = f"{query}\nSector context: {self.sector_context}"
        return super().run_research(enriched_query)