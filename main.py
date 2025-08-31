import streamlit as st
import pandas as pd
import requests
import sqlite3
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import time
import os
class CricbuzzAPI:
    def __init__(self):
        self.api_key = "654779fc79mshf63666cb2a48234p120fe6jsnb482c47c1bbb"  # <-- Put your key here
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
        }

# Page configuration
st.set_page_config(
    page_title="🏏 Cricbuzz LiveStats Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Setup and Connection
class DatabaseManager:
    def __init__(self, db_name: str = "cricket_analytics.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Teams table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            team_type TEXT DEFAULT 'International',
            founded_year INTEGER,
            home_ground TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Players table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            team_id INTEGER,
            country TEXT NOT NULL,
            playing_role TEXT DEFAULT 'Batsman',
            batting_style TEXT,
            bowling_style TEXT,
            date_of_birth DATE,
            debut_date DATE,
            matches_played INTEGER DEFAULT 0,
            total_runs INTEGER DEFAULT 0,
            batting_average REAL DEFAULT 0.0,
            strike_rate REAL DEFAULT 0.0,
            centuries INTEGER DEFAULT 0,
            half_centuries INTEGER DEFAULT 0,
            total_wickets INTEGER DEFAULT 0,
            bowling_average REAL DEFAULT 0.0,
            economy_rate REAL DEFAULT 0.0,
            catches INTEGER DEFAULT 0,
            stumpings INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (team_id)
        )
        """)
        
        # Venues table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            venue_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            capacity INTEGER,
            established_year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Matches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_description TEXT NOT NULL,
            series_name TEXT,
            match_format TEXT DEFAULT 'ODI',
            team1_id INTEGER,
            team2_id INTEGER,
            venue_id INTEGER,
            match_date DATE,
            match_status TEXT DEFAULT 'completed',
            toss_winner_id INTEGER,
            toss_decision TEXT DEFAULT 'bat',
            winner_id INTEGER,
            victory_margin INTEGER,
            victory_type TEXT DEFAULT 'runs',
            result_status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team1_id) REFERENCES teams (team_id),
            FOREIGN KEY (team2_id) REFERENCES teams (team_id),
            FOREIGN KEY (venue_id) REFERENCES venues (venue_id),
            FOREIGN KEY (toss_winner_id) REFERENCES teams (team_id),
            FOREIGN KEY (winner_id) REFERENCES teams (team_id)
        )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert sample data
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample data for demonstration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM teams")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample teams
        teams_data = [
            ("India", "India", "International", 1932, "Wankhede Stadium"),
            ("Australia", "Australia", "International", 1877, "Melbourne Cricket Ground"),
            ("England", "England", "International", 1877, "Lord's Cricket Ground"),
            ("Pakistan", "Pakistan", "International", 1952, "National Stadium"),
            ("South Africa", "South Africa", "International", 1889, "Newlands"),
            ("New Zealand", "New Zealand", "International", 1930, "Eden Park"),
            ("West Indies", "West Indies", "International", 1928, "Kensington Oval"),
            ("Sri Lanka", "Sri Lanka", "International", 1982, "Galle International Stadium")
        ]
        
        cursor.executemany("""
        INSERT INTO teams (team_name, country, team_type, founded_year, home_ground)
        VALUES (?, ?, ?, ?, ?)
        """, teams_data)
        
        # Sample venues
        venues_data = [
            ("Wankhede Stadium", "Mumbai", "India", 33108, 1974),
            ("Melbourne Cricket Ground", "Melbourne", "Australia", 100024, 1853),
            ("Lord's Cricket Ground", "London", "England", 28000, 1814),
            ("Eden Gardens", "Kolkata", "India", 66000, 1864),
            ("The Oval", "London", "England", 25500, 1845),
            ("Sydney Cricket Ground", "Sydney", "Australia", 48000, 1848),
            ("Galle International Stadium", "Galle", "Sri Lanka", 35000, 1998),
            ("Newlands", "Cape Town", "South Africa", 25000, 1888)
        ]
        
        cursor.executemany("""
        INSERT INTO venues (venue_name, city, country, capacity, established_year)
        VALUES (?, ?, ?, ?, ?)
        """, venues_data)
        
        # Sample players
        players_data = [
            ("Virat Kohli", 1, "India", "Batsman", "Right-handed", None, "1988-11-05", "2008-08-18", 254, 12169, 57.32, 93.17, 43, 64, 0, 0.0, 0.0, 121, 0),
            ("Rohit Sharma", 1, "India", "Batsman", "Right-handed", None, "1987-04-30", "2007-06-23", 243, 9205, 46.02, 88.90, 29, 43, 0, 0.0, 0.0, 95, 0),
            ("Steve Smith", 2, "Australia", "Batsman", "Right-handed", "Right-arm leg break", "1989-06-02", "2010-02-25", 128, 7540, 61.80, 57.00, 27, 31, 17, 37.25, 2.93, 112, 0),
            ("Kane Williamson", 6, "New Zealand", "Batsman", "Right-handed", "Right-arm off break", "1990-08-08", "2010-08-11", 87, 6173, 54.31, 51.39, 24, 33, 0, 0.0, 0.0, 90, 0),
            ("Babar Azam", 4, "Pakistan", "Batsman", "Right-handed", None, "1994-10-15", "2015-05-26", 102, 4442, 45.37, 89.34, 17, 26, 0, 0.0, 0.0, 34, 0),
            ("Pat Cummins", 2, "Australia", "Bowler", "Right-handed", "Right-arm fast", "1993-05-08", "2011-11-03", 34, 535, 17.83, 55.96, 0, 1, 164, 23.08, 2.91, 17, 0),
            ("Jasprit Bumrah", 1, "India", "Bowler", "Right-handed", "Right-arm fast", "1993-12-06", "2016-01-23", 30, 59, 8.42, 54.45, 0, 0, 128, 20.06, 2.62, 8, 0),
            ("Ravindra Jadeja", 1, "India", "All-rounder", "Left-handed", "Slow left-arm orthodox", "1988-12-06", "2009-02-08", 67, 2386, 35.26, 57.15, 1, 17, 263, 24.63, 2.39, 57, 0),
            ("Ben Stokes", 3, "England", "All-rounder", "Left-handed", "Right-arm fast-medium", "1991-06-04", "2013-08-05", 79, 4818, 35.89, 58.18, 12, 26, 174, 31.20, 3.16, 95, 0),
            ("MS Dhoni", 1, "India", "Wicket-keeper", "Right-handed", "Right-arm medium", "1981-07-07", "2004-12-23", 350, 10773, 50.57, 87.56, 10, 73, 1, 200.00, 8.25, 256, 38)
        ]
        
        cursor.executemany("""
        INSERT INTO players (player_name, team_id, country, playing_role, batting_style, bowling_style, 
        date_of_birth, debut_date, matches_played, total_runs, batting_average, strike_rate, 
        centuries, half_centuries, total_wickets, bowling_average, economy_rate, catches, stumpings)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, players_data)
        
        # Sample matches
        matches_data = [
            ("India vs Australia 1st Test", "Border-Gavaskar Trophy 2024", "Test", 1, 2, 1, "2024-02-29", "completed", 1, "bat", 1, 31, "runs", "completed"),
            ("India vs England 2nd ODI", "England tour of India 2024", "ODI", 1, 3, 2, "2024-02-02", "completed", 3, "bowl", 1, 100, "runs", "completed"),
            ("Australia vs Pakistan 1st T20I", "Pakistan tour of Australia 2024", "T20I", 2, 4, 3, "2024-01-14", "completed", 2, "bat", 2, 29, "runs", "completed"),
            ("New Zealand vs South Africa Test", "South Africa tour of New Zealand", "Test", 6, 5, 4, "2024-02-04", "completed", 6, "bowl", 6, 4, "wickets", "completed"),
            ("England vs West Indies ODI", "West Indies tour of England", "ODI", 3, 7, 5, "2024-01-28", "completed", 3, "bat", 3, 8, "wickets", "completed")
        ]
        
        cursor.executemany("""
        INSERT INTO matches (match_description, series_name, match_format, team1_id, team2_id, venue_id, 
        match_date, match_status, toss_winner_id, toss_decision, winner_id, victory_margin, victory_type, result_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, matches_data)
        
        conn.commit()
        conn.close()

# Initialize database
@st.cache_resource
def init_db():
    return DatabaseManager()

db = init_db()

# Cricbuzz API Integration
class CricbuzzAPI:
    def __init__(self):
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"
        # Note: Users need to add their own API key from RapidAPI
        self.headers = {
            "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY_HERE",  # Replace with actual key
            "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
        }
    
    def get_live_matches(self) -> List[Dict]:
        """Get live matches from Cricbuzz API"""
        try:
            # For demo purposes, return mock data
            # Replace with actual API call: requests.get(f"{self.base_url}/matches/v1/live", headers=self.headers)
            return [
                {
                    "matchId": "12345",
                    "matchDescription": "India vs Australia 3rd Test",
                    "team1": {"name": "India", "score": "326/7 (87.0)"},
                    "team2": {"name": "Australia", "score": "263 & 104/3 (32.0)"},
                    "status": "Day 3: 2nd innings - In progress",
                    "venue": "Melbourne Cricket Ground"
                },
                {
                    "matchId": "12346",
                    "matchDescription": "England vs New Zealand ODI",
                    "team1": {"name": "England", "score": "285/8 (50.0)"},
                    "team2": {"name": "New Zealand", "score": "198/6 (35.2)"},
                    "status": "2nd innings - In progress",
                    "venue": "Lord's Cricket Ground"
                }
            ]
        except Exception as e:
            st.error(f"Error fetching live matches: {e}")
            return []

# SQL Queries for Analytics
class SQLQueries:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            conn = self.db.get_connection()
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Query execution error: {e}")
            return pd.DataFrame()
    
    # Beginner Level Queries (1-8)
    def query_1_indian_players(self):
        """Find all players who represent India"""
        query = """
        SELECT player_name as 'Full Name', playing_role as 'Playing Role', 
               batting_style as 'Batting Style', bowling_style as 'Bowling Style'
        FROM players 
        WHERE country = 'India'
        ORDER BY player_name
        """
        return self.execute_query(query)
    
    def query_2_recent_matches(self):
        """Show matches played in last 30 days"""
        query = """
        SELECT m.match_description as 'Match Description',
               t1.team_name as 'Team 1', t2.team_name as 'Team 2',
               v.venue_name || ', ' || v.city as 'Venue',
               m.match_date as 'Match Date'
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.match_date >= date('now', '-30 days')
        ORDER BY m.match_date DESC
        """
        return self.execute_query(query)
    
    def query_3_top_run_scorers(self):
        """Top 10 highest run scorers"""
        query = """
        SELECT p.player_name as 'Player Name',
               p.total_runs as 'Total Runs',
               p.batting_average as 'Batting Average',
               p.centuries as 'Centuries'
        FROM players p
        WHERE p.total_runs > 0
        ORDER BY p.total_runs DESC
        LIMIT 10
        """
        return self.execute_query(query)
    
    def query_4_large_venues(self):
        """Venues with capacity > 50,000"""
        query = """
        SELECT venue_name as 'Venue Name', city as 'City', 
               country as 'Country', capacity as 'Capacity'
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC
        """
        return self.execute_query(query)
    
    def query_5_team_wins(self):
        """Count wins per team"""
        query = """
        SELECT t.team_name as 'Team Name', 
               COUNT(*) as 'Total Wins'
        FROM matches m
        JOIN teams t ON m.winner_id = t.team_id
        WHERE m.result_status = 'completed' AND m.winner_id IS NOT NULL
        GROUP BY t.team_name
        ORDER BY COUNT(*) DESC
        """
        return self.execute_query(query)
    
    def query_6_players_by_role(self):
        """Count players by playing role"""
        query = """
        SELECT playing_role as 'Playing Role', 
               COUNT(*) as 'Number of Players'
        FROM players
        GROUP BY playing_role
        ORDER BY COUNT(*) DESC
        """
        return self.execute_query(query)
    
    def query_7_highest_batting_by_cricket(self):
        """Highest individual batting score"""
        query = """
        SELECT player_name as 'Player Name',
                total_runs as 'Total Runs',
                batting_average as 'Batting Average'
        FROM players
        ORDER BY total_runs DESC
        LIMIT 1
        """
        return self.execute_query(query)
    
    def query_8_series_started_2024(self):
        """Cricket series that started in 2024"""
        query = """
        SELECT DISTINCT series_name as 'Series Name'
        country name as 'Country'
        match_type as 'Match Type'
        start_date as 'Start Date'
        FROM matches
        WHERE match_date >= '2024-01-01' AND match_date < '2025-01-01'
        ORDER BY series_name
        """
        return self.execute_query(query)
    
    def query_9_roundall_players(self):
        """All-rounder players with >1000 runs and >50 wickets"""
        query = """
        SELECT player_name as 'Player Name',
               total_runs as 'Total Runs',
               total_wickets as 'Total Wickets'
        FROM players
        WHERE playing_role = 'All-rounder' 
          AND total_runs > 1000 
          AND total_wickets > 50
        ORDER BY total_runs DESC
        """
        return self.execute_query(query)
    
    def query_10_last_20_completed_matches(self):
        """Last 20 completed matches with details"""
        query = """
        SELECT m.match_description as 'Match Description',
               t1.team_name as 'Team 1', t2.team_name as 'Team 2',
               v.venue_name || ', ' || v.city as 'Venue',
               m.match_date as 'Match Date',
               tw.team_name as 'Toss Winner',
               m.toss_decision as 'Toss Decision',
               w.team_name as 'Match Winner',
               m.victory_margin || ' ' || m.victory_type as 'Victory Margin'
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        LEFT JOIN teams tw ON m.toss_winner_id = tw.team_id
        LEFT JOIN teams w ON m.winner_id = w.team_id
        WHERE m.result_status = 'completed'
        ORDER BY m.match_date DESC
        LIMIT 20
        """
        return self.execute_query(query)
    
    def query_11_compare_players_performance(self, player1: str, player2: str):
        """Compare performance of two players"""
        query = """
        SELECT player_name as 'Player Name',
               matches_played as 'Matches Played',
               total_runs as 'Total Runs',
               batting_average as 'Batting Average',
               strike_rate as 'Strike Rate',
               centuries as 'Centuries',
               half_centuries as 'Half Centuries',
               total_wickets as 'Total Wickets',
               bowling_average as 'Bowling Average',
               economy_rate as 'Economy Rate'
        FROM players
        WHERE player_name IN (?, ?)
        """
        return self.execute_query(query, (player1, player2))
    
    def query_12_analyze_international_performace_home_playingaway(self):
        """Analyze international performance at home vs away"""
        query = """
        SELECT p.player_name as 'Player Name',
               SUM(CASE WHEN t.country = p.country THEN p.total_runs ELSE 0 END) as 'Runs at Home',
               SUM(CASE WHEN t.country != p.country THEN p.total_runs ELSE 0 END) as 'Runs Away',
               SUM(CASE WHEN t.country = p.country THEN p.matches_played ELSE 0 END) as 'Matches at Home',
               SUM(CASE WHEN t.country != p.country THEN p.matches_played ELSE 0 END) as 'Matches Away'
        FROM players p
        JOIN teams t ON p.team_id = t.team_id
        GROUP BY p.player_name
        HAVING Runs at Home > 0 AND Runs Away > 0
        ORDER BY p.player_name
        """
        return self.execute_query(query)
    
    def query_13_top_batting_partnership_100_or_moreinnings(self):
        """Top batting partnerships with 100+ runs in an innings"""
        query = """
        SELECT p1.player_name || ' & ' || p2.player_name as 'Partnership',
               COUNT(*) as 'Number of 100+ Partnerships'
        FROM partnerships pa
        JOIN players p1 ON pa.player1_id = p1.player_id
        JOIN players p2 ON pa.player2_id = p2.player_id
        WHERE pa.runs >= 100
        GROUP BY Partnership
        ORDER BY COUNT(*) DESC
        LIMIT 10
        """
        return self.execute_query(query)
    
    def query_14_bowling_performance_at_different_venues_atleast3_matches_bowlers_4overs_ineachmatch(self):
        """Bowling performance at different venues (min 3 matches, 4 overs each)"""
        query = """
        SELECT p.player_name as 'Player Name',
               v.venue_name as 'Venue',
               COUNT(m.match_id) as 'Matches Played',
               SUM(b.wickets) as 'Total Wickets',
               AVG(b.economy_rate) as 'Average Economy Rate'
        FROM bowling_stats b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE b.overs_bowled >= 4
        GROUP BY p.player_name, v.venue_name
        HAVING COUNT(m.match_id) >= 3
        ORDER BY p.player_name, v.venue_name
        """
        return self.execute_query(query)
    
    def query_15_players_perfrom_exceptionally_close_matches(self):
        """Players who performed exceptionally in close matches"""
        query = """
        SELECT p.player_name as 'Player Name',
               COUNT(*) as 'Close Matches Played',
               SUM(CASE WHEN m.victory_margin <= 10 THEN 1 ELSE 0 END) as 'Matches Won by <=10 Runs'
        FROM players p
        JOIN match_performance mp ON p.player_id = mp.player_id
        JOIN matches m ON mp.match_id = m.match_id
        WHERE m.result_status = 'completed'
        GROUP BY p.player_name
        HAVING Close Matches Played > 5 AND Matches Won by <=10 Runs > 0
        ORDER BY Matches Won by <=10 Runs DESC
        """
        return self.execute_query(query)
    
    def query_16_track_players_batting_perfromance_diff_years(self, player_name: str):
        """Track player's batting performance over different years"""
        query = """
        SELECT strftime('%Y', m.match_date) as 'Year',
               SUM(mp.runs_scored) as 'Total Runs',
               AVG(mp.batting_average) as 'Average Batting Average',
               AVG(mp.strike_rate) as 'Average Strike Rate'
        FROM players p
        JOIN match_performance mp ON p.player_id = mp.player_id
        JOIN matches m ON mp.match_id = m.match_id
        WHERE p.player_name = ?
        GROUP BY Year
        ORDER BY Year
        """
        return self.execute_query(query, (player_name,))
    
    def query_17_winning_team_toss_decision_impact(self):
        """Impact of winning the toss and decision on match outcome"""
        query = """
        SELECT m.toss_decision as 'Toss Decision',
               COUNT(*) as 'Total Matches',
               SUM(CASE WHEN m.toss_winner_id = m.winner_id THEN 1 ELSE 0 END) as 'Matches Won After Toss'
        FROM matches m
        WHERE m.result_status = 'completed'
        GROUP BY m.toss_decision
        ORDER BY Total Matches DESC
        """
        return self.execute_query(query)
    
    def query_18_economical_bowlers_limited_over(self):
        """Most economical bowlers in limited overs matches"""
        query = """
        SELECT p.player_name as 'Player Name',
               SUM(b.overs_bowled) as 'Total Overs',
               SUM(b.runs_conceded) as 'Total Runs Conceded',
               (SUM(b.runs_conceded) / SUM(b.overs_bowled)) as 'Economy Rate'
        FROM bowling_stats b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        WHERE m.match_format IN ('ODI', 'T20I')
        GROUP BY p.player_name
        HAVING SUM(b.overs_bowled) >= 20
        ORDER BY Economy Rate ASC
        LIMIT 10
        """
        return self.execute_query(query)
    
    def query_19_batsmen_consistent_scoring(self):
        """Batsmen with consistent scoring (50+ in at least 5 consecutive matches)"""
        query = """
        SELECT p.player_name as 'Player Name',
               COUNT(*) as 'Consecutive 50+ Scores'
        FROM (
            SELECT player_id, match_id,
                   SUM(CASE WHEN runs_scored >= 50 THEN 1 ELSE 0 END) as fifty_plus
            FROM match_performance
            GROUP BY player_id, match_id
            ORDER BY player_id, match_id
        ) AS sub
        JOIN players p ON sub.player_id = p.player_id
        WHERE sub.fifty_plus = 1
        GROUP BY p.player_name
        HAVING COUNT(*) >= 5
        ORDER BY COUNT(*) DESC
        """
        return self.execute_query(query)
    
    def query_20_player_played_match_different_formats(self):
        """Players who have played matches in different formats"""
        query = """
        SELECT p.player_name as 'Player Name',
               COUNT(DISTINCT m.match_format) as 'Formats Played'
        FROM players p
        JOIN match_performance mp ON p.player_id = mp.player_id
        JOIN matches m ON mp.match_id = m.match_id
        GROUP BY p.player_name
        HAVING Formats Played > 1
        ORDER BY Formats Played DESC
        """
        return self.execute_query(query)
    
    def query_21_performance_ranking_sytem_players_batting_bowling(self):
        """Performance ranking system for players"""
        query = """
        SELECT p.player_name as 'Player Name',
               ( (p.total_runs * 0.01) + (p.batting_average * 0.5) + (p.strike_rate * 0.3) ) as 'Batting Score',
               ( (p.total_wickets * 0.02) + (p.bowling_average * 0.4) + (p.economy_rate * 0.4) ) as 'Bowling Score',
               ( ((p.total_runs * 0.01) + (p.batting_average * 0.5) + (p.strike_rate * 0.3)) +
                 ((p.total_wickets * 0.02) + (p.bowling_average * 0.4) + (p.economy_rate * 0.4)) ) as 'Overall Score'
        FROM players p
        ORDER BY Overall Score DESC
        LIMIT 20
        """
        return self.execute_query(query)
    
    def query_22_played_atleast_5matches_against_each_other_3years(self):
        """Players who have played at least 5 matches against each other in last 3 years"""
        query = """
        SELECT p1.player_name || ' & ' || p2.player_name as 'Player Pair',
               COUNT(*) as 'Matches Played Together'
        FROM match_performance mp1
        JOIN match_performance mp2 ON mp1.match_id = mp2.match_id AND mp1.player_id != mp2.player_id
        JOIN players p1 ON mp1.player_id = p1.player_id
        JOIN players p2 ON mp2.player_id = p2.player_id
        JOIN matches m ON mp1.match_id = m.match_id
        WHERE m.match_date >= date('now', '-3 years')
        GROUP BY Player Pair
        HAVING COUNT(*) >= 5
        ORDER BY COUNT(*) DESC
        """
        return self.execute_query(query)


# CRUD Operations
class CRUDOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_player(self, player_data):
        """Add new player to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO players (player_name, team_id, country, playing_role, batting_style, 
                           bowling_style, date_of_birth, matches_played, total_runs, batting_average)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, player_data)
        conn.commit()
        conn.close()
    
    def update_player(self, player_id, player_data):
        """Update existing player"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE players 
        SET player_name=?, country=?, playing_role=?, batting_style=?, 
            bowling_style=?, matches_played=?, total_runs=?, batting_average=?
        WHERE player_id=?
        """
        
        cursor.execute(query, (*player_data, player_id))
        conn.commit()
        conn.close()
    
    def delete_player(self, player_id):
        """Delete player from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM players WHERE player_id=?", (player_id,))
        conn.commit()
        conn.close()
    
    def get_all_players(self):
        """Get all players"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM players ORDER BY player_name", conn)
        conn.close()
        return df

# # Page Functions
# def home_page():
#     """Home page with project overview"""
#     st.markdown("""
#     <div class="main-header">
#         <h1>🏏 Cricbuzz LiveStats Dashboard</h1>
#         <h3>Comprehensive Cricket Analytics Platform</h3>
#     </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.markdown("""
#         ### 📊 Features
#         - **Live Match Updates** - Real-time scores from Cricbuzz API
#         - **Player Statistics** - Comprehensive batting & bowling stats  
#         - **SQL Analytics** - 25+ advanced analytical queries
#         - **CRUD Operations** - Complete database management
#         """)
    
#     with col2:
#         st.markdown("""
#         ### 🛠️ Tech Stack
#         - **Frontend:** Streamlit
#         - **Backend:** Python, SQLite
#         - **API:** Cricbuzz Cricket API
#         - **Analytics:** Pandas, Plotly
#         - **Database:** SQLite with advanced SQL
#         """)
    
#     with col3:
#         st.markdown("""
#         ### 🎯 Use Cases
#         - **Sports Media** - Commentary & analysis
#         - **Fantasy Cricket** - Player selection insights
#         - **Analytics Firms** - Performance modeling
#         - **Education** - SQL learning with real data
#         """)
    
#     st.markdown("---")
    
#     # Project Statistics
#     col1, col2, col3, col4 = st.columns(4)
    
#     # Get database stats
#     conn = db.get_connection()
    
#     with col1:
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) FROM players")
#         player_count = cursor.fetchone()[0]
#         st.metric("Total Players", player_count)
    
