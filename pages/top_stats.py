# pages/top_stats.py
# ============================================================
# TOP PLAYER STATS PAGE  –  Rankings & Career Statistics
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_helper   import get_top_batsmen, get_top_bowlers
from utils.db_connection import run_query


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _flag(country: str) -> str:
    flags = {
        "India": "🇮🇳", "Australia": "🇦🇺", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "Pakistan": "🇵🇰", "South Africa": "🇿🇦", "New Zealand": "🇳🇿",
        "West Indies": "🏳️", "Sri Lanka": "🇱🇰", "Bangladesh": "🇧🇩",
        "Afghanistan": "🇦🇫",
    }
    return flags.get(country, "🏳️")


def _medal(rank: str) -> str:
    return {"1": "🥇", "2": "🥈", "3": "🥉"}.get(str(rank), f"#{rank}")


# ════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ════════════════════════════════════════════════════════════════════════════

def show():
    st.title("📊 Top Player Statistics")

    tab_bat, tab_bowl, tab_career, tab_compare = st.tabs([
        "🏏 Batting Rankings", "🎯 Bowling Rankings",
        "📈 Career Stats",     "⚡ Format Compare"
    ])

    # ── BATTING RANKINGS ─────────────────────────────────────────────────
    with tab_bat:
        st.subheader("🏏 Top Batsmen Rankings")
        fmt = st.selectbox("Format", ["ODI", "Test", "T20I"], key="bat_fmt")

        with st.spinner("Loading batting rankings…"):
            data = get_top_batsmen(fmt)

        ranks = data.get("rank", [])
        if not ranks:
            st.warning("No ranking data available.")
        else:
            # Cards for top 3
            top3 = ranks[:3]
            cols = st.columns(3)
            for col, r in zip(cols, top3):
                with col:
                    st.markdown(f"""
                    <div style="background:#1e1e2e; border:1px solid #e94560;
                                padding:20px; border-radius:14px; text-align:center;">
                        <div style="font-size:2.5em;">{_medal(r['rank'])}</div>
                        <div style="color:#fff; font-weight:bold; font-size:1.1em; margin:8px 0 4px 0;">
                            {_flag(r['country'])} {r['name']}
                        </div>
                        <div style="color:#aaa; font-size:0.85em;">{r['country']}</div>
                        <div style="color:#e94560; font-size:1.4em; font-weight:bold; margin-top:8px;">
                            ⭐ {r['rating']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # Full table
            df = pd.DataFrame([{
                "Rank":    _medal(r["rank"]),
                "Player":  f"{_flag(r['country'])} {r['name']}",
                "Country": r["country"],
                "Rating":  int(r["rating"]),
            } for r in ranks])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Bar chart
            fig = px.bar(
                df, x="Player", y="Rating", color="Rating",
                color_continuous_scale="Blues",
                title=f"Top {fmt} Batsmen by ICC Rating",
            )
            fig.update_layout(
                plot_bgcolor="#12122a", paper_bgcolor="#1e1e2e",
                font_color="#ccc", xaxis_tickangle=-35,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── BOWLING RANKINGS ─────────────────────────────────────────────────
    with tab_bowl:
        st.subheader("🎯 Top Bowlers Rankings")
        fmt = st.selectbox("Format", ["ODI", "Test", "T20I"], key="bowl_fmt")

        with st.spinner("Loading bowling rankings…"):
            data = get_top_bowlers(fmt)

        ranks = data.get("rank", [])
        if ranks:
            top3 = ranks[:3]
            cols = st.columns(3)
            for col, r in zip(cols, top3):
                with col:
                    st.markdown(f"""
                    <div style="background:#1e1e2e; border:1px solid #2ec4b6;
                                padding:20px; border-radius:14px; text-align:center;">
                        <div style="font-size:2.5em;">{_medal(r['rank'])}</div>
                        <div style="color:#fff; font-weight:bold; font-size:1.1em; margin:8px 0 4px 0;">
                            {_flag(r['country'])} {r['name']}
                        </div>
                        <div style="color:#aaa; font-size:0.85em;">{r['country']}</div>
                        <div style="color:#2ec4b6; font-size:1.4em; font-weight:bold; margin-top:8px;">
                            ⭐ {r['rating']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            df = pd.DataFrame([{
                "Rank":    _medal(r["rank"]),
                "Player":  f"{_flag(r['country'])} {r['name']}",
                "Country": r["country"],
                "Rating":  int(r["rating"]),
            } for r in ranks])
            st.dataframe(df, use_container_width=True, hide_index=True)

            fig = px.bar(
                df, x="Player", y="Rating", color="Rating",
                color_continuous_scale="Blues",
                title=f"Top {fmt} Bowlers by ICC Rating",
            )
            fig.update_layout(
                plot_bgcolor="#12122a", paper_bgcolor="#1e1e2e",
                font_color="#ccc", xaxis_tickangle=-35,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── CAREER STATS (from DB) ────────────────────────────────────────────
    with tab_career:
        st.subheader("📈 Career Statistics (from Database)")

        col1, col2 = st.columns(2)
        with col1:
            country_df = run_query("SELECT DISTINCT country FROM players ORDER BY country")
            countries  = ["All"] + (list(country_df["country"].dropna()) if not country_df.empty else [])
            sel_country = st.selectbox("Filter by Country", countries)
        with col2:
            fmt2 = st.selectbox("Format", ["ODI", "Test", "T20I"], key="career_fmt")

        # Build query
        if sel_country == "All":
            df = run_query(f"""
                SELECT p.full_name AS Player, p.country AS Country,
                       p.playing_role AS Role, c.matches_played AS Matches,
                       c.total_runs AS Runs, c.highest_score AS HS,
                       c.batting_average AS BatAvg,
                       c.batting_strike_rate AS SR,
                       c.centuries AS "100s", c.half_centuries AS "50s",
                       c.total_wickets AS Wickets,
                       c.bowling_average AS BowlAvg,
                       c.economy_rate AS Economy
                FROM player_career_stats c
                JOIN players p ON p.player_id = c.player_id
                WHERE c.format = '{fmt2}'
                ORDER BY c.total_runs DESC
            """)
        else:
            df = run_query(f"""
                SELECT p.full_name AS Player, p.country AS Country,
                       p.playing_role AS Role, c.matches_played AS Matches,
                       c.total_runs AS Runs, c.highest_score AS HS,
                       c.batting_average AS BatAvg,
                       c.batting_strike_rate AS SR,
                       c.centuries AS "100s", c.half_centuries AS "50s",
                       c.total_wickets AS Wickets,
                       c.bowling_average AS BowlAvg,
                       c.economy_rate AS Economy
                FROM player_career_stats c
                JOIN players p ON p.player_id = c.player_id
                WHERE c.format = '{fmt2}' AND p.country = '{sel_country}'
                ORDER BY c.total_runs DESC
            """)

        if df.empty:
            st.info("No data for this selection.")
        else:
            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Players", len(df))
            m2.metric("Highest Runs",  int(df["Runs"].max()) if "Runs" in df else 0)
            m3.metric("Best Average", f"{df['BatAvg'].max():.2f}" if "BatAvg" in df else "0")
            m4.metric("Most Wickets",  int(df["Wickets"].max()) if "Wickets" in df else 0)

            st.dataframe(
                df.style.background_gradient(subset=["Runs"], cmap="Reds")
                        .background_gradient(subset=["Wickets"], cmap="Blues"),
                use_container_width=True, hide_index=True
            )

            # Top scorers chart
            top10 = df.nlargest(10, "Runs")
            fig = px.bar(
                top10, x="Player", y="Runs",
                color="Country", title=f"Top {fmt2} Run Scorers",
                text="Runs",
            )
            fig.update_layout(
                plot_bgcolor="#12122a", paper_bgcolor="#1e1e2e",
                font_color="#ccc", xaxis_tickangle=-35,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── FORMAT COMPARISON ────────────────────────────────────────────────
    with tab_compare:
        st.subheader("⚡ Player Format Comparison")

        player_df = run_query("SELECT DISTINCT full_name FROM players ORDER BY full_name")
        if player_df.empty:
            st.warning("No player data in database.")
            return

        player_names = player_df["full_name"].tolist()
        sel_player   = st.selectbox("Select Player", player_names)

        df = run_query(f"""
            SELECT c.format AS Format,
                   c.matches_played AS Matches,
                   c.total_runs AS Runs,
                   c.batting_average AS BatAvg,
                   c.batting_strike_rate AS SR,
                   c.centuries AS "100s",
                   c.total_wickets AS Wickets,
                   c.economy_rate AS Economy
            FROM player_career_stats c
            JOIN players p ON p.player_id = c.player_id
            WHERE p.full_name = '{sel_player}'
            ORDER BY c.format
        """)

        if df.empty:
            st.info(f"No career data found for {sel_player}.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

            