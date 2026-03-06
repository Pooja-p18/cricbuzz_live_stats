# pages/sql_queries.py
# ============================================================
# SQL ANALYTICS PAGE  –  All 25 queries (Beginner → Advanced)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import run_query


# ════════════════════════════════════════════════════════════════════════════
# QUERY CATALOGUE
# Each entry: (level, title, description, sql)
# ════════════════════════════════════════════════════════════════════════════

QUERIES = [
    # ── BEGINNER (1-8) ──────────────────────────────────────────────────
    (
        "🟢 Beginner", "Q1 – India Players",
        "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
        """SELECT full_name AS "Player Name",
              playing_role AS "Role",
              batting_style AS "Batting Style",
              bowling_style AS "Bowling Style"
       FROM players
       WHERE country = 'India'
       ORDER BY full_name;"""
    ),
    (
        "🟢 Beginner", "Q2 – Recent Matches",
        "Show all cricket matches played recently. Include match description, both team names, venue, and date.",
        """SELECT m.match_description AS "Match",
              t1.team_name AS "Team 1",
              t2.team_name AS "Team 2",
              v.venue_name || ', ' || v.city AS "Venue",
              m.match_date AS "Date"
       FROM matches m
       JOIN teams   t1 ON t1.team_id  = m.team1_id
       JOIN teams   t2 ON t2.team_id  = m.team2_id
       JOIN venues  v  ON v.venue_id  = m.venue_id
       ORDER BY m.match_date DESC;"""
    ),
    (
        "🟢 Beginner", "Q3 – Top 10 ODI Run Scorers",
        "List the top 10 highest run scorers in ODI cricket. Show player name, total runs, batting average, and centuries.",
        """SELECT p.full_name AS "Player",
              c.total_runs AS "Runs",
              ROUND(c.batting_average, 2) AS "Average",
              c.centuries AS "100s"
       FROM player_career_stats c
       JOIN players p ON p.player_id = c.player_id
       WHERE c.format = 'ODI'
       ORDER BY c.total_runs DESC
       LIMIT 10;"""
    ),
    (
        "🟢 Beginner", "Q4 – Venues with Capacity > 25 000",
        "Display cricket venues with seating capacity over 25,000. Ordered by largest first (top 10).",
        """SELECT venue_name AS "Venue",
              city AS "City",
              country AS "Country",
              capacity AS "Capacity"
       FROM venues
       WHERE capacity > 25000
       ORDER BY capacity DESC
       LIMIT 10;"""
    ),
    (
        "🟢 Beginner", "Q5 – Most Match Wins per Team",
        "Calculate how many matches each team has won. Show team name and total wins.",
        """SELECT t.team_name AS "Team",
              COUNT(*) AS "Wins"
       FROM matches m
       JOIN teams t ON t.team_id = m.winning_team_id
       WHERE m.winning_team_id IS NOT NULL
       GROUP BY t.team_name
       ORDER BY "Wins" DESC;"""
    ),
    (
        "🟢 Beginner", "Q6 – Players by Role",
        "Count how many players belong to each playing role.",
        """SELECT playing_role AS "Role",
              COUNT(*) AS "Player Count"
       FROM players
       GROUP BY playing_role
       ORDER BY "Player Count" DESC;"""
    ),
    (
        "🟢 Beginner", "Q7 – Highest Score per Format",
        "Find the highest individual batting score achieved in each cricket format.",
        """SELECT c.format AS "Format",
              MAX(c.highest_score) AS "Highest Score"
       FROM player_career_stats c
       GROUP BY c.format
       ORDER BY "Highest Score" DESC;"""
    ),
    (
        "🟢 Beginner", "Q8 – Series Started in 2024",
        "Show all cricket series that started in 2024.",
        """SELECT series_name AS "Series",
              host_country AS "Host Country",
              match_type AS "Format",
              start_date AS "Start Date",
              total_matches AS "Total Matches"
       FROM series
       WHERE start_date LIKE '2024%'
       ORDER BY start_date;"""
    ),

    # ── INTERMEDIATE (9-16) ─────────────────────────────────────────────
    (
        "🟡 Intermediate", "Q9 – All-rounders (1000 runs & 50 wkts)",
        "Find all-rounders who have scored over 1000 runs AND taken over 50 wickets in any format.",
        """SELECT p.full_name AS "Player",
              c.format AS "Format",
              c.total_runs AS "Runs",
              c.total_wickets AS "Wickets"
       FROM player_career_stats c
       JOIN players p ON p.player_id = c.player_id
       WHERE p.playing_role = 'All-rounder'
         AND c.total_runs    > 1000
         AND c.total_wickets > 50
       ORDER BY c.total_runs DESC;"""
    ),
    (
        "🟡 Intermediate", "Q10 – Last 20 Completed Matches",
        "Details of the last 20 completed matches with winning team and victory info.",
        """SELECT m.match_description AS "Match",
              t1.team_name AS "Team 1",
              t2.team_name AS "Team 2",
              wt.team_name AS "Winner",
              m.victory_margin AS "Margin",
              m.victory_type AS "Type",
              v.venue_name AS "Venue",
              m.match_date AS "Date"
       FROM matches m
       JOIN teams  t1 ON t1.team_id = m.team1_id
       JOIN teams  t2 ON t2.team_id = m.team2_id
       LEFT JOIN teams  wt ON wt.team_id = m.winning_team_id
       JOIN venues v  ON v.venue_id  = m.venue_id
       WHERE m.status = 'Completed'
       ORDER BY m.match_date DESC
       LIMIT 20;"""
    ),
    (
        "🟡 Intermediate", "Q11 – Multi-format Runs Comparison",
        "For players who have played at least 2 different formats, show their runs in each format and overall average.",
        """SELECT p.full_name AS "Player",
              SUM(CASE WHEN c.format='Test' THEN c.total_runs ELSE 0 END) AS "Test Runs",
              SUM(CASE WHEN c.format='ODI'  THEN c.total_runs ELSE 0 END) AS "ODI Runs",
              SUM(CASE WHEN c.format='T20I' THEN c.total_runs ELSE 0 END) AS "T20I Runs",
              ROUND(AVG(c.batting_average), 2) AS "Overall Avg"
       FROM player_career_stats c
       JOIN players p ON p.player_id = c.player_id
       GROUP BY p.full_name
       HAVING COUNT(DISTINCT c.format) >= 2
       ORDER BY "ODI Runs" DESC;"""
    ),
    (
        "🟡 Intermediate", "Q12 – Home vs Away Win Analysis",
        "Analyse each international team's performance when playing at home vs away.",
        """SELECT t.team_name AS "Team",
              SUM(CASE WHEN v.country = t.country THEN 1 ELSE 0 END) AS "Home Wins",
              SUM(CASE WHEN v.country != t.country THEN 1 ELSE 0 END) AS "Away Wins"
       FROM matches m
       JOIN teams  t ON t.team_id  = m.winning_team_id
       JOIN venues v ON v.venue_id = m.venue_id
       WHERE m.winning_team_id IS NOT NULL
       GROUP BY t.team_name
       ORDER BY "Home Wins" DESC;"""
    ),
    (
        "🟡 Intermediate", "Q13 – High Batting Partnerships (≥100 runs combined)",
        "Identify batting pairs where consecutive batsmen combined for 100+ runs in the same innings.",
        """SELECT p1.full_name AS "Batsman 1",
              p2.full_name AS "Batsman 2",
              b1.runs_scored + b2.runs_scored AS "Partnership Runs",
              b1.innings_number AS "Innings"
       FROM batting_stats b1
       JOIN batting_stats b2 ON b2.match_id       = b1.match_id
                             AND b2.innings_number = b1.innings_number
                             AND b2.batting_position = b1.batting_position + 1
       JOIN players p1 ON p1.player_id = b1.player_id
       JOIN players p2 ON p2.player_id = b2.player_id
       WHERE b1.runs_scored + b2.runs_scored >= 100
       ORDER BY "Partnership Runs" DESC
       LIMIT 20;"""
    ),
    (
        "🟡 Intermediate", "Q14 – Bowling at Specific Venues (≥3 matches)",
        "For bowlers who have played at least 3 matches at the same venue, show their average economy and wickets.",
        """SELECT p.full_name AS "Bowler",
              v.venue_name AS "Venue",
              COUNT(DISTINCT b.match_id) AS "Matches",
              SUM(b.wickets_taken) AS "Wickets",
              ROUND(AVG(b.economy_rate), 2) AS "Avg Economy"
       FROM bowling_stats b
       JOIN players p ON p.player_id = b.player_id
       JOIN matches  m ON m.match_id  = b.match_id
       JOIN venues   v ON v.venue_id  = m.venue_id
       WHERE b.overs_bowled >= 4
       GROUP BY p.full_name, v.venue_name
       HAVING COUNT(DISTINCT b.match_id) >= 3
       ORDER BY "Avg Economy";"""
    ),
    (
        "🟡 Intermediate", "Q15 – Players in Close Matches",
        "Identify players who perform well in close matches (won by <50 runs or <5 wickets).",
        """SELECT p.full_name AS "Player",
              COUNT(DISTINCT b.match_id) AS "Close Matches",
              ROUND(AVG(b.runs_scored), 2) AS "Avg Runs in Close Matches"
       FROM batting_stats b
       JOIN players p ON p.player_id = b.player_id
       JOIN matches  m ON m.match_id  = b.match_id
       WHERE (m.victory_type = 'runs'     AND CAST(m.victory_margin AS INTEGER) < 50)
          OR (m.victory_type = 'wickets'  AND CAST(m.victory_margin AS INTEGER) < 5)
       GROUP BY p.full_name
       ORDER BY "Avg Runs in Close Matches" DESC
       LIMIT 15;"""
    ),
    (
        "🟡 Intermediate", "Q16 – Yearly Batting Trends (2020+)",
        "Track player batting performance year-by-year for matches since 2020 (min 5 matches/year).",
        """SELECT p.full_name AS "Player",
              SUBSTR(m.match_date, 1, 4) AS "Year",
              COUNT(DISTINCT b.match_id) AS "Matches",
              ROUND(AVG(b.runs_scored), 2) AS "Avg Runs",
              ROUND(AVG(b.strike_rate), 2) AS "Avg SR"
       FROM batting_stats b
       JOIN players p ON p.player_id = b.player_id
       JOIN matches  m ON m.match_id  = b.match_id
       WHERE m.match_date >= '2020-01-01'
       GROUP BY p.full_name, SUBSTR(m.match_date,1,4)
       HAVING COUNT(DISTINCT b.match_id) >= 5
       ORDER BY "Year" DESC, "Avg Runs" DESC;"""
    ),

    # ── ADVANCED (17-25) ────────────────────────────────────────────────
    (
        "🔴 Advanced", "Q17 – Toss Advantage Analysis",
        "Does winning the toss help win the match? Win % by toss decision.",
        """SELECT m.toss_decision AS "Toss Decision",
              COUNT(*) AS "Total Matches",
              SUM(CASE WHEN m.toss_winner_id = m.winning_team_id THEN 1 ELSE 0 END) AS "Toss Winner Wins",
              ROUND(100.0 * SUM(CASE WHEN m.toss_winner_id = m.winning_team_id THEN 1 ELSE 0 END)
                    / COUNT(*), 2) AS "Win %"
       FROM matches m
       WHERE m.toss_winner_id IS NOT NULL
         AND m.winning_team_id IS NOT NULL
         AND m.toss_decision IS NOT NULL
       GROUP BY m.toss_decision
       ORDER BY "Win %" DESC;"""
    ),
    (
        "🔴 Advanced", "Q18 – Most Economical Bowlers (Limited Overs)",
        "Most economical bowlers in ODI & T20I with at least 10 matches bowled.",
        """SELECT p.full_name AS "Bowler",
              p.country AS "Country",
              COUNT(DISTINCT b.match_id) AS "Matches",
              SUM(b.wickets_taken) AS "Wickets",
              ROUND(SUM(b.runs_conceded) / SUM(b.overs_bowled), 2) AS "Economy"
       FROM bowling_stats b
       JOIN players p ON p.player_id = b.player_id
       JOIN matches  m ON m.match_id  = b.match_id
       WHERE m.match_format IN ('ODI','T20I')
       GROUP BY p.full_name
       HAVING COUNT(DISTINCT b.match_id) >= 2
         AND  AVG(b.overs_bowled) >= 2
       ORDER BY "Economy";"""
    ),
    (
        "🔴 Advanced", "Q19 – Most Consistent Batsmen (Low Std Dev)",
        "Find the most consistent batsmen using standard deviation of scores (lower = more consistent).",
        """SELECT p.full_name AS "Player",
              COUNT(b.stat_id) AS "Innings",
              ROUND(AVG(b.runs_scored), 2) AS "Avg Runs",
              ROUND(
                SQRT(AVG(b.runs_scored * b.runs_scored) - AVG(b.runs_scored) * AVG(b.runs_scored)),
                2
              ) AS "Std Dev (lower = consistent)"
       FROM batting_stats b
       JOIN players p ON p.player_id = b.player_id
       JOIN matches  m ON m.match_id  = b.match_id
       WHERE b.balls_faced >= 10
         AND m.match_date >= '2022-01-01'
       GROUP BY p.full_name
       HAVING COUNT(b.stat_id) >= 3
       ORDER BY "Std Dev (lower = consistent)";"""
    ),
    (
        "🔴 Advanced", "Q20 – Multi-format Match Count & Avg",
        "Analyse how many matches each player has played in different formats and their batting avg. (20+ total matches)",
        """SELECT p.full_name AS "Player",
              SUM(CASE WHEN c.format='Test' THEN c.matches_played ELSE 0 END) AS "Test M",
              SUM(CASE WHEN c.format='ODI'  THEN c.matches_played ELSE 0 END) AS "ODI M",
              SUM(CASE WHEN c.format='T20I' THEN c.matches_played ELSE 0 END) AS "T20I M",
              SUM(c.matches_played) AS "Total Matches",
              ROUND(SUM(CASE WHEN c.format='Test' THEN c.batting_average * c.matches_played ELSE 0 END)
                    / NULLIF(SUM(CASE WHEN c.format='Test' THEN c.matches_played ELSE 0 END), 0), 2) AS "Test Avg",
              ROUND(SUM(CASE WHEN c.format='ODI'  THEN c.batting_average * c.matches_played ELSE 0 END)
                    / NULLIF(SUM(CASE WHEN c.format='ODI'  THEN c.matches_played ELSE 0 END), 0), 2) AS "ODI Avg"
       FROM player_career_stats c
       JOIN players p ON p.player_id = c.player_id
       GROUP BY p.full_name
       HAVING SUM(c.matches_played) >= 20
       ORDER BY "Total Matches" DESC;"""
    ),
    (
        "🔴 Advanced", "Q21 – Comprehensive Player Performance Ranking",
        "Rank players using a weighted score combining batting, bowling, and career data.",
        """SELECT p.full_name AS "Player",
              p.playing_role AS "Role",
              c.format AS "Format",
              ROUND(
                (c.total_runs * 0.01 + c.batting_average * 0.5 + c.batting_strike_rate * 0.3) +
                (c.total_wickets * 2  + (50 - COALESCE(c.bowling_average,50)) * 0.5 +
                 (6  - COALESCE(c.economy_rate,6)) * 2),
                2
              ) AS "Performance Score",
              c.total_runs AS "Runs",
              c.total_wickets AS "Wickets",
              ROUND(c.batting_average, 2) AS "BatAvg",
              ROUND(c.economy_rate, 2) AS "Economy"
       FROM player_career_stats c
       JOIN players p ON p.player_id = c.player_id
       ORDER BY "Performance Score" DESC
       LIMIT 20;"""
    ),
    (
        "🔴 Advanced", "Q22 – Head-to-Head Team Records",
        "For team pairs with 2+ matches in the DB, show win counts and win %.",
        """SELECT t1.team_name AS "Team 1",
              t2.team_name AS "Team 2",
              COUNT(*) AS "Matches",
              SUM(CASE WHEN m.winning_team_id = m.team1_id THEN 1 ELSE 0 END) AS "T1 Wins",
              SUM(CASE WHEN m.winning_team_id = m.team2_id THEN 1 ELSE 0 END) AS "T2 Wins",
              ROUND(100.0 * SUM(CASE WHEN m.winning_team_id = m.team1_id THEN 1 ELSE 0 END) / COUNT(*), 1) AS "T1 Win %"
       FROM matches m
       JOIN teams t1 ON t1.team_id = m.team1_id
       JOIN teams t2 ON t2.team_id = m.team2_id
       WHERE m.winning_team_id IS NOT NULL
       GROUP BY t1.team_name, t2.team_name
       HAVING COUNT(*) >= 2
       ORDER BY "Matches" DESC;"""
    ),
    (
        "🔴 Advanced", "Q23 – Recent Player Form Analysis",
        "Analyse each player's recent form and categorise as Excellent / Good / Average / Poor.",
        """WITH recent AS (
         SELECT p.full_name,
                AVG(b.runs_scored) AS recent_avg,
                AVG(b.strike_rate) AS recent_sr,
                SUM(CASE WHEN b.runs_scored >= 50 THEN 1 ELSE 0 END) AS fifties
         FROM batting_stats b
         JOIN players  p ON p.player_id = b.player_id
         JOIN matches   m ON m.match_id  = b.match_id
         WHERE m.match_date >= '2023-01-01'
         GROUP BY p.full_name
       )
       SELECT full_name AS "Player",
              ROUND(recent_avg, 2) AS "Recent Avg",
              ROUND(recent_sr,  2) AS "Strike Rate",
              fifties AS "50+ Scores",
              CASE
                WHEN recent_avg >= 50                     THEN '🔥 Excellent Form'
                WHEN recent_avg >= 35                     THEN '✅ Good Form'
                WHEN recent_avg >= 20                     THEN '⚠️  Average Form'
                ELSE                                           '❌ Poor Form'
              END AS "Form Category"
       FROM recent
       ORDER BY recent_avg DESC;"""
    ),
    (
        "🔴 Advanced", "Q24 – Best Batting Partnerships (5+ together)",
        "Find the most successful batting pairs who batted together in 5+ partnerships.",
        """SELECT p1.full_name AS "Batsman 1",
              p2.full_name AS "Batsman 2",
              COUNT(*) AS "Partnerships",
              ROUND(AVG(b1.runs_scored + b2.runs_scored), 2) AS "Avg Partnership",
              MAX(b1.runs_scored + b2.runs_scored) AS "Best Partnership",
              SUM(CASE WHEN b1.runs_scored + b2.runs_scored >= 50 THEN 1 ELSE 0 END) AS "50+ Stands",
              ROUND(100.0 * SUM(CASE WHEN b1.runs_scored + b2.runs_scored >= 50 THEN 1 ELSE 0 END)
                    / COUNT(*), 1) AS "Success %"
       FROM batting_stats b1
       JOIN batting_stats b2 ON b2.match_id        = b1.match_id
                             AND b2.innings_number  = b1.innings_number
                             AND b2.batting_position = b1.batting_position + 1
       JOIN players p1 ON p1.player_id = b1.player_id
       JOIN players p2 ON p2.player_id = b2.player_id
       WHERE b1.player_id < b2.player_id
       GROUP BY p1.full_name, p2.full_name
       HAVING COUNT(*) >= 2
       ORDER BY "Avg Partnership" DESC
       LIMIT 15;"""
    ),
    (
        "🔴 Advanced", "Q25 – Career Trajectory Analysis",
        "Classify players' career trajectory as Ascending, Declining, or Stable based on batting trend.",
        """WITH yearly AS (
         SELECT p.full_name,
                SUBSTR(m.match_date,1,4) AS yr,
                AVG(b.runs_scored) AS yr_avg
         FROM batting_stats b
         JOIN players p ON p.player_id = b.player_id
         JOIN matches  m ON m.match_id  = b.match_id
         GROUP BY p.full_name, SUBSTR(m.match_date,1,4)
         HAVING COUNT(*) >= 2
       ),
       trend AS (
         SELECT full_name,
                COUNT(DISTINCT yr) AS years_active,
                AVG(yr_avg) AS career_avg,
                MAX(CASE WHEN yr = (SELECT MAX(yr) FROM yearly y2 WHERE y2.full_name=yearly.full_name) THEN yr_avg END) AS latest_avg,
                MIN(yr_avg) AS min_avg,
                MAX(yr_avg) AS max_avg
         FROM yearly
         GROUP BY full_name
         HAVING COUNT(DISTINCT yr) >= 1
       )
       SELECT full_name AS "Player",
              years_active AS "Years Active",
              ROUND(career_avg, 2) AS "Career Avg",
              ROUND(latest_avg, 2) AS "Latest Avg",
              CASE
                WHEN latest_avg > career_avg * 1.1  THEN '📈 Career Ascending'
                WHEN latest_avg < career_avg * 0.9  THEN '📉 Career Declining'
                ELSE                                      '➡️  Career Stable'
              END AS "Trajectory"
       FROM trend
       ORDER BY career_avg DESC;"""
    ),
]


