import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import check_db_health


def show():
    # ── Hero Banner ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                padding: 40px 30px; border-radius: 16px; text-align: center; margin-bottom: 30px;">
        <h1 style="color:#e94560; font-size:3em; margin:0;">🏏 Cricbuzz LiveStats</h1>
        <p style="color:#a8dadc; font-size:1.3em; margin-top:10px;">
            Real-time Cricket Analytics Dashboard
        </p>
        <p style="color:#888; font-size:0.95em;">
            Powered by Cricbuzz API  •  SQL Analytics  •  Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Cards ───────────────────────────────────────────────────────
    st.subheader("📊 Database Overview")
    health = check_db_health()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧑‍🤝‍🧑 Teams",   health.get("teams",   0))
    col2.metric("👤 Players",  health.get("players", 0))
    col3.metric("🏟️ Venues",  health.get("venues",  0))
    col4.metric("🏏 Matches",  health.get("matches", 0))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("📋 Series",        health.get("series",              0))
    col6.metric("🏏 Batting Rows",  health.get("batting_stats",       0))
    col7.metric("🎯 Bowling Rows",  health.get("bowling_stats",       0))
    col8.metric("📈 Career Stats",  health.get("player_career_stats", 0))

    st.divider()

    # ── Navigation Guide ──────────────────────────────────────────────────
    st.subheader("🧭 Pages & Features")

    pages_info = [
        ("📺 Live Matches",      "Real-time scores, scorecards, and match status from the Cricbuzz API."),
        ("📊 Top Player Stats",  "Batting & bowling rankings, career stats, and format comparisons."),
        ("🔍 SQL Analytics",     "25 SQL queries from Beginner → Advanced with live results."),
        ("🛠️ CRUD Operations",  "Add / Edit / Delete players and match records directly in the database."),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(pages_info):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#1e1e2e; border-left:4px solid #e94560;
                        padding:16px 18px; border-radius:10px; margin-bottom:14px;">
                <h4 style="color:#e94560; margin:0 0 6px 0;">{title}</h4>
                <p style="color:#ccc; margin:0; font-size:0.9em;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Tech Stack ────────────────────────────────────────────────────────
    st.subheader("🛠️ Technology Stack")
    cols = st.columns(5)
    techs = [
        ("🐍", "Python 3.10+",    "#3776ab"),
        ("📊", "Streamlit",       "#ff4b4b"),
        ("🗄️", "SQLite / PG",    "#336791"),
        ("🌐", "Cricbuzz API",    "#1da462"),
        ("📈", "Plotly",          "#636efa"),
    ]
    for col, (icon, name, color) in zip(cols, techs):
        col.markdown(f"""
        <div style="background:#1e1e2e; border:1px solid {color};
                    padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:2em;">{icon}</div>
            <div style="color:{color}; font-weight:bold; margin-top:4px;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Setup Instructions ────────────────────────────────────────────────
    st.subheader("Project Overview")
    with st.expander(" Click here to know", expanded=False):
        st.markdown("""
                    ### 📊 Project Overview

The **Cricbuzz Live Stats Dashboard** is an interactive data analytics
application built using **Python, SQL, and Streamlit**.  
It simulates live cricket match analysis using realistic Cricbuzz-style
data and provides powerful insights into player performance, match
statistics, and historical trends.

This project demonstrates **data engineering, API integration, SQL
analytics, and dashboard development skills**.

---
        """)

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:20px; color:#555; margin-top:30px;">
        Built with ❤️ using Python + Streamlit | Data via Cricbuzz API (RapidAPI)
    </div>
    """, unsafe_allow_html=True)
