import requests
import streamlit as st
import pandas as pd
import json
import os

# Function to fetch FPL data based on the team ID
def fetch_fpl_data(team_id):
    url = f"https://fantasy.premierleague.com/api/entry/{team_id}/history/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve data for team ID {team_id}. Status code: {response.status_code}")
        return None

# Function to process and format the data for display
def process_fpl_data(data, team_id):
    if data and 'past' in data:
        seasons = {season['season_name']: {'Total Points': season['total_points'], 'Rank': season['rank']} for season in data['past']}
        return seasons
    return {}

# Function to load team data from a file
def load_team_data(filename="team_data.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return {}

# Function to save team data to a file
def save_team_data(team_data, filename="team_data.json"):
    with open(filename, "w") as file:
        json.dump(team_data, file)

# Main function to run the Streamlit app
def main():
    st.title("Fantasy Premier League Team Tracker")

    # Initialize session state to store multiple teams' data
    if 'teams_data' not in st.session_state:
        st.session_state['teams_data'] = load_team_data()

    # Input for team ID
    team_id_input = st.text_input("Enter FPL Team ID", "")

    if st.button("Add Team ID"):
        if team_id_input:
            data = fetch_fpl_data(team_id_input)
            team_data = process_fpl_data(data, team_id_input)
            if team_data:
                st.session_state['teams_data'][team_id_input] = team_data
                # Save updated team data to file
                save_team_data(st.session_state['teams_data'])
        else:
            st.error("Please enter a valid team ID.")

    # Prepare data for tables
    if st.session_state['teams_data']:
        df_points = pd.DataFrame({team_id: {season: data['Total Points'] for season, data in seasons.items()} 
                                  for team_id, seasons in st.session_state['teams_data'].items()}).T
        df_ranks = pd.DataFrame({team_id: {season: data['Rank'] for season, data in seasons.items()} 
                                 for team_id, seasons in st.session_state['teams_data'].items()}).T

        # Display the tables
        st.write("### Total Points by Season")
        st.dataframe(df_points)

        st.write("### Rank by Season")
        st.dataframe(df_ranks)
    else:
        st.write("No team data available. Please add a team ID.")

if __name__ == "__main__":
    main()