#     with col2:
#         cursor.execute("SELECT COUNT(*) FROM teams")
#         team_count = cursor.fetchone()[0]
#         st.metric("Teams", team_count)
    
#     with col3:
#         cursor.execute("SELECT COUNT(*) FROM matches")
#         match_count = cursor.fetchone()[0]
#         st.metric("Matches", match_count)
    
#     with col4:
#         cursor.execute("SELECT COUNT(*) FROM venues")
#         venue_count = cursor.fetchone()[0]
#         st.metric("Venues", venue_count)
    
#     conn.close()
    
#     st.markdown("""
#     ### 📖 Getting Started
    
#     1. **Live Matches** - View real-time cricket scores and updates
#     2. **Player Stats** - Explore comprehensive player statistics  
#     3. **SQL Analytics** - Run advanced queries on cricket data
#     4. **CRUD Operations** - Manage players and match data
    
#     Navigate using the sidebar to explore different sections of the dashboard.
    
#     ### 🔧 Setup Instructions for API
    
#     To enable live API features:
#     1. Go to [RapidAPI Cricbuzz](https://rapidapi.com/cricketapi/api/cricbuzz-cricket/)
#     2. Subscribe to get your API key (free tier available)
#     3. Replace `YOUR_RAPIDAPI_KEY_HERE` in the code with your actual key
#     4. Restart the application
    
