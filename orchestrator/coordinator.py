from orchestrator.router import classify_sector
from orchestrator.planner import generate_research_plan
from agents.it_agent import ITSectorAgent
from agents.pharma_agent import PharmaSectorAgent
from analysis.synthesizer import generate_report, save_report


def get_agent(sector: str):
    """Return the right sector agent based on classification."""
    if sector == "IT":
        return ITSectorAgent()
    elif sector == "PHARMA":
        return PharmaSectorAgent()
    return None


def run_full_research(query: str) -> str:
    """
    Master coordinator — runs the complete end-to-end research workflow.
    Returns path to the saved report file.
    """

    # Step 1: Classify sector
    print(f"\n Analyzing query...")
    sector = classify_sector(query)

    if sector == "UNKNOWN":
        print("Query is outside financial domain. Please ask about IT or Pharma sectors.")
        return None

    print(f" Sector identified: {sector}")

    # Step 2: Generate research plan
    print(f"\n Generating research plan...")
    plan = generate_research_plan(query, sector)

    # Step 3: Show plan to user and get approval
    print(f"\n{'='*55}")
    print(f"  RESEARCH PLAN  |  Sector: {sector}")
    print(f"{'='*55}")
    print(plan["plan"])
    print(f"{'='*55}")

    approval = input("\nProceed with this plan? (yes / no / modify): ").strip().lower()

    if approval == "no":
        print("Research cancelled.")
        return None

    if approval == "modify":
        extra = input("What should I focus on differently? ").strip()
        query = f"{query}. Additional focus: {extra}"

    # Step 4: Run deep research
    print(f"\n Starting deep research — this may take 1-2 minutes...")
    agent = get_agent(sector)
    raw_findings = agent.run