from agents.base_agent import BaseFinancialAgent

PHARMA_COMPANIES = {
    "Sun Pharma": "SUNPHARMA.NS",
    "Cipla": "CIPLA.NS",
    "Dr Reddys": "DRREDDY.NS",
    "Divi's Labs": "DIVISLAB.NS",
    "Biocon": "BIOCON.NS"
}

class PharmaSectorAgent(BaseFinancialAgent):
    def __init__(self):
        super().__init__("Pharmaceuticals", PHARMA_COMPANIES)
        self.sector_context = """
Focus areas for pharma sector research:
- USFDA approvals and warning letters
- API (Active Pharmaceutical Ingredient) exports
- Biosimilar pipeline and launches
- Domestic formulations vs exports split
- R&D spend as % of revenue
- Patent cliffs and generic opportunities"""
    
    def run_research(self, query: str) -> str:
        enriched_query = f"{query}\nSector context: {self.sector_context}"
        return super().run_research(enriched_query)