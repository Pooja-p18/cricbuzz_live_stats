import os
import requests
import json
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY",  "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
BASE_URL      = f"https://{RAPIDAPI_HOST}"

HEADERS = {
    "X-RapidAPI-Key":  RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
}


# ════════════════════════════════════════════════════════════════════════════
# LOW-LEVEL REQUEST
# ════════════════════════════════════════════════════════════════════════════

def _get(endpoint: str, params: dict = None) -> dict:
    """Make a GET request to the Cricbuzz API. Returns {} on error."""
    if not RAPIDAPI_KEY:
        return {}          # no key → caller uses mock data
    try:
        url  = f"{BASE_URL}/{endpoint}"
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[API ERROR] {endpoint}: {e}")
        return {}


# ════════════════════════════════════════════════════════════════════════════
# PUBLIC FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def get_live_matches() -> list:
    """
    Fetch currently live / recent matches.
    Returns a list of match dicts (real or mock).
    """
    data = _get("matches/v1/live")
    if data:
        try:
            return data.get("typeMatches", [])
        except Exception:
            pass

    # ── Mock fallback ──────────────────────────────────────────────────────
    return [
        {
            "matchType": "International",
            "seriesMatches": [{
                "seriesAdWrapper": {
                    "seriesName": "India vs Australia Test Series 2025",
                    "matches": [{
                        "matchInfo": {
                            "matchId": 9001,
                            "matchDesc": "1st Test",
                            "matchFormat": "TEST",
                            "startDate": "1714000000000",
                            "status": "India opt to bat",
                            "team1": {"teamName": "India",     "teamSName": "IND"},
                            "team2": {"teamName": "Australia", "teamSName": "AUS"},
                            "venueInfo": {"ground": "Narendra Modi Stadium", "city": "Ahmedabad"},
                        },
                        "matchScore": {
                            "team1Score": {"inngs1": {"runs": 245, "wickets": 6, "overs": 67.3}},
                            "team2Score": {},
                        },
                    }]
                }
            }]
        },
        {
            "matchType": "Domestic",
            "seriesMatches": [{
                "seriesAdWrapper": {
                    "seriesName": "IPL 2025",
                    "matches": [{
                        "matchInfo": {
                            "matchId": 9002,
                            "matchDesc": "Match 12",
                            "matchFormat": "T20",
                            "startDate": "1714050000000",
                            "status": "Mumbai Indians won by 6 wickets",
                            "team1": {"teamName": "Mumbai Indians",  "teamSName": "MI"},
                            "team2": {"teamName": "Chennai Super Kings", "teamSName": "CSK"},
                            "venueInfo": {"ground": "Wankhede Stadium", "city": "Mumbai"},
                        },
                        "matchScore": {
                            "team1Score": {"inngs1": {"runs": 180, "wickets": 5, "overs": 20}},
                            "team2Score": {"inngs1": {"runs": 184, "wickets": 4, "overs": 18.3}},
                        },
                    }]
                }
            }]
        }
    ]


def get_recent_matches() -> list:
    """Fetch recently completed matches."""
    data = _get("matches/v1/recent")
    if data:
        try:
            return data.get("typeMatches", [])
        except Exception:
            pass
    # reuse live mock for demo purposes
    return get_live_matches()


def get_upcoming_matches() -> list:
    """Fetch upcoming scheduled matches."""
    data = _get("matches/v1/upcoming")
    if data:
        try:
            return data.get("typeMatches", [])
        except Exception:
            pass
    return [
        {
            "matchType": "International",
            "seriesMatches": [{
                "seriesAdWrapper": {
                    "seriesName": "ICC Champions Trophy 2025",
                    "matches": [{
                        "matchInfo": {
                            "matchId": 9003,
                            "matchDesc": "Semi Final 1",
                            "matchFormat": "ODI",
                            "startDate": "1716000000000",
                            "status": "Upcoming",
                            "team1": {"teamName": "India",    "teamSName": "IND"},
                            "team2": {"teamName": "Pakistan", "teamSName": "PAK"},
                            "venueInfo": {"ground": "Gaddafi Stadium", "city": "Lahore"},
                        },
                        "matchScore": {},
                    }]
                }
            }]
        }
    ]


def get_match_scorecard(match_id: int) -> dict:
    """Fetch detailed scorecard for a specific match."""
    data = _get(f"mcenter/v1/{match_id}/scard")
    if data:
        return data

    return {
        "matchHeader": {
            "matchId": match_id,
            "status": "India won by 6 wickets",
            "matchDescription": "1st Test",
        },
        "scoreCard": [
            {
                "inningsId": 1,
                "inningsData": {
                    "batTeamDetails": {
                        "batTeamName": "Australia",
                        "batsmenData": {
                            "bat_1": {"batName": "David Warner",  "runs": 45,  "balls": 68,  "fours": 6, "sixes": 0},
                            "bat_2": {"batName": "Steve Smith",   "runs": 121, "balls": 187, "fours": 14,"sixes": 1},
                        }
                    },
                    "bowlTeamDetails": {
                        "bowlTeamName": "India",
                        "bowlersData": {
                            "bowl_1": {"bowlName": "Jasprit Bumrah", "overs": "15.0", "runs": 42, "wickets": 3},
                            "bowl_2": {"bowlName": "Mohammed Shami", "overs": "12.0", "runs": 51, "wickets": 2},
                        }
                    },
                    "scoreDetails": {"runs": 263, "wickets": 10, "overs": 78.3},
                }
            }
        ]
    }


