import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import run_query, execute_dml


# =============================================================================
# UTILITY HELPERS
# =============================================================================

def success_msg(msg):  st.success(f"✅  {msg}")
def error_msg(msg):    st.error(f"❌  {msg}")
def info_msg(msg):     st.info(f"ℹ️  {msg}")


def get_teams_map():
    df = run_query("SELECT team_id, team_name FROM teams ORDER BY team_name")
    if df.empty:
        return {}, []
    return dict(zip(df["team_name"], df["team_id"])), list(df["team_name"])


def get_venues_map():
    df = run_query("SELECT venue_id, venue_name FROM venues ORDER BY venue_name")
    if df.empty:
        return {}, []
    return dict(zip(df["venue_name"], df["venue_id"])), list(df["venue_name"])


def get_series_map():
    df = run_query("SELECT series_id, series_name FROM series ORDER BY series_name")
    if df.empty:
        return {}, []
    return dict(zip(df["series_name"], df["series_id"])), list(df["series_name"])


def get_players_map():
    df = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    if df.empty:
        return {}, []
    return dict(zip(df["full_name"], df["player_id"])), list(df["full_name"])


def show_db_summary():
    tables = {
        "👤 Players":       "players",
        "🏏 Matches":       "matches",
        "🧑 Teams":         "teams",
        "🏟️ Venues":       "venues",
        "📋 Series":        "series",
        "📊 Career Stats":  "player_career_stats",
    }
    cols = st.columns(len(tables))
    for col, (label, tbl) in zip(cols, tables.items()):
        df  = run_query(f"SELECT COUNT(*) AS cnt FROM {tbl}")
        cnt = int(df["cnt"].iloc[0]) if not df.empty else 0
        col.metric(label, cnt)


# =============================================================================
# SECTION A — PLAYERS CRUD
# =============================================================================