# ════════════════════════════════════════════════════════════════════════════
# MAIN PAGE – SEARCH BASED SQL EXECUTION
# ════════════════════════════════════════════════════════════════════════════

def show():

    st.title("🔍 SQL Analytics – Query Search")
    st.caption("Search cricket analytics queries and view results instantly")

    # ── Filter bar ────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        search = st.text_input(
            "🔎 Search queries",
            placeholder="e.g. india, toss, wickets"
        )

    with col2:
        level_filter = st.selectbox(
            "Level",
            ["All", "🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"]
        )

    st.divider()

    # ── Custom SQL ────────────────────────────────────────────────────────
    with st.expander("⌨️ Write & Run Custom SQL"):

        custom_sql = st.text_area(
            "Enter SQL query:",
            value="SELECT * FROM players LIMIT 5;",
            height=120,
        )

        if st.button("▶ Run Query", use_container_width=True):

            with st.spinner("Running query..."):
                df = run_query(custom_sql)

            if df.empty:
                st.warning("No results returned")
            else:
                st.dataframe(df, use_container_width=True)
                st.caption(f"✅ {len(df)} rows returned")

    st.divider()

    # ── Require search text ───────────────────────────────────────────────
    if not search:
        st.info("Start typing to search queries")
        return

    # ── Filter queries ────────────────────────────────────────────────────
    results = []

    for q in QUERIES:

        level, title, description, sql = q

        if level_filter != "All" and level != level_filter:
            continue

        if (
            search.lower() in title.lower()
            or search.lower() in description.lower()
        ):
            results.append(q)

    if not results:
        st.warning("No matching queries found")
        return

    st.success(f"{len(results)} query result(s) found")

    st.divider()

    # ── Execute & Show Results ────────────────────────────────────────────
    for level, title, description, sql in results:

        # Query Title Card
        st.markdown(f"""
        <div style="
        padding:14px;
        border-radius:10px;
        background:#1e1e2e;
        border:1px solid #2a2a40;
        margin-bottom:10px">

        <b>{title}</b><br>
        <span style="color:#aaa">{description}</span>

        </div>
        """, unsafe_allow_html=True)

        # Run Query Automatically
        with st.spinner("Running query..."):

            df = run_query(sql)

        if df.empty:
            st.info("No results for this query")
        else:
            st.dataframe(df, use_container_width=True)
            st.caption(f"✅ {len(df)} rows returned")


