# pages/live_matches.py
# ============================================================
# LIVE MATCHES PAGE  –  Real-time scores & scorecards
# ============================================================

import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_helper import get_live_matches, get_recent_matches, get_upcoming_matches, get_match_scorecard
from datetime import datetime


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ts_to_str(ts_ms: str) -> str:
    """Convert millisecond timestamp string to readable date."""
    try:
        return datetime.fromtimestamp(int(ts_ms) / 1000).strftime("%d %b %Y, %H:%M")
    except Exception:
        return "N/A"


def _score_str(score_obj: dict, key: str) -> str:
    """Build 'runs/wickets (overs)' string from score dict."""
    try:
        inngs = score_obj.get(key, {})
        if not inngs:
            return "Yet to bat"
        r = inngs.get("runs", 0)
        w = inngs.get("wickets", 10)
        o = inngs.get("overs", 0)
        return f"{r}/{w}  ({o} ov)"
    except Exception:
        return "-"


def _render_match_card(match: dict, color: str = "#e94560"):
    """Render a single match card from matchInfo + matchScore."""
    info  = match.get("matchInfo",  {})
    score = match.get("matchScore", {})

    team1 = info.get("team1", {}).get("teamName",  "Team 1")
    team2 = info.get("team2", {}).get("teamName",  "Team 2")
    t1_sn = info.get("team1", {}).get("teamSName", "T1")
    t2_sn = info.get("team2", {}).get("teamSName", "T2")
    venue = info.get("venueInfo", {})
    ground = venue.get("ground", "Unknown Venue")
    city   = venue.get("city",   "")
    status = info.get("status", "")
    desc   = info.get("matchDesc",   info.get("matchDescription", ""))
    fmt    = info.get("matchFormat", "")
    date   = _ts_to_str(str(info.get("startDate", 0)))

    t1_score = _score_str(score.get("team1Score", {}), "inngs1")
    t2_score = _score_str(score.get("team2Score", {}), "inngs1")

    # format badge colour
    fmt_colors = {"TEST": "#f4a261", "ODI": "#2ec4b6", "T20": "#e94560", "T20I": "#e94560"}
    fmt_color  = fmt_colors.get(fmt.upper(), "#888")

    st.markdown(f"""
    <div style="background:#1e1e2e; border:1px solid {color};
                border-radius:14px; padding:20px 22px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="color:#aaa; font-size:0.85em;">📅 {date}</span>
            <span style="background:{fmt_color}; color:#fff; padding:3px 10px;
                         border-radius:20px; font-size:0.78em; font-weight:bold;">{fmt}</span>
        </div>
        <h3 style="color:#fff; margin:0 0 6px 0;">{team1}  vs  {team2}</h3>
        <p style="color:#aaa; margin:0 0 14px 0; font-size:0.88em;">
            🏟️ {ground}{', ' + city if city else ''}  •  {desc}
        </p>
        <div style="display:flex; gap:20px; margin-bottom:12px;">
            <div style="flex:1; background:#12122a; padding:12px 16px; border-radius:10px;">
                <div style="color:#e94560; font-weight:bold; font-size:0.85em;">{t1_sn}</div>
                <div style="color:#fff; font-size:1.1em; font-weight:bold;">{t1_score}</div>
            </div>
            <div style="flex:1; background:#12122a; padding:12px 16px; border-radius:10px;">
                <div style="color:#2ec4b6; font-weight:bold; font-size:0.85em;">{t2_sn}</div>
                <div style="color:#fff; font-size:1.1em; font-weight:bold;">{t2_score}</div>
            </div>
        </div>
        <div style="background:#0f3460; padding:10px 14px; border-radius:8px;
                    color:#a8dadc; font-size:0.9em; font-weight:bold;">
            📢 {status}
        </div>
    </div>
    """, unsafe_allow_html=True)
    return info.get("matchId")


def _extract_matches(type_matches: list) -> list:
    """Flatten typeMatches → flat list of {matchInfo, matchScore}."""
    result = []
    for tm in type_matches:
        for sm in tm.get("seriesMatches", []):
            wrapper = sm.get("seriesAdWrapper", {})
            for m in wrapper.get("matches", []):
                result.append(m)
    return result


# ════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ════════════════════════════════════════════════════════════════════════════