def get_series_list(match_type: str = "international") -> list:
    """Get list of current series. match_type: international | domestic | league"""
    data = _get(f"series/v1/{match_type}")
    if data:
        try:
            return data.get("seriesMapProto", [])
        except Exception:
            pass
    return [
        {"date": "Jun 2025", "series": [
            {"id": 1001, "name": "India tour of England", "startDt": "2025-06-01",
             "endDt": "2025-07-15", "seriesType": "International"},
        ]},
        {"date": "May 2025", "series": [
            {"id": 1002, "name": "ICC World Test Championship Final",
             "startDt": "2025-06-07", "endDt": "2025-06-11", "seriesType": "International"},
        ]},
    ]


def get_player_stats(player_id: int) -> dict:
    """Fetch player profile and career statistics."""
    data = _get(f"stats/v1/player/{player_id}")
    if data:
        return data
    return {
        "id": player_id,
        "name": "Virat Kohli",
        "role": "Batsman",
        "bat_style": "Right-hand bat",
        "bowl_style": "Right-arm medium",
        "team": "India",
        "batting": {
            "Test": {"matches": 113, "runs": 8848, "avg": 49.15, "hs": 254, "100s": 29},
            "ODI":  {"matches": 295, "runs": 13906,"avg": 58.18, "hs": 183, "100s": 50},
            "T20I": {"matches": 125, "runs": 4188, "avg": 52.35, "hs": 122, "100s": 1},
        }
    }


def get_top_batsmen(match_format: str = "ODI") -> dict:
    """Fetch top run-scorers for a given format."""
    fmt_map = {"Test": "test", "ODI": "odi", "T20I": "t20"}
    data = _get(f"stats/v1/ranking/batsmen?formatType={fmt_map.get(match_format,'odi')}")
    if data:
        return data
    # mock top batsmen
    return {
        "rank": [
            {"rank": "1", "name": "Virat Kohli",     "country": "India",     "rating": "880"},
            {"rank": "2", "name": "Babar Azam",       "country": "Pakistan",  "rating": "866"},
            {"rank": "3", "name": "Joe Root",         "country": "England",   "rating": "849"},
            {"rank": "4", "name": "Steve Smith",      "country": "Australia", "rating": "832"},
            {"rank": "5", "name": "Kane Williamson",  "country": "New Zealand","rating":"820"},
            {"rank": "6", "name": "Rohit Sharma",     "country": "India",     "rating": "815"},
            {"rank": "7", "name": "Shubman Gill",     "country": "India",     "rating": "798"},
            {"rank": "8", "name": "Quinton de Kock",  "country": "South Africa","rating":"790"},
            {"rank": "9", "name": "David Warner",     "country": "Australia", "rating": "780"},
            {"rank": "10","name": "Ben Stokes",       "country": "England",   "rating": "772"},
        ]
    }


def get_top_bowlers(match_format: str = "ODI") -> dict:
    """Fetch top wicket-takers for a given format."""
    fmt_map = {"Test": "test", "ODI": "odi", "T20I": "t20"}
    data = _get(f"stats/v1/ranking/bowlers?formatType={fmt_map.get(match_format,'odi')}")
    if data:
        return data
    return {
        "rank": [
            {"rank": "1", "name": "Jasprit Bumrah",  "country": "India",        "rating": "900"},
            {"rank": "2", "name": "Pat Cummins",      "country": "Australia",    "rating": "855"},
            {"rank": "3", "name": "Kagiso Rabada",    "country": "South Africa", "rating": "845"},
            {"rank": "4", "name": "Mitchell Starc",   "country": "Australia",    "rating": "830"},
            {"rank": "5", "name": "Shaheen Afridi",   "country": "Pakistan",     "rating": "818"},
            {"rank": "6", "name": "James Anderson",   "country": "England",      "rating": "802"},
            {"rank": "7", "name": "Mohammed Shami",   "country": "India",        "rating": "795"},
            {"rank": "8", "name": "Trent Boult",      "country": "New Zealand",  "rating": "785"},
            {"rank": "9", "name": "Ravindra Jadeja",  "country": "India",        "rating": "776"},
            {"rank": "10","name": "Shadab Khan",      "country": "Pakistan",     "rating": "768"},
        ]
    }
