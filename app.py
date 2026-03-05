import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_connection import create_tables, seed_sample_data
from pages import home, live_matches, top_stats, sql_queries, crud_operations

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Hide Streamlit chrome ──────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── LIGHT background ───────────────────────────────────── */
.stApp { background-color: #f5f7fa; color: #1a1a2e; }

/* ── Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-right: none;
    box-shadow: 3px 0 15px rgba(0,0,0,0.15);
}

/* ── Nav buttons ────────────────────────────────────────── */
.stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: #cdd6f4 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    font-size: 0.92em !important;
    padding: 10px 14px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
    margin-bottom: 4px !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.3) !important;
    color: white !important;
    border-color: rgba(99,102,241,0.5) !important;
    transform: translateX(3px) !important;
}

/* ── Metrics ────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] label { color: #6b7280 !important; font-size:0.82em !important; }
[data-testid="stMetricValue"]          { color: #1a1a2e !important; font-size:1.9em !important; font-weight:700 !important; }
[data-testid="stMetricDelta"]          { font-size:0.82em !important; }

/* ── Cards / containers ─────────────────────────────────── */
[data-testid="stExpander"] {
    background: white;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* ── DataFrames ─────────────────────────────────────────── */
.stDataFrame { border-radius: 10px; border: 1px solid #e8ecf0; overflow: hidden; }

/* ── Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #f0f2f5;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: #6b7280 !important;
    padding: 8px 16px !important;
    border: none !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #6366f1 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12) !important;
    font-weight: 600 !important;
}

/* ── Inputs ─────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: white !important;
    color: #1a1a2e !important;
    border: 1.5px solid #e0e4eb !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus { border-color: #6366f1 !important; }

/* ── Form submit ────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg,#6366f1,#4f46e5) !important;
    color: white !important; border: none !important;
    border-radius: 9px !important; font-weight: 600 !important;
    padding: 10px 20px !important;
}

/* ── Download button ────────────────────────────────────── */
.stDownloadButton > button {
    background: #f0f2f5 !important; color: #374151 !important;
    border: 1px solid #d1d5db !important; border-radius: 8px !important;
}

/* ── Divider ────────────────────────────────────────────── */
hr { border: none; border-top: 1px solid #e8ecf0; margin: 16px 0; }

/* ── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar       { width: 5px; }
::-webkit-scrollbar-track { background: #f0f2f5; }
::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 3px; }

/* ── Radio ──────────────────────────────────────────────── */
.stRadio label { color: #374151 !important; }

/* ── Main content padding ───────────────────────────────── */
.block-container { padding: 28px 36px 40px 36px !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Setting up database…")
def _init_db():
    create_tables(); seed_sample_data(); return True
_init_db()

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:28px 12px 22px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:18px;">
        <div style="color:white;font-size:1.4em;font-weight:700;letter-spacing:.5px;">Cricbuzz</div>
        <div style="color:#8892b0;font-size:0.78em;margin-top:3px;">LiveStats Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    NAV = [
        ("🏠  Home",              "Home"),
        ("📺  Live Matches",      "Live Matches"),
        ("📊  Top Player Stats",  "Top Stats"),
        ("🔍  SQL Analytics",     "SQL Queries"),
        ("🛠️  CRUD Operations",  "CRUD"),
    ]

    for label, key in NAV:
        if st.session_state.page == key:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#6366f1,#4f46e5);
                        border-radius:10px;padding:11px 14px;margin-bottom:18px;
                        color:white;font-weight:600;font-size:0.92em;
                        box-shadow:0 4px 12px rgba(99,102,241,0.4);">
                {label}
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(label, use_container_width=True, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:0 0 14px'>", unsafe_allow_html=True)

    api_key = os.getenv("RAPIDAPI_KEY", "")
    if api_key and api_key != "your_rapidapi_key_here":
        st.markdown("""<div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);
            border-radius:8px;padding:10px;color:#10b981;font-size:0.82em;text-align:center;">
            🔑 <b>API Connected</b><br><span style="color:#8892b0;font-size:.9em;">Live data active</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.35);
            border-radius:8px;padding:10px;color:#f59e0b;font-size:0.82em;text-align:center;">
            🔑 <b>Demo Mode</b><br><span style="color:#8892b0;font-size:.9em;">Using sample data</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="text-align:center;color:#4a5568;font-size:0.72em;margin-top:20px;padding:10px;
        border-top:1px solid rgba(255,255,255,0.06);">
        Built with Streamlit<br>© 2025 Cricbuzz LiveStats
    </div>""", unsafe_allow_html=True)

# ── ROUTER ───────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "Home")
if   page == "Home":          home.show()
elif page == "Live Matches":  live_matches.show()
elif page == "Top Stats":     top_stats.show()
elif page == "SQL Queries":   sql_queries.show()
elif page == "CRUD":          crud_operations.show()
