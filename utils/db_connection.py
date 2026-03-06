# DATABASE CONNECTION & SCHEMA SETUP
import sqlite3
import os
import pandas as pd
from datetime import datetime, date
import json

# ── Load environment variables (fallback to SQLite if no .env) ──────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_TYPE    = os.getenv("DB_TYPE", "sqlite")
SQLITE_PATH = os.getenv("SQLITE_PATH", "cricbuzz.db")


# ════════════════════════════════════════════════════════════════════════════
# 1.  CONNECTION HELPERS
# ════════════════════════════════════════════════════════════════════════════

def get_connection():
    """
    Return a raw DB-API connection object.
    Supports sqlite | postgresql | mysql based on DB_TYPE env var.
    """
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row          # access columns by name
        conn.execute("PRAGMA journal_mode=WAL") # better concurrency
        return conn

    elif DB_TYPE == "postgresql":
        import psycopg2
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("DB_NAME", "cricbuzz_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )

    elif DB_TYPE == "mysql":
        import pymysql
        return pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            db=os.getenv("DB_NAME", "cricbuzz_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")


def run_query(sql: str, params=()) -> pd.DataFrame:
    """
    Execute a SELECT query and return results as a Pandas DataFrame.
    Always closes the connection afterwards.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    except Exception as e:
        print(f"[run_query ERROR] {e}\nSQL: {sql}")
        return pd.DataFrame()
    finally:
        conn.close()


def execute_dml(sql: str, params=()) -> bool:
    """
    Execute INSERT / UPDATE / DELETE statements.
    Returns True on success, False on failure.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[execute_dml ERROR] {e}\nSQL: {sql}")
        return False
    finally:
        conn.close()


def execute_many(sql: str, data: list) -> bool:
    """Bulk-insert a list of tuples."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.executemany(sql, data)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[execute_many ERROR] {e}")
        return False
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# 2.  SCHEMA CREATION  (CREATE TABLE IF NOT EXISTS)
# ════════════════════════════════════════════════════════════════════════════

CREATE_TABLES_SQL = """

-- ── Teams ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    team_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name   TEXT NOT NULL UNIQUE,
    short_name  TEXT,
    country     TEXT,
    team_type   TEXT DEFAULT 'International',  -- International / Domestic / Franchise
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Venues ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS venues (
    venue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name  TEXT NOT NULL,
    city        TEXT,
    country     TEXT,
    capacity    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Players ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS players (
    player_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    country         TEXT,
    date_of_birth   TEXT,
    batting_style   TEXT,   -- Right-hand bat / Left-hand bat
    bowling_style   TEXT,   -- Right-arm fast / Left-arm spin / etc.
    playing_role    TEXT,   -- Batsman / Bowler / All-rounder / WK-Batsman
    team_id         INTEGER REFERENCES teams(team_id),
    jersey_number   INTEGER,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Series / Tournaments ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS series (
    series_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name     TEXT NOT NULL,
    host_country    TEXT,
    match_type      TEXT,   -- Test / ODI / T20I / IPL / etc.
    start_date      TEXT,
    end_date        TEXT,
    total_matches   INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Matches ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matches (
    match_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id           INTEGER REFERENCES series(series_id),
    match_description   TEXT,
    team1_id            INTEGER REFERENCES teams(team_id),
    team2_id            INTEGER REFERENCES teams(team_id),
    venue_id            INTEGER REFERENCES venues(venue_id),
    match_date          TEXT,
    match_format        TEXT,   -- Test / ODI / T20I
    status              TEXT,   -- Live / Completed / Upcoming
    toss_winner_id      INTEGER REFERENCES teams(team_id),
    toss_decision       TEXT,   -- bat / bowl
    winning_team_id     INTEGER REFERENCES teams(team_id),
    victory_margin      TEXT,
    victory_type        TEXT,   -- runs / wickets
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Batting Stats (per innings) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batting_stats (
    stat_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER REFERENCES matches(match_id),
    player_id       INTEGER REFERENCES players(player_id),
    innings_number  INTEGER DEFAULT 1,
    runs_scored     INTEGER DEFAULT 0,
    balls_faced     INTEGER DEFAULT 0,
    fours           INTEGER DEFAULT 0,
    sixes           INTEGER DEFAULT 0,
    strike_rate     REAL DEFAULT 0.0,
    dismissal_type  TEXT,
    batting_position INTEGER,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Bowling Stats (per innings) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bowling_stats (
    stat_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER REFERENCES matches(match_id),
    player_id       INTEGER REFERENCES players(player_id),
    innings_number  INTEGER DEFAULT 1,
    overs_bowled    REAL DEFAULT 0.0,
    runs_conceded   INTEGER DEFAULT 0,
    wickets_taken   INTEGER DEFAULT 0,
    economy_rate    REAL DEFAULT 0.0,
    maidens         INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Fielding Stats (per match) ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fielding_stats (
    stat_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id    INTEGER REFERENCES matches(match_id),
    player_id   INTEGER REFERENCES players(player_id),
    catches     INTEGER DEFAULT 0,
    stumpings   INTEGER DEFAULT 0,
    run_outs    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Career Summary (aggregated) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS player_career_stats (
    career_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id           INTEGER REFERENCES players(player_id),
    format              TEXT,   -- Test / ODI / T20I
    matches_played      INTEGER DEFAULT 0,
    innings_batted      INTEGER DEFAULT 0,
    total_runs          INTEGER DEFAULT 0,
    highest_score       INTEGER DEFAULT 0,
    batting_average     REAL DEFAULT 0.0,
    batting_strike_rate REAL DEFAULT 0.0,
    centuries           INTEGER DEFAULT 0,
    half_centuries      INTEGER DEFAULT 0,
    total_wickets       INTEGER DEFAULT 0,
    bowling_average     REAL DEFAULT 0.0,
    economy_rate        REAL DEFAULT 0.0,
    five_wicket_hauls   INTEGER DEFAULT 0,
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def create_tables():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        # SQLite supports multiple statements via executescript
        if DB_TYPE == "sqlite":
            conn.executescript(CREATE_TABLES_SQL)
        else:
            for stmt in CREATE_TABLES_SQL.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cur.execute(stmt)
        conn.commit()
        print("✅ All tables created successfully.")
    except Exception as e:
        print(f"[create_tables ERROR] {e}")
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# 3.  SAMPLE DATA SEEDER
# ════════════════════════════════════════════════════════════════════════════

def seed_sample_data():
    """
    Insert realistic sample data so the dashboard works
    even without a live API key.
    Run once — skips if data already exists.
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ── Guard: skip if data already present ──────────────────────────────
    cur.execute("SELECT COUNT(*) FROM players")
    row = cur.fetchone()
    count = row[0] if isinstance(row, (tuple, list)) else row["COUNT(*)"]
    if count > 0:
        conn.close()
        print("ℹ️  Sample data already present — skipping seed.")
        return

    print("🌱 Seeding sample data …")

    # ── Teams ─────────────────────────────────────────────────────────────
    teams = [
        ("India",        "IND", "India",       "International"),
        ("Australia",    "AUS", "Australia",   "International"),
        ("England",      "ENG", "England",     "International"),
        ("Pakistan",     "PAK", "Pakistan",    "International"),
        ("South Africa", "SA",  "South Africa","International"),
        ("New Zealand",  "NZ",  "New Zealand", "International"),
        ("West Indies",  "WI",  "West Indies", "International"),
        ("Sri Lanka",    "SL",  "Sri Lanka",   "International"),
        ("Bangladesh",   "BAN", "Bangladesh",  "International"),
        ("Afghanistan",  "AFG", "Afghanistan", "International"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO teams (team_name, short_name, country, team_type) VALUES (?,?,?,?)",
        teams
    )

    # ── Venues ────────────────────────────────────────────────────────────
    venues = [
        ("Narendra Modi Stadium",    "Ahmedabad",      "India",        132000),
        ("Melbourne Cricket Ground", "Melbourne",      "Australia",    100024),
        ("Eden Gardens",             "Kolkata",        "India",        66000),
        ("Lord's Cricket Ground",    "London",         "England",      30000),
        ("Wankhede Stadium",         "Mumbai",         "India",        33108),
        ("The Oval",                 "London",         "England",      25500),
        ("Headingley",               "Leeds",          "England",      18350),
        ("Sydney Cricket Ground",    "Sydney",         "Australia",    48000),
        ("Gaddafi Stadium",          "Lahore",         "Pakistan",     27000),
        ("SuperSport Park",          "Centurion",      "South Africa", 22000),
        ("MA Chidambaram Stadium",   "Chennai",        "India",        50000),
        ("Rajiv Gandhi Intl Stadium","Hyderabad",      "India",        55000),
        ("National Stadium",         "Karachi",        "Pakistan",     34228),
        ("Basin Reserve",            "Wellington",     "New Zealand",  11600),
        ("Kensington Oval",          "Bridgetown",     "West Indies",  28000),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO venues (venue_name, city, country, capacity) VALUES (?,?,?,?)",
        venues
    )

    # ── Fetch IDs ─────────────────────────────────────────────────────────
    cur.execute("SELECT team_id, team_name FROM teams")
    team_map = {r[1]: r[0] for r in cur.fetchall()}

    cur.execute("SELECT venue_id, venue_name FROM venues")
    venue_map = {r[1]: r[0] for r in cur.fetchall()}

    # ── Players ───────────────────────────────────────────────────────────
    players = [
        # India
        ("Virat Kohli",      "India", "1988-11-05", "Right-hand bat", "Right-arm medium",       "Batsman",      team_map["India"],        18),
        ("Rohit Sharma",     "India", "1987-04-30", "Right-hand bat", "Right-arm off-break",    "Batsman",      team_map["India"],        45),
        ("Jasprit Bumrah",   "India", "1993-12-06", "Right-hand bat", "Right-arm fast",         "Bowler",       team_map["India"],        93),
        ("Ravindra Jadeja",  "India", "1988-12-06", "Left-hand bat",  "Left-arm orthodox spin", "All-rounder",  team_map["India"],         8),
        ("MS Dhoni",         "India", "1981-07-07", "Right-hand bat", "Right-arm medium",       "WK-Batsman",   team_map["India"],         7),
        ("Hardik Pandya",    "India", "1993-10-11", "Right-hand bat", "Right-arm fast-medium",  "All-rounder",  team_map["India"],        33),
        ("Shubman Gill",     "India", "2000-09-08", "Right-hand bat", "Right-arm off-break",    "Batsman",      team_map["India"],        77),
        ("Mohammed Shami",   "India", "1990-09-03", "Right-hand bat", "Right-arm fast",         "Bowler",       team_map["India"],        11),
        # Australia
        ("Steve Smith",      "Australia", "1989-06-02", "Right-hand bat", "Right-arm leg-break",    "Batsman",      team_map["Australia"],    49),
        ("Pat Cummins",      "Australia", "1993-05-08", "Right-hand bat", "Right-arm fast",         "Bowler",       team_map["Australia"],    30),
        ("David Warner",     "Australia", "1986-10-27", "Left-hand bat",  "Right-arm off-break",    "Batsman",      team_map["Australia"],     2),
        ("Mitchell Starc",   "Australia", "1990-01-30", "Left-hand bat",  "Left-arm fast",          "Bowler",       team_map["Australia"],    56),
        ("Glenn Maxwell",    "Australia", "1988-10-14", "Right-hand bat", "Right-arm off-break",    "All-rounder",  team_map["Australia"],    32),
        # England
        ("Joe Root",         "England", "1990-12-30", "Right-hand bat", "Right-arm off-break",    "Batsman",      team_map["England"],       66),
        ("Ben Stokes",       "England", "1991-06-04", "Left-hand bat",  "Right-arm fast-medium",  "All-rounder",  team_map["England"],       55),
        ("James Anderson",   "England", "1982-07-30", "Right-hand bat", "Right-arm fast-medium",  "Bowler",       team_map["England"],        9),
        ("Jos Buttler",      "England", "1990-09-08", "Right-hand bat", "Right-arm medium",       "WK-Batsman",   team_map["England"],        6),
        # Pakistan
        ("Babar Azam",       "Pakistan", "1994-10-15", "Right-hand bat", "Right-arm off-break",   "Batsman",      team_map["Pakistan"],      56),
        ("Shaheen Afridi",   "Pakistan", "2000-04-06", "Left-hand bat",  "Left-arm fast",         "Bowler",       team_map["Pakistan"],      10),
        ("Shadab Khan",      "Pakistan", "1998-10-04", "Right-hand bat", "Right-arm leg-break",   "All-rounder",  team_map["Pakistan"],      16),
        # South Africa
        ("Quinton de Kock",  "South Africa", "1993-01-17", "Left-hand bat",  "Right-arm medium",      "WK-Batsman",   team_map["South Africa"], 18),
        ("Kagiso Rabada",    "South Africa", "1995-05-25", "Right-hand bat", "Right-arm fast",        "Bowler",       team_map["South Africa"], 25),
        # New Zealand
        ("Kane Williamson",  "New Zealand",  "1990-08-08", "Right-hand bat", "Right-arm off-break",  "Batsman",      team_map["New Zealand"],  22),
        ("Trent Boult",      "New Zealand",  "1989-07-22", "Right-hand bat", "Left-arm fast-medium", "Bowler",       team_map["New Zealand"],  22),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO players
           (full_name, country, date_of_birth, batting_style, bowling_style, playing_role, team_id, jersey_number)
           VALUES (?,?,?,?,?,?,?,?)""",
        players
    )

    # ── Series ────────────────────────────────────────────────────────────
    series_data = [
        ("ICC Cricket World Cup 2023",    "India",     "ODI",  "2023-10-05", "2023-11-19", 48),
        ("ICC World Test Championship",   "Multiple",  "Test", "2023-06-07", "2025-06-11", 22),
        ("India vs Australia Test 2024",  "Australia", "Test", "2024-11-22", "2025-01-07",  5),
        ("IPL 2024",                      "India",     "T20",  "2024-03-22", "2024-05-26", 74),
        ("T20 World Cup 2024",            "USA/WI",    "T20I", "2024-06-01", "2024-06-29", 55),
        ("Ashes 2023",                    "England",   "Test", "2023-06-16", "2023-07-31",  5),
        ("India vs England ODI 2024",     "India",     "ODI",  "2024-02-06", "2024-02-11",  3),
        ("SA20 2024",                     "South Africa","T20","2024-01-10", "2024-02-10", 33),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO series (series_name, host_country, match_type, start_date, end_date, total_matches) VALUES (?,?,?,?,?,?)",
        series_data
    )

    cur.execute("SELECT series_id, series_name FROM series")
    series_map = {r[1]: r[0] for r in cur.fetchall()}

    # ── Matches ───────────────────────────────────────────────────────────
    matches_data = [
        (series_map["ICC Cricket World Cup 2023"], "IND vs AUS - Final",      team_map["India"],       team_map["Australia"],   venue_map["Narendra Modi Stadium"],    "2023-11-19","ODI",  "Completed", team_map["India"],       "bat",  team_map["Australia"],   "6 wickets", "wickets"),
        (series_map["ICC Cricket World Cup 2023"], "IND vs PAK - Group Stage", team_map["India"],       team_map["Pakistan"],    venue_map["Narendra Modi Stadium"],    "2023-10-14","ODI",  "Completed", team_map["India"],       "bat",  team_map["India"],       "7 wickets", "wickets"),
        (series_map["ICC Cricket World Cup 2023"], "AUS vs ENG - Group Stage", team_map["Australia"],   team_map["England"],     venue_map["Narendra Modi Stadium"],    "2023-11-04","ODI",  "Completed", team_map["Australia"],   "bat",  team_map["Australia"],   "33 runs",   "runs"),
        (series_map["Ashes 2023"],                 "ENG vs AUS - 1st Test",    team_map["England"],     team_map["Australia"],   venue_map["Headingley"],               "2023-06-16","Test", "Completed", team_map["England"],     "bat",  team_map["England"],     "2 wickets", "wickets"),
        (series_map["Ashes 2023"],                 "ENG vs AUS - 2nd Test",    team_map["England"],     team_map["Australia"],   venue_map["Lord's Cricket Ground"],    "2023-06-28","Test", "Completed", team_map["Australia"],   "bowl", team_map["Australia"],   "43 runs",   "runs"),
        (series_map["India vs Australia Test 2024"],"IND vs AUS - 1st Test",   team_map["India"],       team_map["Australia"],   venue_map["MA Chidambaram Stadium"],   "2024-11-22","Test", "Completed", team_map["Australia"],   "bat",  team_map["India"],       "295 runs",  "runs"),
        (series_map["India vs Australia Test 2024"],"IND vs AUS - 2nd Test",   team_map["India"],       team_map["Australia"],   venue_map["Rajiv Gandhi Intl Stadium"],"2024-12-06","Test", "Completed", team_map["India"],       "bowl", team_map["Australia"],   "10 wickets","wickets"),
        (series_map["T20 World Cup 2024"],         "IND vs SA - Final",        team_map["India"],       team_map["South Africa"],venue_map["Kensington Oval"],          "2024-06-29","T20I", "Completed", team_map["India"],       "bat",  team_map["India"],       "7 runs",    "runs"),
        (series_map["India vs England ODI 2024"],  "IND vs ENG - 1st ODI",     team_map["India"],       team_map["England"],     venue_map["Narendra Modi Stadium"],    "2024-02-06","ODI",  "Completed", team_map["India"],       "bat",  team_map["India"],       "5 wickets", "wickets"),
        (series_map["India vs England ODI 2024"],  "IND vs ENG - 2nd ODI",     team_map["India"],       team_map["England"],     venue_map["MA Chidambaram Stadium"],   "2024-02-09","ODI",  "Completed", team_map["England"],     "bowl", team_map["England"],     "100 runs",  "runs"),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO matches
           (series_id, match_description, team1_id, team2_id, venue_id,
            match_date, match_format, status, toss_winner_id, toss_decision,
            winning_team_id, victory_margin, victory_type)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        matches_data
    )

    # ── Career Stats ──────────────────────────────────────────────────────
    cur.execute("SELECT player_id, full_name FROM players")
    player_map = {r[1]: r[0] for r in cur.fetchall()}

    career_stats = [
        # (player_id, format, matches, inn, runs, hs, avg,  sr,    100s, 50s, wkts, bowl_avg, eco, 5w)
        (player_map["Virat Kohli"],     "ODI",  295, 285, 13906, 183, 58.18, 93.25, 50, 72,  4, 166.0, 5.50, 0),
        (player_map["Virat Kohli"],     "Test", 113, 193,  8848, 254, 49.15, 55.30, 29, 30,  0,   0.0, 0.00, 0),
        (player_map["Virat Kohli"],     "T20I", 125, 119,  4188, 122, 52.35,138.90, 1,  37,  0,   0.0, 0.00, 0),
        (player_map["Rohit Sharma"],    "ODI",  264, 255, 10709, 264, 48.68, 89.53, 31, 55,  8, 147.0, 5.30, 0),
        (player_map["Rohit Sharma"],    "Test", 67,  115,  4301, 212, 40.57, 58.50, 12, 17,  0,   0.0, 0.00, 0),
        (player_map["Rohit Sharma"],    "T20I", 159, 152,  4231, 118, 32.05,140.89, 5,  32,  0,   0.0, 0.00, 0),
        (player_map["Jasprit Bumrah"],  "ODI",   86,  37,   257,  35, 11.68, 97.35, 0,   0, 149, 24.31, 4.63, 0),
        (player_map["Jasprit Bumrah"],  "Test",  40,  55,   546,  55, 12.50, 68.00, 0,   1, 163, 19.52, 2.72, 6),
        (player_map["Jasprit Bumrah"],  "T20I",  85,  18,   116,  10,  8.29, 95.08, 0,   0,  90, 20.23, 6.23, 0),
        (player_map["Ravindra Jadeja"], "Test",  82, 109,  3163, 175, 38.57, 59.23, 3,  21, 292, 24.37, 2.37,10),
        (player_map["Ravindra Jadeja"], "ODI",  196, 141,  2756, 87,  32.42,  88.7, 0,  14, 220, 36.11, 4.97, 1),
        (player_map["MS Dhoni"],        "ODI",  350, 297, 10773, 183, 50.57, 87.56, 10,  73, 1, 135.0, 4.50, 0),
        (player_map["MS Dhoni"],        "T20I", 98,  85,  1617, 56,  37.60, 126.1, 0,   2,  0,   0.0, 0.00, 0),
        (player_map["Hardik Pandya"],   "ODI",  76,  63,  1727, 92,  33.21,117.90, 0,  12, 77,  36.55, 5.34, 0),
        (player_map["Hardik Pandya"],   "T20I", 94,  73,  1492, 71,  26.64,147.31, 0,  8,  72,  23.22, 8.79, 0),
        (player_map["Steve Smith"],     "Test", 110, 196,  9339, 239, 56.27, 55.10, 32, 38,  7, 172.0, 3.40, 0),
        (player_map["Steve Smith"],     "ODI",  155, 149,  5417, 164, 43.49, 86.95, 12, 30,  9, 135.0, 4.88, 0),
        (player_map["Pat Cummins"],     "Test",  62,  82,   890,  66, 15.86, 82.56, 0,   2, 249, 21.58, 2.75, 8),
        (player_map["Pat Cummins"],     "ODI",   95,  59,   773,  52, 19.83,102.11, 0,   1, 157, 29.44, 5.22, 0),
        (player_map["Joe Root"],        "Test", 145, 260, 12277, 254, 50.52, 55.96, 35, 64,  62, 49.00, 2.82, 0),
        (player_map["Joe Root"],        "ODI",  164, 159,  6207, 133, 46.32, 86.75, 16, 39,  22, 70.00, 4.72, 0),
        (player_map["Ben Stokes"],      "Test",  98, 167,  6124, 258, 37.27, 58.41, 13, 31, 195, 32.67, 2.93, 4),
        (player_map["Babar Azam"],      "ODI",  109, 107,  5007, 158, 57.55, 87.57, 19, 26,  0,   0.0, 0.00, 0),
        (player_map["Babar Azam"],      "Test",  58, 102,  3929, 196, 45.10, 52.29, 9,  22,  0,   0.0, 0.00, 0),
        (player_map["Babar Azam"],      "T20I", 121, 119,  4022, 122, 44.11,130.61, 4,  38,  0,   0.0, 0.00, 0),
        (player_map["Kane Williamson"], "Test",  100, 181, 7953, 251, 54.47, 52.22, 26, 37,  51, 72.00, 3.15, 0),
        (player_map["Kane Williamson"], "ODI",   167, 161, 6554, 148, 47.84, 81.57, 13, 46,  37, 65.00, 4.88, 0),
        (player_map["Kagiso Rabada"],   "Test",   60,  85,   777,  38, 12.61, 64.41, 0,   0, 252, 22.50, 3.23, 9),
        (player_map["Kagiso Rabada"],   "ODI",    78,  37,   370,  36, 13.70, 85.32, 0,   0, 148, 27.22, 5.29, 2),
        (player_map["Shubman Gill"],    "ODI",    58,  57,  2483, 208, 52.82, 99.44, 6,  13,  0,   0.0, 0.00, 0),
        (player_map["Shubman Gill"],    "Test",   29,  53,  1917, 128, 37.58, 57.18, 4,  10,  0,   0.0, 0.00, 0),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO player_career_stats
           (player_id, format, matches_played, innings_batted, total_runs, highest_score,
            batting_average, batting_strike_rate, centuries, half_centuries,
            total_wickets, bowling_average, economy_rate, five_wicket_hauls)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        career_stats
    )

    # ── Batting Stats (match-level) ───────────────────────────────────────
    cur.execute("SELECT match_id FROM matches LIMIT 10")
    match_ids = [r[0] for r in cur.fetchall()]

    batting_rows = []
    import random
    random.seed(42)
    for mid in match_ids:
        for pid in list(player_map.values())[:8]:
            runs   = random.randint(0, 120)
            balls  = max(runs, random.randint(5, 140))
            fours  = random.randint(0, runs // 10)
            sixes  = random.randint(0, runs // 20)
            sr     = round((runs / balls * 100) if balls else 0, 2)
            pos    = random.randint(1, 7)
            batting_rows.append((mid, pid, 1, runs, balls, fours, sixes, sr, "b", pos))

    cur.executemany(
        """INSERT OR IGNORE INTO batting_stats
           (match_id, player_id, innings_number, runs_scored, balls_faced,
            fours, sixes, strike_rate, dismissal_type, batting_position)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        batting_rows
    )

    # ── Bowling Stats (match-level) ───────────────────────────────────────
    bowling_rows = []
    for mid in match_ids:
        bowlers = [player_map[n] for n in
                   ["Jasprit Bumrah","Mohammed Shami","Ravindra Jadeja","Pat Cummins","James Anderson","Kagiso Rabada"] if n in player_map]
        for pid in bowlers:
            overs   = round(random.uniform(2, 10), 1)
            runs_c  = random.randint(15, 70)
            wkts    = random.randint(0, 4)
            eco     = round(runs_c / overs, 2) if overs else 0
            bowling_rows.append((mid, pid, 1, overs, runs_c, wkts, eco, 0))

    cur.executemany(
        """INSERT OR IGNORE INTO bowling_stats
           (match_id, player_id, innings_number, overs_bowled, runs_conceded,
            wickets_taken, economy_rate, maidens)
           VALUES (?,?,?,?,?,?,?,?)""",
        bowling_rows
    )

    conn.commit()
    conn.close()
    print("✅ Sample data seeded successfully!")


# ════════════════════════════════════════════════════════════════════════════
# 4.  QUICK HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════════

def check_db_health() -> dict:
    """Return row counts for each table — useful for a dashboard status widget."""
    tables = ["teams", "venues", "players", "series", "matches",
              "batting_stats", "bowling_stats", "player_career_stats"]
    result = {}
    for t in tables:
        try:
            df = run_query(f"SELECT COUNT(*) AS cnt FROM {t}")
            result[t] = int(df["cnt"].iloc[0]) if not df.empty else 0
        except Exception:
            result[t] = "error"
    return result


# ── Run directly to initialise the database ──────────────────────────────────
if __name__ == "__main__":
    print("Initialising database …")
    create_tables()
    seed_sample_data()
    print("\n📊 Database health check:")
    for table, count in check_db_health().items():
        print(f"   {table:30s}  {count:>5} rows")
