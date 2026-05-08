import streamlit as st
import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.router import classify_sector
from orchestrator.planner import generate_research_plan
from agents.it_agent import ITSectorAgent
from agents.pharma_agent import PharmaSectorAgent
from analysis.synthesizer import generate_report, save_report
from research.web_search import web_search
from research.financial_api import get_stock_data
from research.rag import retrieve

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinResearch AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0a0e1a;
}
.block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1200px;
}

/* ── Hero header ── */
.hero-wrap {
    background: linear-gradient(135deg, #0d1b3e 0%, #0a0e1a 50%, #0d2b1e 100%);
    border: 1px solid rgba(99,202,155,0.15);
    border-radius: 20px;
    padding: 2.8rem 3rem 2.2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(99,202,155,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(56,139,253,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    margin: 0 0 0.5rem;
    letter-spacing: -0.5px;
}
.hero-title span {
    background: linear-gradient(90deg, #63ca9b, #388bfd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: rgba(255,255,255,0.5);
    font-size: 1rem;
    font-weight: 300;
    margin: 0 0 1.8rem;
    letter-spacing: 0.2px;
}
.hero-stats {
    display: flex;
    gap: 2rem;
}
.hero-stat {
    text-align: left;
}
.hero-stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #63ca9b;
}
.hero-stat-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #63ca9b;
    margin-bottom: 0.8rem;
}

/* ── Example query chips ── */
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.2rem;
}
.chip {
    background: rgba(99,202,155,0.08);
    border: 1px solid rgba(99,202,155,0.2);
    color: rgba(255,255,255,0.75);
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.chip:hover {
    background: rgba(99,202,155,0.18);
    border-color: #63ca9b;
    color: #fff;
}

/* ── Input area ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    resize: none !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,202,155,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,202,155,0.08) !important;
}
.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.25) !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #63ca9b, #388bfd) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.3px !important;
    padding: 0.7rem 1.5rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.7) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.25) !important;
    color: #fff !important;
}

/* ── History card ── */
.history-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    cursor: pointer;
    transition: all 0.2s;
}
.history-card:hover {
    background: rgba(99,202,155,0.06);
    border-color: rgba(99,202,155,0.2);
}
.history-card-query {
    color: rgba(255,255,255,0.85);
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.history-card-meta {
    color: rgba(255,255,255,0.35);
    font-size: 0.72rem;
    display: flex;
    gap: 8px;
    align-items: center;
}
.history-badge {
    padding: 1px 8px;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 600;
}
.badge-IT   { background: rgba(56,139,253,0.15); color: #388bfd; }
.badge-PHARMA { background: rgba(99,202,155,0.15); color: #63ca9b; }

/* ── Plan card ── */
.plan-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,202,155,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

/* ── Step log ── */
.step-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
.step-icon {
    width: 24px; height: 24px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
    margin-top: 1px;
}
.icon-web   { background: rgba(56,139,253,0.15); }
.icon-fin   { background: rgba(99,202,155,0.15); }
.icon-rag   { background: rgba(255,170,51,0.15); }
.step-text  { color: rgba(255,255,255,0.7); font-size: 0.83rem; line-height: 1.4; }
.step-num   { color: rgba(255,255,255,0.25); font-size: 0.75rem; flex-shrink: 0; margin-top: 2px; min-width: 20px; }

/* ── Report styling ── */
.report-container {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 2rem;
}
.report-container h1, .report-container h2, .report-container h3 {
    font-family: 'Syne', sans-serif;
    color: #fff;
}
.report-container p, .report-container li {
    color: rgba(255,255,255,0.75);
    line-height: 1.7;
}

/* ── Metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-tile {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
.metric-tile-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: rgba(255,255,255,0.35);
    margin-bottom: 4px;
}
.metric-tile-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #63ca9b;
}

/* ── Progress bar override ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #63ca9b, #388bfd) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 100px !important;
    height: 6px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #080c18 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.75) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,202,155,0.12) !important;
    color: #63ca9b !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: rgba(99,202,155,0.1) !important;
    border: 1px solid rgba(99,202,155,0.3) !important;
    border-radius: 10px !important;
    color: #63ca9b !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(99,202,155,0.18) !important;
    border-color: #63ca9b !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Alerts ── */
.stAlert {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.8) !important;
}
.stSuccess {
    background: rgba(99,202,155,0.08) !important;
    border-color: rgba(99,202,155,0.25) !important;
}
.element-container:has(.stAlert) p { color: rgba(255,255,255,0.8) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "stage": "input",
    "plan": None,
    "sector": None,
    "query": "",
    "report": None,
    "filepath": None,
    "research_steps": [],
    "history": [],          # list of {query, sector, date, report, steps}
    "complexity": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_agent(sector):
    return ITSectorAgent() if sector == "IT" else PharmaSectorAgent()

def reset():
    for k in ["stage","plan","sector","query","report","filepath",
               "research_steps","complexity"]:
        st.session_state[k] = defaults[k]
    st.rerun()

def set_query(q):
    st.session_state.query = q

EXAMPLE_QUERIES = [
    "Analyze Infosys Q4 FY26 financial performance",
    "Compare TCS vs Wipro vs HCL financial health 2025",
    "Indian IT sector trends and outlook 2026",
    "Sun Pharma growth strategy and financials",
    "Biosimilar market trends in Indian pharma",
    "Impact of AI on IT services revenue",
    "Cipla vs Dr Reddys comparative analysis",
    "Cloud migration deals in Indian IT sector",
]


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1.5rem'>
      <div style='font-family:Syne,sans-serif;font-size:1.2rem;
                  font-weight:800;color:#fff;letter-spacing:-0.3px'>
        📈 FinResearch <span style='color:#63ca9b'>AI</span>
      </div>
      <div style='font-size:0.72rem;color:rgba(255,255,255,0.3);
                  text-transform:uppercase;letter-spacing:1.5px;margin-top:2px'>
        Deep Financial Intelligence
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="section-label">Navigation</div>',
                unsafe_allow_html=True)

    if st.button("🏠  Home", use_container_width=True,
                 type="primary" if st.session_state.stage=="input" else "secondary"):
        reset()

    st.markdown("<br>", unsafe_allow_html=True)

    # Covered sectors
    st.markdown('<div class="section-label">Covered Sectors</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex;flex-direction:column;gap:8px;margin-bottom:1.5rem'>
      <div style='background:rgba(56,139,253,0.1);border:1px solid rgba(56,139,253,0.2);
                  border-radius:8px;padding:8px 12px'>
        <div style='font-size:0.8rem;font-weight:600;color:#388bfd'>💻 IT Services</div>
        <div style='font-size:0.72rem;color:rgba(255,255,255,0.4);margin-top:2px'>
          TCS · Infosys · Wipro · HCL · LTI
        </div>
      </div>
      <div style='background:rgba(99,202,155,0.1);border:1px solid rgba(99,202,155,0.2);
                  border-radius:8px;padding:8px 12px'>
        <div style='font-size:0.8rem;font-weight:600;color:#63ca9b'>💊 Pharmaceuticals</div>
        <div style='font-size:0.72rem;color:rgba(255,255,255,0.4);margin-top:2px'>
          Sun Pharma · Cipla · Dr Reddys · Biocon
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Research history
    st.markdown('<div class="section-label">Research History</div>',
                unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div style='color:rgba(255,255,255,0.25);font-size:0.8rem;
                    text-align:center;padding:1rem 0'>
          No research history yet
        </div>""", unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            badge_cls = f"badge-{item['sector']}"
            st.markdown(f"""
            <div class='history-card'>
              <div class='history-card-query'>{item['query'][:55]}{'…' if len(item['query'])>55 else ''}</div>
              <div class='history-card-meta'>
                <span class='history-badge {badge_cls}'>{item['sector']}</span>
                {item['date']} · {item['steps']} steps
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"↩ Reload", key=f"hist_{i}",
                         use_container_width=True):
                st.session_state.query   = item["query"]
                st.session_state.report  = item["report"]
                st.session_state.sector  = item["sector"]
                st.session_state.research_steps = item["steps_log"]
                st.session_state.stage   = "report"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.7rem;color:rgba(255,255,255,0.2);text-align:center'>
      Powered by Groq · Tavily · yfinance<br>
      © 2026 FinResearch AI
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# STAGE 1 — INPUT
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "input":

    # Hero
    st.markdown("""
    <div class='hero-wrap'>
      <div class='hero-title'>Deep Financial<br><span>Research Agent</span></div>
      <div class='hero-sub'>
        Multi-step AI research for Indian IT &amp; Pharma sectors —
        powered by Groq LLaMA 3.3
      </div>
      <div class='hero-stats'>
        <div class='hero-stat'>
          <div class='hero-stat-num'>15+</div>
          <div class='hero-stat-label'>Research Steps</div>
        </div>
        <div class='hero-stat'>
          <div class='hero-stat-num'>2</div>
          <div class='hero-stat-label'>Sectors Covered</div>
        </div>
        <div class='hero-stat'>
          <div class='hero-stat-num'>Live</div>
          <div class='hero-stat-label'>Market Data</div>
        </div>
        <div class='hero-stat'>
          <div class='hero-stat-num'>RAG</div>
          <div class='hero-stat-label'>Doc Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 2], gap="large")

    with col_main:
        # Example queries
        st.markdown('<div class="section-label">Quick Start — Click Any Query</div>',
                    unsafe_allow_html=True)
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLE_QUERIES):
            with cols[i % 2]:
                if st.button(q, key=f"ex_{i}", use_container_width=True):
                    st.session_state.query = q
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Query input
        st.markdown('<div class="section-label">Your Research Query</div>',
                    unsafe_allow_html=True)
        query = st.text_area(
            label="query_input",
            label_visibility="collapsed",
            value=st.session_state.query,
            height=110,
            placeholder="e.g. Analyze the financial performance and growth outlook of Infosys for FY26..."
        )

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            go = st.button("🔍  Generate Research Plan",
                           type="primary", use_container_width=True)
        with col_btn2:
            if st.button("Clear", use_container_width=True):
                st.session_state.query = ""
                st.rerun()

        if go:
            if not query.strip():
                st.warning("Please enter a research query first.")
            else:
                with st.spinner("Analyzing query..."):
                    sector = classify_sector(query)
                if sector == "UNKNOWN":
                    st.error("❌ This query is outside our coverage. "
                             "Please ask about IT or Pharma sectors.")
                else:
                    with st.spinner("Building research plan..."):
                        plan = generate_research_plan(query, sector)
                    st.session_state.query  = query
                    st.session_state.sector = sector
                    st.session_state.plan   = plan
                    st.session_state.stage  = "plan"
                    st.rerun()

    with col_side:
        # How it works
        st.markdown('<div class="section-label">How It Works</div>',
                    unsafe_allow_html=True)
        steps_info = [
            ("01", "🔍", "Query Analysis",
             "AI classifies your query and identifies the research sector"),
            ("02", "📋", "Research Plan",
             "A structured plan is generated and shown for your approval"),
            ("03", "🔬", "Deep Research",
             "Agent runs 5–18 adaptive research steps using web + APIs"),
            ("04", "📄", "Report Generation",
             "Findings are synthesized into a professional report"),
        ]
        for num, icon, title, desc in steps_info:
            st.markdown(f"""
            <div style='display:flex;gap:12px;margin-bottom:1rem;
                        padding:0.9rem;border-radius:12px;
                        background:rgba(255,255,255,0.02);
                        border:1px solid rgba(255,255,255,0.06)'>
              <div style='font-family:Syne,sans-serif;font-size:0.65rem;
                          font-weight:700;color:rgba(99,202,155,0.5);
                          min-width:20px;margin-top:2px'>{num}</div>
              <div>
                <div style='font-size:0.88rem;font-weight:500;
                            color:rgba(255,255,255,0.85);margin-bottom:3px'>
                  {icon} {title}
                </div>
                <div style='font-size:0.78rem;color:rgba(255,255,255,0.35);
                            line-height:1.5'>{desc}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Coverage
        st.markdown('<div class="section-label" style="margin-top:0.5rem">Data Sources</div>',
                    unsafe_allow_html=True)
        sources = [("🌐", "Tavily Web Search", "Live news & reports"),
                   ("📈", "yfinance API", "Real-time market data"),
                   ("📚", "RAG Documents", "Annual reports & filings"),
                   ("🤖", "Groq LLaMA 3.3", "70B reasoning model")]
        for icon, name, desc in sources:
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;
                        padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04)'>
              <span style='font-size:1rem'>{icon}</span>
              <div>
                <div style='font-size:0.82rem;color:rgba(255,255,255,0.75);
                            font-weight:500'>{name}</div>
                <div style='font-size:0.72rem;color:rgba(255,255,255,0.3)'>{desc}</div>
              </div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# STAGE 2 — PLAN APPROVAL
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "plan":

    sector     = st.session_state.sector
    badge_col  = "#388bfd" if sector == "IT" else "#63ca9b"
    badge_bg   = "rgba(56,139,253,0.12)" if sector == "IT" else "rgba(99,202,155,0.12)"

    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='font-family:Syne,sans-serif;font-size:1.6rem;
                  font-weight:800;color:#fff'>Research Plan</div>
      <div style='background:{badge_bg};border:1px solid {badge_col}33;
                  color:{badge_col};padding:4px 14px;border-radius:100px;
                  font-size:0.8rem;font-weight:600'>
        {sector} Sector
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:1rem 1.3rem;margin-bottom:1.5rem'>
      <div style='font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;
                  color:rgba(255,255,255,0.3);margin-bottom:4px'>Your Query</div>
      <div style='color:rgba(255,255,255,0.9);font-size:0.95rem;font-weight:500'>
        {st.session_state.query}
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_plan, col_act = st.columns([3, 2], gap="large")

    with col_plan:
        st.markdown('<div class="section-label">Research Plan</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class='plan-card'>
          <div style='color:rgba(255,255,255,0.8);font-size:0.88rem;line-height:1.7'>
            {st.session_state.plan['plan'].replace(chr(10), '<br>')}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_act:
        st.markdown('<div class="section-label">Refine Focus (Optional)</div>',
                    unsafe_allow_html=True)
        modify = st.text_area(
            label="modify",
            label_visibility="collapsed",
            height=120,
            placeholder="e.g. Focus more on margin analysis and recent deal wins..."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Actions</div>',
                    unsafe_allow_html=True)

        if st.button("✅  Approve & Start Research",
                     type="primary", use_container_width=True):
            if modify.strip():
                st.session_state.query += f". Additional focus: {modify}"
            st.session_state.stage = "research"
            st.rerun()

        if st.button("✏️  Modify Query", use_container_width=True):
            st.session_state.stage = "input"
            st.rerun()

        if st.button("❌  Cancel", use_container_width=True):
            reset()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(99,202,155,0.06);border:1px solid rgba(99,202,155,0.15);
                    border-radius:10px;padding:0.9rem;font-size:0.8rem;
                    color:rgba(255,255,255,0.5);line-height:1.6'>
          💡 The agent will dynamically determine how many research steps
          are needed based on your query complexity (5–18 steps).
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# STAGE 3 — RESEARCH IN PROGRESS
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "research":

    st.markdown("""
    <div style='font-family:Syne,sans-serif;font-size:1.6rem;
                font-weight:800;color:#fff;margin-bottom:0.3rem'>
      🔬 Deep Research Running
    </div>
    <div style='color:rgba(255,255,255,0.4);font-size:0.88rem;margin-bottom:1.5rem'>
      Do not close this window — research is in progress
    </div>
    """, unsafe_allow_html=True)

    st.info(f"**Query:** {st.session_state.query}")

    col_prog, col_log = st.columns([1, 2], gap="large")

    with col_prog:
        progress_bar  = st.progress(0)
        status_box    = st.empty()
        complexity_box = st.empty()

    with col_log:
        st.markdown('<div class="section-label">Live Research Steps</div>',
                    unsafe_allow_html=True)
        log_placeholder = st.empty()

    # ── Run research ──
    agent      = get_agent(st.session_state.sector)
    query      = st.session_state.query
    complexity = agent._assess_query_complexity(query)
    min_steps  = complexity["min_steps"]
    max_steps  = complexity["max_steps"]

    complexity_box.markdown(f"""
    <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                border-radius:10px;padding:0.9rem;margin-bottom:1rem'>
      <div style='font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;
                  color:rgba(255,255,255,0.3);margin-bottom:6px'>Query Complexity</div>
      <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;
                  color:#63ca9b;margin-bottom:2px'>{complexity['complexity'].title()}</div>
      <div style='font-size:0.78rem;color:rgba(255,255,255,0.4)'>
        {min_steps}–{max_steps} research steps planned
      </div>
    </div>
    """, unsafe_allow_html=True)

    findings   = []
    steps_log  = []
    iteration  = 0
    icon_map   = {
        "web_search":    ("🌐", "icon-web"),
        "financial_data":("📈", "icon-fin"),
        "rag_search":    ("📄", "icon-rag"),
    }

    while iteration < max_steps:
        iteration += 1
        findings_text = "\n\n".join(
            [f"Finding {i+1}: {f}" for i, f in enumerate(findings)]
        )
        action = agent._get_next_action(query, findings_text)

        if action["action"] == "done" and iteration >= min_steps:
            break
        if action["action"] == "done" and iteration < min_steps:
            action = {"action": "web_search",
                      "query": f"{query} latest analysis",
                      "reasoning": "Minimum steps not reached"}

        act_type = action.get("action", "web_search")
        act_q    = action.get("query", "")
        icon_e, icon_cls = icon_map.get(act_type, ("🔍", "icon-web"))

        steps_log.append({
            "num": iteration, "icon": icon_e,
            "cls": icon_cls, "type": act_type, "query": act_q
        })

        # Render live log
        log_html = "".join([f"""
        <div class='step-item'>
          <div class='step-num'>#{s['num']}</div>
          <div class='step-icon {s['cls']}'>{s['icon']}</div>
          <div class='step-text'>
            <span style='color:rgba(255,255,255,0.4);font-size:0.75rem'>
              {s['type'].replace('_',' ').title()}
            </span><br>{s['query']}
          </div>
        </div>""" for s in steps_log])
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

        pct = int((iteration / max_steps) * 100)
        progress_bar.progress(pct)
        status_box.markdown(f"""
        <div style='text-align:center;padding:0.5rem'>
          <div style='font-family:Syne,sans-serif;font-size:2rem;
                      font-weight:800;color:#63ca9b'>{pct}%</div>
          <div style='font-size:0.78rem;color:rgba(255,255,255,0.4)'>
            Step {iteration} of ~{max_steps}
          </div>
        </div>""", unsafe_allow_html=True)

        # Execute action
        result = ""
        if act_type == "web_search":
            agent.queries_used.append(act_q)
            results = web_search(act_q)
            result  = agent._format_search_results(results)
        elif act_type == "financial_data":
            ticker = action.get("ticker", "").strip()
            if ticker:
                data   = get_stock_data(ticker)
                result = f"Financial data for {ticker}:\n{json.dumps(data, indent=2)}"
            else:
                agent.queries_used.append(act_q)
                results = web_search(act_q)
                result  = agent._format_search_results(results)
        elif act_type == "rag_search":
            docs   = retrieve(act_q)
            result = "Document findings:\n" + "\n---\n".join(docs)

        if result:
            findings.append(f"[{act_type}] Query: {act_q}\n{result}")

    progress_bar.progress(100)
    status_box.markdown(f"""
    <div style='text-align:center;padding:0.5rem'>
      <div style='font-family:Syne,sans-serif;font-size:2rem;
                  font-weight:800;color:#63ca9b'>✓</div>
      <div style='font-size:0.78rem;color:rgba(255,255,255,0.4)'>
        {iteration} steps complete
      </div>
    </div>""", unsafe_allow_html=True)

    # Generate report
    with st.spinner("Synthesizing report..."):
        raw_findings = "\n\n".join(findings)
        report   = generate_report(query, st.session_state.sector, raw_findings)
        filepath = save_report(report, query)

    # Save to history
    st.session_state.history.append({
        "query":    query,
        "sector":   st.session_state.sector,
        "date":     datetime.now().strftime("%d %b %Y"),
        "steps":    iteration,
        "steps_log": steps_log,
        "report":   report,
    })
    st.session_state.report         = report
    st.session_state.filepath       = filepath
    st.session_state.research_steps = steps_log
    st.session_state.complexity     = complexity
    st.session_state.stage          = "report"
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# STAGE 4 — REPORT
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "report":

    sector    = st.session_state.sector
    badge_col = "#388bfd" if sector == "IT" else "#63ca9b"
    badge_bg  = "rgba(56,139,253,0.12)" if sector == "IT" else "rgba(99,202,155,0.12)"
    n_steps   = len(st.session_state.research_steps)

    st.markdown(f"""
    <div style='display:flex;align-items:center;justify-content:space-between;
                margin-bottom:1.5rem;flex-wrap:wrap;gap:1rem'>
      <div>
        <div style='font-family:Syne,sans-serif;font-size:1.6rem;
                    font-weight:800;color:#fff'>Research Report</div>
        <div style='color:rgba(255,255,255,0.4);font-size:0.85rem;margin-top:2px'>
          Generated {datetime.now().strftime("%d %b %Y, %I:%M %p")}
        </div>
      </div>
      <div style='background:{badge_bg};border:1px solid {badge_col}33;
                  color:{badge_col};padding:6px 18px;border-radius:100px;
                  font-size:0.85rem;font-weight:600'>
        {sector} Sector
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric tiles
    st.markdown(f"""
    <div class='metric-row'>
      <div class='metric-tile'>
        <div class='metric-tile-label'>Research Steps</div>
        <div class='metric-tile-value'>{n_steps}</div>
      </div>
      <div class='metric-tile'>
        <div class='metric-tile-label'>Complexity</div>
        <div class='metric-tile-value' style='font-size:1rem'>
          {st.session_state.complexity['complexity'].title() if st.session_state.complexity else 'N/A'}
        </div>
      </div>
      <div class='metric-tile'>
        <div class='metric-tile-label'>Sector</div>
        <div class='metric-tile-value' style='color:{badge_col}'>{sector}</div>
      </div>
      <div class='metric-tile'>
        <div class='metric-tile-label'>Data Sources</div>
        <div class='metric-tile-value'>3</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Query recap
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1.5rem'>
      <span style='font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;
                   color:rgba(255,255,255,0.3)'>Query · </span>
      <span style='color:rgba(255,255,255,0.8);font-size:0.9rem'>
        {st.session_state.query}
      </span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📄  Full Report", "🔍  Research Steps", "⬇️  Download"])

    with tab1:
        st.markdown(
            f"<div class='report-container'>{st.session_state.report}</div>",
            unsafe_allow_html=True
        )

    with tab2:
        st.markdown('<div class="section-label">All Research Steps Executed</div>',
                    unsafe_allow_html=True)
        icon_map = {
            "web_search":    ("🌐", "icon-web", "#388bfd"),
            "financial_data":("📈", "icon-fin", "#63ca9b"),
            "rag_search":    ("📄", "icon-rag", "#ffaa33"),
        }
        web_count = sum(1 for s in st.session_state.research_steps
                        if s["type"]=="web_search")
        fin_count = sum(1 for s in st.session_state.research_steps
                        if s["type"]=="financial_data")
        rag_count = sum(1 for s in st.session_state.research_steps
                        if s["type"]=="rag_search")

        st.markdown(f"""
        <div style='display:flex;gap:1rem;margin-bottom:1.2rem'>
          <div style='background:rgba(56,139,253,0.1);border:1px solid rgba(56,139,253,0.2);
                      border-radius:8px;padding:6px 14px;font-size:0.8rem;color:#388bfd'>
            🌐 Web Search · {web_count}
          </div>
          <div style='background:rgba(99,202,155,0.1);border:1px solid rgba(99,202,155,0.2);
                      border-radius:8px;padding:6px 14px;font-size:0.8rem;color:#63ca9b'>
            📈 Financial Data · {fin_count}
          </div>
          <div style='background:rgba(255,170,51,0.1);border:1px solid rgba(255,170,51,0.2);
                      border-radius:8px;padding:6px 14px;font-size:0.8rem;color:#ffaa33'>
            📄 RAG Search · {rag_count}
          </div>
        </div>
        """, unsafe_allow_html=True)

        for s in st.session_state.research_steps:
            icon_e, icon_cls, col = icon_map.get(s["type"], ("🔍","icon-web","#888"))
            st.markdown(f"""
            <div class='step-item'>
              <div class='step-num'>#{s['num']}</div>
              <div class='step-icon {icon_cls}'>{icon_e}</div>
              <div class='step-text'>
                <span style='color:{col};font-size:0.75rem;font-weight:500'>
                  {s['type'].replace('_',' ').title()}
                </span><br>{s['query']}
              </div>
            </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div style='text-align:center;padding:2rem 0 1rem'>
          <div style='font-family:Syne,sans-serif;font-size:1.3rem;
                      font-weight:700;color:#fff;margin-bottom:0.5rem'>
            Download Your Report
          </div>
          <div style='color:rgba(255,255,255,0.4);font-size:0.88rem;margin-bottom:1.5rem'>
            Save the full research report to your device
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
        with col_d2:
            filename = os.path.basename(st.session_state.filepath) \
                       if st.session_state.filepath else "report.md"

            st.download_button(
                label="⬇️  Download as Markdown (.md)",
                data=st.session_state.report,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="⬇️  Download as Text (.txt)",
                data=st.session_state.report,
                file_name=filename.replace(".md", ".txt"),
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄  Start New Research", type="primary",
                 use_container_width=True):
        reset()