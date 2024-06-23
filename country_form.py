from bs4 import BeautifulSoup
import pandas as pd 
import requests
"""
Takes two countries defined in teams() and returns previous match stats as a head to head dataframe."""

def get_h2h_comparison(team_1, team_2):
    h2h_df = pd.DataFrame()
    teams = [team_1, team_2]
    endpoint_df = pd.read_json("endpoint.json")
    base_url = "https://fbref.com"

    for team in teams:

        country_data = endpoint_df.loc[endpoint_df["Squad"] == team].reset_index(drop=True)
        matches_played = country_data["MP"][0]
        last_5_matches = country_data["Last_5_url"][0]
        last_5_matches.reverse()
        for i, matches in enumerate(range(0, matches_played)):
            url = last_5_matches[i]
            response = requests.get(base_url + url)
            print(response.status_code)
            print(response.reason)
            print(response.headers)

            soup = BeautifulSoup(response.content, "html.parser")

            divs = soup.find("div", {"id" : "team_stats_extra"})

            div_list = [] 

            for div in divs:
                for div2 in div:
                    if div2 == "\n":
                        pass
                    else:
                        div_list.append(div2)
            
            if div_list[0].get_text() == team:
                team_list = div_list[0::3]
                opposition_team = div_list[2].get_text()
            else:
                team_list = div_list[2::3]
                opposition_team = div_list[0].get_text()
            
            df_columns = div_list[1::3]
            

            for i, div in enumerate(team_list):
                strip = div.get_text()
                team_list[i] = strip
            
            for i, stat in enumerate(team_list):
                if stat == team:
                    team_list.remove(team)
            
            for i, column_name in enumerate(df_columns):
                strip = column_name.get_text()
                df_columns[i] = strip
            
            empty_line = "\xa0"
            for i, column_name in enumerate(df_columns):
                if column_name == empty_line:
                    df_columns.remove(empty_line)
            
            team_list = [int(i) for i in team_list]

            team_list.append(opposition_team)
            df_columns.append("Opposition")
            df = pd.DataFrame()
            df[team] = team_list
            df.index = df_columns
            h2h_df = pd.concat([h2h_df, df], axis = 1)
    return h2h_df 

df = get_h2h_comparison("England", "Denmark")