def players_crud():
    st.subheader("👤 Players Management")
    st.caption("Add, view, update or delete player profiles in the database.")

    op = st.radio(
        "Choose Operation:",
        ["📋 View / Search", "➕ Add New Player", "✏️ Edit Player", "🗑️ Delete Player"],
        horizontal=True, key="player_crud_op",
    )

    # ── READ ──────────────────────────────────────────────────────────────
    if op == "📋 View / Search":
        st.markdown("#### 🔍 Search & Filter Players")

        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Search by Name:", placeholder="e.g. Virat", key="p_search_name")
        with col2:
            country_df   = run_query("SELECT DISTINCT country FROM players ORDER BY country")
            country_list = ["All"] + list(country_df["country"].dropna()) if not country_df.empty else ["All"]
            sel_country  = st.selectbox("Filter by Country:", country_list, key="p_country")
        with col3:
            sel_role = st.selectbox("Filter by Role:", ["All","Batsman","Bowler","All-rounder","WK-Batsman"], key="p_role")

        conditions = []
        if search_name:
            conditions.append(f"p.full_name LIKE '%{search_name}%'")
        if sel_country != "All":
            conditions.append(f"p.country = '{sel_country}'")
        if sel_role != "All":
            conditions.append(f"p.playing_role = '{sel_role}'")
        where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        df = run_query(f"""
            SELECT p.player_id AS "ID", p.full_name AS "Full Name",
                   p.country AS "Country", p.playing_role AS "Role",
                   p.batting_style AS "Batting Style", p.bowling_style AS "Bowling Style",
                   t.team_name AS "Team", p.jersey_number AS "Jersey #",
                   p.date_of_birth AS "DOB"
            FROM players p
            LEFT JOIN teams t ON t.team_id = p.team_id
            {where_sql}
            ORDER BY p.country, p.full_name
        """)

        if df.empty:
            info_msg("No players found matching your filters.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"📊 Showing **{len(df)}** player(s)")
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download as CSV", data=csv,
                               file_name="players.csv", mime="text/csv")

    # ── CREATE ────────────────────────────────────────────────────────────
    elif op == "➕ Add New Player":
        st.markdown("#### ➕ Add a New Player")
        st.markdown("> Fill in all fields and click **Add Player** to save to the database.")

        team_map, team_names = get_teams_map()

        with st.form("form_add_player", clear_on_submit=True):
            st.markdown("**Personal Information**")
            col1, col2 = st.columns(2)
            with col1:
                full_name    = st.text_input("Full Name *", placeholder="e.g. Virat Kohli")
                country      = st.text_input("Country *", placeholder="e.g. India")
                dob          = st.date_input("Date of Birth")
                jersey_no    = st.number_input("Jersey Number", min_value=0, max_value=999, value=0)
            with col2:
                playing_role  = st.selectbox("Playing Role *", ["Batsman","Bowler","All-rounder","WK-Batsman"])
                batting_style = st.selectbox("Batting Style",  ["Right-hand bat","Left-hand bat"])
                bowling_style = st.selectbox("Bowling Style", [
                    "N/A (does not bowl)", "Right-arm fast", "Right-arm fast-medium",
                    "Right-arm medium", "Right-arm off-break", "Right-arm leg-break",
                    "Left-arm fast", "Left-arm fast-medium", "Left-arm medium",
                    "Left-arm orthodox spin", "Left-arm wrist spin",
                ])
                team_name = st.selectbox("Team", team_names if team_names else ["No teams found"])

            st.divider()
            submitted = st.form_submit_button("➕ Add Player to Database", use_container_width=True)

        if submitted:
            if not full_name.strip():
                error_msg("Full Name is required.")
            elif not country.strip():
                error_msg("Country is required.")
            else:
                team_id = team_map.get(team_name)
                ok = execute_dml("""
                    INSERT INTO players
                        (full_name, country, date_of_birth, batting_style,
                         bowling_style, playing_role, team_id, jersey_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (full_name.strip(), country.strip(), str(dob),
                      batting_style, bowling_style, playing_role,
                      team_id, int(jersey_no)))
                if ok:
                    success_msg(f"Player **{full_name}** added successfully!")
                    st.balloons()
                else:
                    error_msg("Failed to add player. Check for duplicate names.")

    # ── UPDATE ────────────────────────────────────────────────────────────
    elif op == "✏️ Edit Player":
        st.markdown("#### ✏️ Edit an Existing Player")
        st.markdown("> Select a player — their data will pre-fill. Edit and save.")

        player_map, player_names = get_players_map()
        team_map, team_names     = get_teams_map()

        if not player_names:
            info_msg("No players in the database yet.")
            return

        selected_name = st.selectbox("Select Player to Edit:", player_names, key="edit_player_select")
        pid = player_map[selected_name]

        current = run_query(f"""
            SELECT p.full_name, p.country, p.date_of_birth, p.batting_style,
                   p.bowling_style, p.playing_role, p.jersey_number, t.team_name
            FROM players p
            LEFT JOIN teams t ON t.team_id = p.team_id
            WHERE p.player_id = {pid}
        """)

        if current.empty:
            error_msg("Could not load player data.")
            return

        row = current.iloc[0]

        with st.expander("📋 Current Data (before edit)", expanded=False):
            st.dataframe(current, use_container_width=True, hide_index=True)

        with st.form("form_edit_player"):
            col1, col2 = st.columns(2)
            with col1:
                new_name    = st.text_input("Full Name",    value=str(row["full_name"]))
                new_country = st.text_input("Country",      value=str(row["country"]))
                new_jersey  = st.number_input("Jersey Number",
                                              value=int(row["jersey_number"] or 0),
                                              min_value=0, max_value=999)
            with col2:
                roles      = ["Batsman","Bowler","All-rounder","WK-Batsman"]
                curr_role  = str(row["playing_role"]) if row["playing_role"] in roles else roles[0]
                new_role   = st.selectbox("Playing Role", roles, index=roles.index(curr_role))

                bat_styles = ["Right-hand bat","Left-hand bat"]
                curr_bat   = str(row["batting_style"]) if row["batting_style"] in bat_styles else bat_styles[0]
                new_bat    = st.selectbox("Batting Style", bat_styles, index=bat_styles.index(curr_bat))

                curr_team  = str(row["team_name"]) if row["team_name"] in team_names else team_names[0] if team_names else ""
                new_team   = st.selectbox("Team", team_names,
                                          index=team_names.index(curr_team) if curr_team in team_names else 0)

            sub = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if sub:
            if not new_name.strip():
                error_msg("Full Name cannot be empty.")
            else:
                new_team_id = team_map.get(new_team)
                ok = execute_dml("""
                    UPDATE players
                    SET full_name=?, country=?, playing_role=?,
                        batting_style=?, jersey_number=?, team_id=?
                    WHERE player_id=?
                """, (new_name.strip(), new_country.strip(), new_role,
                      new_bat, int(new_jersey), new_team_id, pid))
                if ok:
                    success_msg(f"**{new_name}** updated successfully!")
                else:
                    error_msg("Update failed. Please try again.")

    # ── DELETE ────────────────────────────────────────────────────────────
    elif op == "🗑️ Delete Player":
        st.markdown("#### 🗑️ Delete a Player")
        st.warning("""
        ⚠️ Deleting a player also removes ALL their:
        batting stats · bowling stats · fielding stats · career summary stats.
        This **cannot be undone**.
        """)

        player_map, player_names = get_players_map()
        if not player_names:
            info_msg("No players to delete.")
            return

        selected_name = st.selectbox("Select Player to Delete:", player_names, key="del_player_select")
        pid = player_map[selected_name]

        preview = run_query(f"""
            SELECT p.full_name, p.country, p.playing_role, t.team_name AS team
            FROM players p
            LEFT JOIN teams t ON t.team_id = p.team_id
            WHERE p.player_id = {pid}
        """)
        if not preview.empty:
            st.markdown("**Player to be deleted:**")
            st.dataframe(preview, use_container_width=True, hide_index=True)

        confirm    = st.checkbox(f"✅ I confirm I want to permanently delete **{selected_name}**", key="del_confirm")
        delete_btn = st.button("🗑️ DELETE PLAYER", type="primary", use_container_width=True)

        if delete_btn:
            if not confirm:
                error_msg("Please tick the confirmation checkbox first.")
            else:
                execute_dml("DELETE FROM batting_stats       WHERE player_id=?", (pid,))
                execute_dml("DELETE FROM bowling_stats       WHERE player_id=?", (pid,))
                execute_dml("DELETE FROM fielding_stats      WHERE player_id=?", (pid,))
                execute_dml("DELETE FROM player_career_stats WHERE player_id=?", (pid,))
                ok = execute_dml("DELETE FROM players WHERE player_id=?", (pid,))
                if ok:
                    success_msg(f"**{selected_name}** and all related stats deleted.")
                else:
                    error_msg("Deletion failed.")


# =============================================================================
# MAIN PAGE  –  entry point called from app.py
# =============================================================================

def show():
    st.title("🛠️ CRUD Operations")
    st.markdown("""
    This page lets you **Create, Read, Update and Delete** records in the cricket database
    through a form-based interface.
    """)

    st.markdown("#### 📊 Current Database Record Counts")
    show_db_summary()
    st.divider()

    tab_players, = st.tabs([
        "👤 Players"
    ])

    with tab_players:
        players_crud()