def show():
    st.title("📺 Live & Recent Matches")
    st.caption("Scores and match info fetched from the Cricbuzz API (or demo data if no key configured)")

    # ── Tab selector ──────────────────────────────────────────────────────
    tab_live, tab_recent, tab_upcoming, tab_scorecard = st.tabs([
        "🔴 Live Now", "✅ Recent", "🗓️ Upcoming", "📋 Scorecard"
    ])

    # ── LIVE ─────────────────────────────────────────────────────────────
    with tab_live:
        st.subheader("🔴 Live Matches")
        with st.spinner("Fetching live data…"):
            raw   = get_live_matches()
            games = _extract_matches(raw)

        if not games:
            st.info("No live matches right now. Check back later!")
        else:
            st.success(f"Found **{len(games)}** live / active match(es)")
            col1, col2 = st.columns([2, 1])
            with col1:
                match_ids = []
                for m in games:
                    mid = _render_match_card(m, "#e94560")
                    match_ids.append(mid)
            with col2:
                st.markdown("#### 📊 Quick Stats")
                formats = [m.get("matchInfo", {}).get("matchFormat", "?") for m in games]
                for fmt in set(formats):
                    cnt = formats.count(fmt)
                    st.metric(f"{fmt} matches", cnt)

    # ── RECENT ───────────────────────────────────────────────────────────
    with tab_recent:
        st.subheader("✅ Recently Completed Matches")
        with st.spinner("Loading recent matches…"):
            raw   = get_recent_matches()
            games = _extract_matches(raw)

        if not games:
            st.info("No recent matches found.")
        else:
            for m in games:
                _render_match_card(m, "#2ec4b6")

    # ── UPCOMING ─────────────────────────────────────────────────────────
    with tab_upcoming:
        st.subheader("🗓️ Upcoming Matches")
        with st.spinner("Fetching schedule…"):
            raw   = get_upcoming_matches()
            games = _extract_matches(raw)

        if not games:
            st.info("No upcoming matches scheduled.")
        else:
            for m in games:
                _render_match_card(m, "#f4a261")

    # ── SCORECARD ────────────────────────────────────────────────────────
    with tab_scorecard:
        st.subheader("📋 Detailed Scorecard")
        match_id = st.number_input(
            "Enter Match ID (try 9001 for demo):",
            min_value=1, value=9001, step=1
        )
        if st.button("🔍 Load Scorecard", use_container_width=True):
            with st.spinner(f"Loading scorecard for match {match_id}…"):
                scard = get_match_scorecard(match_id)

            if not scard:
                st.error("Could not load scorecard. Check the match ID.")
                return

            # ── Header ────────────────────────────────────────────────
            header = scard.get("matchHeader", {})
            st.markdown(f"""
            <div style="background:#1e1e2e; padding:18px 22px; border-radius:12px; margin-bottom:20px;">
                <h3 style="color:#e94560; margin:0;">{header.get('matchDescription','Match')}</h3>
                <p style="color:#aaa; margin:6px 0 0 0;">📢 {header.get('status','')}</p>
            </div>
            """, unsafe_allow_html=True)

            # ── Innings ───────────────────────────────────────────────
            for innings in scard.get("scoreCard", []):
                inn_id  = innings.get("inningsId", "?")
                inn_data = innings.get("inningsData", {})

                bat_team = inn_data.get("batTeamDetails", {})
                bowl_team = inn_data.get("bowlTeamDetails", {})
                score_d  = inn_data.get("scoreDetails", {})

                st.markdown(f"### Innings {inn_id} — {bat_team.get('batTeamName','')}")
                st.caption(f"Score: {score_d.get('runs',0)}/{score_d.get('wickets',0)} ({score_d.get('overs',0)} ov)")

                # Batting table
                bats = bat_team.get("batsmenData", {})
                if bats:
                    import pandas as pd
                    rows = []
                    for b in bats.values():
                        rows.append({
                            "Batsman": b.get("batName",""),
                            "Runs":    b.get("runs",0),
                            "Balls":   b.get("balls",0),
                            "4s":      b.get("fours",0),
                            "6s":      b.get("sixes",0),
                            "SR":      round(b.get("runs",0) / b.get("balls",1) * 100, 1) if b.get("balls",0) else 0,
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)

                # Bowling table
                bowls = bowl_team.get("bowlersData", {})
                if bowls:
                    import pandas as pd
                    rows = []
                    for b in bowls.values():
                        rows.append({
                            "Bowler":   b.get("bowlName",""),
                            "Overs":    b.get("overs","0"),
                            "Runs":     b.get("runs",0),
                            "Wickets":  b.get("wickets",0),
                            "Economy":  round(b.get("runs",0) / float(b.get("overs","1") or 1), 2),
                        })
                    st.caption("Bowling")
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
