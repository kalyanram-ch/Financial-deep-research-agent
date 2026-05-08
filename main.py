from orchestrator.router import classify_sector
from orchestrator.planner import generate_research_plan
from agents.it_agent import ITSectorAgent
from agents.pharma_agent import PharmaSectorAgent
from analysis.synthesizer import generate_report, save_report

def run():
    print("=" * 60)
    print("   Financial Deep Research Agent")
    print("=" * 60)
    
    query = input("\nEnter your research query: ").strip()
    if not query:
        return
    
    # Step 1: Classify and plan
    sector = classify_sector(query)
    if sector == "UNKNOWN":
        print("⚠️  Query doesn't appear finance-related. Please ask about IT or Pharma sectors.")
        return
    
    plan = generate_research_plan(query, sector)
    
    # Step 2: Show plan and get approval
    print(f"\n📋 RESEARCH PLAN (Sector: {sector})\n{'='*50}")
    print(plan["plan"])
    
    approval = input("\nProceed with this plan? (yes/no/modify): ").strip().lower()
    if approval == "no":
        print("Research cancelled.")
        return
    elif approval == "modify":
        additional = input("What should I focus on differently? ")
        query = f"{query}. Additional focus: {additional}"
    
    # Step 3: Run deep research
    print(f"\n🔬 Running deep research ({sector} sector)...")
    
    if sector == "IT":
        agent = ITSectorAgent()
    elif sector == "PHARMA":
        agent = PharmaSectorAgent()
    
    raw_findings = agent.run_research(query)
    
    # Step 4: Synthesize report
    print("\n📝 Generating comprehensive report...")
    report = generate_report(query, sector, raw_findings)
    
    # Step 5: Save and display
    filepath = save_report(report, query)
    print(f"\n✅ Report saved to: {filepath}")
    print("\n" + "="*60 + "\nREPORT PREVIEW\n" + "="*60)
    print(report[:2000] + "\n...[see full report in file]")

if __name__ == "__main__":
    run()