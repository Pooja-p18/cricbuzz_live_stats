# 🏏 Cricbuzz LiveStats — Cricket Analytics Dashboard

A full-stack cricket analytics web application built with
**Python · Streamlit · SQLite · Cricbuzz API (RapidAPI)**.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Features](#-features-by-page)
3. [Tech Stack](#️-tech-stack)
4. [Project Structure](#-project-structure)
5. [Database Schema](#️-database-schema)
6. [Quick Start — Step by Step](#-quick-start--step-by-step)
7. [Getting a Free API Key](#-getting-a-free-cricbuzz-api-key)
8. [SQL Query Guide](#-sql-query-guide-25-queries)
9. [Switching Databases](#-switching-databases)
10. [Troubleshooting](#-troubleshooting)

---

## 📋 Project Overview

Cricbuzz LiveStats is a **5-page interactive dashboard** that combines:
- **Live data** from the Cricbuzz API (real match scores, player rankings)
- **SQL analytics** with 25 practice queries (beginner → advanced)
- **Full CRUD operations** for managing cricket data
- **Interactive charts** using Plotly

> ✅ Works **without an API key** using realistic mock/demo data.
> Add a real key anytime to get live scores.

---

## 📊 Features by Page

### 🏠 Page 1 — Home
- Project overview with database health metrics
- Navigation guide and tech stack display
- Setup instructions and folder structure reference

### 📺 Page 2 — Live Matches
- **Live Now** tab: ongoing match scores with live status
- **Recent** tab: recently completed matches
- **Upcoming** tab: scheduled matches
- **Scorecard** tab: detailed batting & bowling scorecard by match ID

### 📊 Page 3 — Top Player Stats
- ICC batting and bowling rankings by format (Test / ODI / T20I)
- Top-3 player podium with medals
- Career statistics table from database with country/role filters
- **Format comparison radar chart** — see a player's stats across all formats

### 🔍 Page 4 — SQL Analytics
- All **25 SQL queries** from beginner to advanced
- Search/filter queries by keyword or difficulty level
- **Run** button shows results as a table
- **Visualise** button auto-generates a bar chart
- **Custom SQL editor** — write and run your own queries

### 🛠️ Page 5 — CRUD Operations
- **Players** — Add / View / Edit / Delete with full form UI
- **Matches** — Record results, update status, delete records
- **Teams** — Add and edit team details
- **Venues** — Add and edit stadium records
- **Career Stats** — Manually enter/update career numbers per format

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Core language |
| Streamlit | 1.35+ | Web UI framework |
| SQLite | Built-in | Default database |
| Pandas | 2.0+ | Data manipulation & display |
| Plotly | 5.18+ | Interactive charts |
| Requests | 2.31+ | HTTP API calls |
| python-dotenv | 1.0+ | Secure API key loading |

---

## 📁 Project Structure

```
cricbuzz_livestats/
│
├── app.py                    ← Main entry point (run this!)
│                               Handles navigation, CSS theme, DB init
│
├── requirements.txt          ← All Python dependencies + explanations
├── .env.example              ← Template for API key and DB config
├── README.md                 ← This file
│
├── pages/                    ← One file per page of the dashboard
│   ├── __init__.py
│   ├── home.py               ← Page 1: Overview & project info
│   ├── live_matches.py       ← Page 2: Live/Recent/Upcoming + Scorecard
│   ├── top_stats.py          ← Page 3: Rankings & Career Stats
│   ├── sql_queries.py        ← Page 4: 25 SQL queries with execution
│   └── crud_operations.py    ← Page 5: Full CRUD forms for all tables
│
├── utils/                    ← Shared utility modules
│   ├── db_connection.py      ← DB connect, schema create, data seeder,
│   │                           run_query(), execute_dml() helpers
│   └── api_helper.py         ← Cricbuzz API wrapper + mock fallback data
│
└── notebooks/                ← Optional practice notebooks
    └── data_fetching.ipynb   ← Jupyter notebook for API experiments
```

---

## 🗄️ Database Schema

The database has **8 tables** linked by foreign keys:

```
teams ──────────────────────────────┐
  team_id (PK)                       │
  team_name, short_name              │
  country, team_type                 │
                                     │
venues ─────────────────────────────┤
  venue_id (PK)                      │
  venue_name, city                   │
  country, capacity                  │
                                     ▼
players                           matches
  player_id (PK)                    match_id (PK)
  full_name, country                series_id (FK → series)
  batting_style                     team1_id, team2_id (FK → teams)
  bowling_style                     venue_id (FK → venues)
  playing_role                      match_date, match_format
  team_id (FK → teams)              status, toss_winner_id
                                    winning_team_id, victory_margin
        │                                     │
        ▼                                     ▼
player_career_stats            batting_stats + bowling_stats
  (aggregated totals             (per-innings records linked
   per format)                    to match + player)
```

---

## 🚀 Quick Start — Step by Step

### Step 1: Download / Clone the project
```bash
# If using Git:
git clone <your-repo-url>
cd cricbuzz_livestats

# Or simply unzip the downloaded folder and cd into it
```

### Step 2: Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install all dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment file
```bash
# Copy the template
cp .env.example .env

# Open .env in any text editor and add your API key (optional)
# The app works fine without one using demo data
```

### Step 5: Initialize the database
```bash
# This creates all 8 tables AND seeds 24 players, 10 matches, etc.
python utils/db_connection.py
```

You should see:
```
Initialising database …
✅ All tables created successfully.
🌱 Seeding sample data …
✅ Sample data seeded successfully!

📊 Database health check:
   teams                              10 rows
   venues                             15 rows
   players                            24 rows
   ...
```

### Step 6: Launch the dashboard
```bash
streamlit run app.py
```

Then open your browser at: **http://localhost:8501**

---

## 🔑 Getting a Free Cricbuzz API Key

The app works with demo/mock data out of the box.
To get **real live scores**, follow these steps:

1. Go to [https://rapidapi.com](https://rapidapi.com) — create a **free account**
2. Search for **"Cricbuzz Cricket"** in the marketplace
3. Click **Subscribe** on the **Basic (Free)** plan — 500 requests/month
4. Go to the **Endpoints** tab and copy your `X-RapidAPI-Key`
5. Open your `.env` file and set:
   ```
   RAPIDAPI_KEY=paste_your_key_here
   RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com
   ```
6. Restart the Streamlit app — real data will flow automatically

---

## 🧮 SQL Query Guide (25 Queries)

### 🟢 Beginner (Q1–Q8) — Core SQL
| # | Topic | Key SQL Concepts |
|---|-------|-----------------|
| Q1 | India Players | `SELECT`, `WHERE` |
| Q2 | Recent Matches | `JOIN`, `ORDER BY DESC` |
| Q3 | Top ODI Scorers | `ORDER BY`, `LIMIT` |
| Q4 | Large Venues | `WHERE capacity > 25000` |
| Q5 | Team Wins | `GROUP BY`, `COUNT` |
| Q6 | Players by Role | `GROUP BY`, `COUNT` |
| Q7 | Highest Score per Format | `GROUP BY`, `MAX` |
| Q8 | 2024 Series | `WHERE date LIKE '2024%'` |

### 🟡 Intermediate (Q9–Q16) — JOINs & Aggregation
| # | Topic | Key SQL Concepts |
|---|-------|-----------------|
| Q9  | All-rounders | Multiple conditions with `AND` |
| Q10 | Completed Matches | Multi-table `JOIN` |
| Q11 | Multi-format Runs | `CASE WHEN` pivot |
| Q12 | Home vs Away | `CASE WHEN` with JOIN |
| Q13 | Partnerships ≥100 | Self-JOIN on batting_stats |
| Q14 | Bowling at Venues | `HAVING COUNT >= 3` |
| Q15 | Close Match Performers | Filtered `AVG` |
| Q16 | Yearly Trends | `SUBSTR` date grouping |

### 🔴 Advanced (Q17–Q25) — CTEs & Analytics
| # | Topic | Key SQL Concepts |
|---|-------|-----------------|
| Q17 | Toss Advantage | Conditional `COUNT`, win % |
| Q18 | Economical Bowlers | Calculated economy rate |
| Q19 | Consistent Batsmen | Standard deviation in SQL |
| Q20 | Format Match Count | Multi-format `CASE WHEN` |
| Q21 | Performance Ranking | Weighted formula scoring |
| Q22 | Head-to-Head | Self-join on matches |
| Q23 | Player Form Analysis | `WITH` CTE + `CASE` |
| Q24 | Best Partnerships | Complex self-join + `HAVING` |
| Q25 | Career Trajectory | CTE + trend comparison |

---

## 🗄️ Switching Databases

The default is **SQLite** (zero setup). To switch:

### PostgreSQL
```bash
# 1. Install driver
pip install psycopg2-binary

# 2. Create database
createdb cricbuzz_db

# 3. Update .env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cricbuzz_db
DB_USER=postgres
DB_PASSWORD=yourpassword
```

### MySQL
```bash
# 1. Install driver
pip install pymysql

# 2. Create database in MySQL:
# CREATE DATABASE cricbuzz_db;

# 3. Update .env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=cricbuzz_db
DB_USER=root
DB_PASSWORD=yourpassword
```

Then re-run `python utils/db_connection.py` to create tables.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: streamlit` | Run `pip install -r requirements.txt` |
| `No module named 'dotenv'` | Run `pip install python-dotenv` |
| `Database is locked` | Restart the app — SQLite WAL mode handles this |
| API returns empty data | Check your `.env` key; app falls back to mock data |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| Blank page on load | Hard-refresh the browser (Ctrl+Shift+R) |

---

## 📝 Learning Objectives

After completing this project you will understand:
- **API integration** with Python `requests` and authentication headers
- **SQL database design** with normalised tables and foreign keys
- **CRUD operations** with parameterised queries (prevents SQL injection)
- **Streamlit** multi-page app architecture
- **Data visualisation** with Plotly in a web UI
- **Environment variable management** with `.env` and `python-dotenv`
- **Error handling** for API calls and database operations

---

## 📄 License

This project is for educational purposes.
Cricket data provided by Cricbuzz via RapidAPI.