#     **Database is automatically created as SQLite file - no external setup needed!**
#     """)

def live_matches_page():
    """Live matches page"""
    st.title("🔴 Live Scores")
    
    # API key check
    st.info("⚠️ To view real live matches, please configure your RapidAPI key. Currently showing demo data.")
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Live Scores", type="primary"):
        st.rerun()
    
    # Get live matches
    api = CricbuzzAPI()
    live_matches = api.get_live_matches()
    
    if live_matches:
        for i, match in enumerate(live_matches):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {match['matchDescription']}")
                    
                    # Team scores
                    col_team1, col_vs, col_team2 = st.columns([2, 1, 2])
                    
                    with col_team1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{match['team1']['name']}</h4>
                            <h3>{match['team1']['score']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_vs:
                        st.markdown("<div style='text-align: center; padding: 2rem;'><h2>VS</h2></div>", unsafe_allow_html=True)
                    
                    with col_team2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{match['team2']['name']}</h4>
                            <h3>{match['team2']['score']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Status:** {match['status']}")
                    st.markdown(f"**Venue:** {match['venue']}")
                
                with col2:
                    st.markdown("### Quick Stats")
                    if st.button(f"View Details", key=f"details_{i}"):
                        st.info("Detailed scorecard would be displayed here with full API integration.")
                
                st.markdown("---")

def player_stats_page():
    """Player statistics page"""
    st.title("⭐ Player Statistics")
    
    # Player filter
    conn = db.get_connection()
    players_df = pd.read_sql_query("SELECT player_name, country, playing_role FROM players", conn)
    conn.close()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_country = st.selectbox("Filter by Country", 
                                      ['All'] + list(players_df['country'].unique()))
    
    with col2:
        selected_role = st.selectbox("Filter by Role", 
                                   ['All'] + list(players_df['playing_role'].unique()))
    
    # Apply filters
    filtered_df = players_df.copy()
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['playing_role'] == selected_role]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Top performers charts
    st.markdown("### 📊 Top Performers")
    
    # Get top run scorers
    query = SQLQueries(db)
    top_scorers = query.query_3_top_run_scorers()
    
    if not top_scorers.empty:
        fig = px.bar(top_scorers, x='Player Name', y='Total Runs', 
                    title='Top Run Scorers')
        st.plotly_chart(fig, use_container_width=True)

def sql_analytics_page():
    """SQL Analytics page"""
    st.title("🔍 SQL Analytics & Queries")
    
    query_executor = SQLQueries(db)
    
    # Query categories
    tab1, tab2, tab3 = st.tabs(["📚 Beginner Queries", "🎯 Intermediate Queries", "🚀 Advanced Queries"])
    
    with tab1:
        st.markdown("### Beginner Level Queries")
        
        queries = {
            "Q1: All Indian Players": query_executor.query_1_indian_players,
            "Q2: Recent Matches (Last 30 Days)": query_executor.query_2_recent_matches,
            "Q3: Top 10 Run Scorers": query_executor.query_3_top_run_scorers,
            "Q4: Large Venues (50k+ capacity)": query_executor.query_4_large_venues,
            "Q5: Team Wins Count": query_executor.query_5_team_wins,
            "Q6: Players by Role": query_executor.query_6_players_by_role,
            "Q7: Highest Individual Batting Score": query_executor.query_7_highest_batting_by_cricket,
            "Q8: Series Started in 2024": query_executor.query_8_series_started_2024,
            "Q9: All-rounders with >1000 runs & >50 wickets": query_executor.query_9_roundall_players,
            "Q10: Last 20 Completed Matches": query_executor.query_10_last_20_completed_matches,
            "Q11: Compare Two Players' Performance": lambda: query_executor.query_11_compare_players_performance(
                st.text_input("Player 1 Name", "Virat Kohli"), 
                st.text_input("Player 2 Name", "Steve Smith")
            ),
            "Q12: International Performance Home vs Away": query_executor.query_12_analyze_international_performace_home_playingaway,
            "Q13: Top Batting Partnerships (100+ runs)": query_executor.query_13_top_batting_partnership_100_or_moreinnings,
            "Q14: Bowling Performance at Different Venues": query_executor.query_14_bowling_performance_at_different_venues_atleast3_matches_bowlers_4overs_ineachmatch,
            "Q15: Players Performing Exceptionally in Close Matches": query_executor.query_15_players_perfrom_exceptionally_close_matches,
            "Q16: Track Player's Batting Performance Over Years": lambda: query_executor.query_16_track_players_batting_perfromance_diff_years(
                st.text_input("Player Name", "Virat Kohli")
            ),
            "Q17: Impact of Winning Toss Decision": query_executor.query_17_winning_team_toss_decision_impact,
            "Q18: Most Economical Bowlers in Limited Overs": query_executor.query_18_economical_bowlers_limited_over,
            "Q19: Batsmen with Consistent Scoring (50+ in 5 consecutive matches)": query_executor.query_19_batsmen_consistent_scoring,
            "Q20: Players in Different Formats": query_executor.query_20_player_played_match_different_formats,
            "Q21: Performance Ranking System for Players": query_executor.query_21_performance_ranking_sytem_players_batting_bowling,
            "Q22: Players Played at least 5 Matches Against Each Other in Last 3 Years": query_executor.query_22_played_atleast_5matches_against_each_other_3years
        }
        
        selected_query = st.selectbox("Select Query", list(queries.keys()))
        
        if st.button("Execute Query", type="primary"):
            with st.spinner("Executing query..."):
                result = queries[selected_query]()
                if not result.empty:
                    st.dataframe(result, use_container_width=True)
                    st.success(f"Query executed successfully! Found {len(result)} records.")
                else:
                    st.warning("No data found for this query.")
    
    with tab2:
        st.markdown("### Intermediate Level Queries")
        st.info("Additional intermediate queries would be implemented here with JOIN operations and subqueries.")
        
        # Custom SQL Query box
        st.markdown("#### Custom SQL Query")
        custom_query = st.text_area("Enter your SQL query:", height=100,
                                  value="SELECT * FROM players LIMIT 5;")
        
        if st.button("Run Custom Query"):
            try:
                result = query_executor.execute_query(custom_query)
                if not result.empty:
                    st.dataframe(result, use_container_width=True)
                else:
                    st.info("Query executed successfully but returned no results.")
            except Exception as e:
                st.error(f"Query error: {e}")
    
    with tab3:
        st.markdown("### Advanced Level Queries")
        st.info("Advanced analytics with window functions, CTEs, and complex calculations would be implemented here.")

def crud_operations_page():
    """CRUD Operations page"""
    st.title("🛠️ Database Management (CRUD Operations)")
    
    crud = CRUDOperations(db)
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Player", "📖 View Players", "✏️ Update Player", "🗑️ Delete Player"])
    
    with tab1:
        st.markdown("### Add New Player")
        
        with st.form("add_player_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Player Name*")
                country = st.text_input("Country*")
                role = st.selectbox("Playing Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
                batting_style = st.text_input("Batting Style")
            
            with col2:
                bowling_style = st.text_input("Bowling Style")
                dob = st.date_input("Date of Birth")
                matches = st.number_input("Matches Played", min_value=0, value=0)
                total_runs = st.number_input("Total Runs", min_value=0, value=0)
                avg = st.number_input("Batting Average", min_value=0.0, value=0.0, format="%.2f")
            
            # Get team ID
            conn = db.get_connection()
            teams_df = pd.read_sql_query("SELECT team_id, team_name FROM teams", conn)
            conn.close()
            
            team_name = st.selectbox("Team", teams_df['team_name'].tolist())
            team_id = teams_df[teams_df['team_name'] == team_name]['team_id'].iloc[0]
            
            submitted = st.form_submit_button("Add Player", type="primary")
            
            if submitted:
                if name and country:
                    try:
                        player_data = (name, team_id, country, role, batting_style, 
                                     bowling_style, dob, matches, total_runs, avg)
                        crud.add_player(player_data)
                        st.success("✅ Player added successfully!")
                    except Exception as e:
                        st.error(f"Error adding player: {e}")
                else:
                    st.error("Please fill in required fields (Name and Country)")
    
    with tab2:
        st.markdown("### View All Players")
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        players_df = crud.get_all_players()
        
        if not players_df.empty:
            # Search functionality
            search_term = st.text_input("🔍 Search players by name:")
            if search_term:
                players_df = players_df[players_df['player_name'].str.contains(search_term, case=False, na=False)]
            
            st.dataframe(players_df, use_container_width=True)
            st.info(f"Total players: {len(players_df)}")
        else:
            st.warning("No players found in the database.")
    
    with tab3:
        st.markdown("### Update Player Information")
        
        # Select player to update
        players_df = crud.get_all_players()
        
        if not players_df.empty:
            player_names = players_df['player_name'].tolist()
            selected_player = st.selectbox("Select Player to Update", player_names)
            
            if selected_player:
                player_data = players_df[players_df['player_name'] == selected_player].iloc[0]
                
                with st.form("update_player_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Player Name", value=player_data['player_name'])
                        country = st.text_input("Country", value=player_data['country'])
                        role = st.selectbox("Playing Role", 
                                          ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"],
                                          index=["Batsman", "Bowler", "All-rounder", "Wicket-keeper"].index(player_data['playing_role']))
                        batting_style = st.text_input("Batting Style", value=player_data['batting_style'] or "")
                    
                    with col2:
                        bowling_style = st.text_input("Bowling Style", value=player_data['bowling_style'] or "")
                        matches = st.number_input("Matches Played", min_value=0, value=int(player_data['matches_played']))
                        total_runs = st.number_input("Total Runs", min_value=0, value=int(player_data['total_runs']))
                        avg = st.number_input("Batting Average", min_value=0.0, value=float(player_data['batting_average']), format="%.2f")
                    
                    submitted = st.form_submit_button("Update Player", type="primary")
                    
                    if submitted:
                        try:
                            update_data = (name, country, role, batting_style, bowling_style, 
                                         matches, total_runs, avg)
                            crud.update_player(player_data['player_id'], update_data)
                            st.success("✅ Player updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating player: {e}")
        else:
            st.warning("No players available to update.")
    
    with tab4:
        st.markdown("### Delete Player")
        st.warning("⚠️ This action cannot be undone!")
        
        players_df = crud.get_all_players()
        
        if not players_df.empty:
            player_names = players_df['player_name'].tolist()
            selected_player = st.selectbox("Select Player to Delete", [""] + player_names)
            
            if selected_player:
                player_data = players_df[players_df['player_name'] == selected_player].iloc[0]
                
                st.info(f"""
                **Player Details:**
                - Name: {player_data['player_name']}
                - Country: {player_data['country']}
                - Role: {player_data['playing_role']}
                - Matches: {player_data['matches_played']}
                - Runs: {player_data['total_runs']}
                """)
                
                if st.button("🗑️ Delete Player", type="secondary"):
                    if st.button("⚠️ Confirm Deletion", type="secondary"):
                        try:
                            crud.delete_player(player_data['player_id'])
                            st.success("✅ Player deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting player: {e}")
        else:
            st.warning("No players available to delete.")

# Main Application
def main():
    """Main application function"""
    
    # Sidebar navigation
    st.sidebar.title("🏏 Cricket Dashboard")
    
    pages = {
        "🔴 Live Matches": live_matches_page,
        "⭐ Player Statistics": player_stats_page,
        "🔍 SQL Analytics": sql_analytics_page,
        "🛠️ CRUD Operations": crud_operations_page
    }
    
    selected_page = st.sidebar.selectbox("Choose Page:", list(pages.keys()))
    
    pages[selected_page]()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏏 Cricket Analytics Dashboard | Built with Streamlit & SQLite | 
        <a href='https://rapidapi.com/cricketapi/api/cricbuzz-cricket/' target='_blank'>Get API Key</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()