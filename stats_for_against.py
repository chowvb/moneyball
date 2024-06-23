import requests
from bs4 import BeautifulSoup
import pandas as pd 

standard_stats_url = "https://fbref.com/en/comps/676/stats/European-Championship-Stats"

response = requests.get(url = standard_stats_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id" : "stats_squads_standard_for"})

    if table:
        stats_for_df = pd.read_html(str(table))[0]
        stats_for_df = stats_for_df.drop(columns="Per 90 Minutes")
        stats_for_df = stats_for_df.droplevel(0, axis = 1)
        squad_abbr = []
        squad_name = []
        for i, name in enumerate(stats_for_df["Squad"]):
                abbr, name = name.split()
                
                squad_abbr.append(abbr)
                squad_name.append(name)
        
        stats_for_df["Squad"] = squad_name
    
    table = soup.find("table", {"id" : "stats_squads_standard_against"})

    if table:
        stats_against_df = pd.read_html(str(table))[0]
        stats_against_df = stats_against_df.drop(columns="Per 90 Minutes")
        stats_against_df = stats_against_df.droplevel(0, axis = 1)
        squad_abbr = []
        squad_name = []
        for i, name in enumerate(stats_against_df["Squad"]):
                abbr, vs, name = name.split()
                
                squad_abbr.append(abbr)
                squad_name.append(name)
        
        stats_against_df["Squad"] = squad_name
else:
    print(response.status_code, response.headers)


passing_stats_url = "https://fbref.com/en/comps/676/passing_types/European-Championship-Stats"

response = requests.get(passing_stats_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id" : "stats_squads_passing_types_for"})
    passing_for_df = pd.read_html(str(table))[0]
    corners_for_df = passing_for_df.droplevel(0, axis = 1)
    squad_name = []
    for i, name in enumerate(corners_for_df["Squad"]):
            abbr, name = name.split()
            
            squad_abbr.append(abbr)
            squad_name.append(name)
    
    corners_for_df["Squad"] = squad_name
    team_corners_for_df = corners_for_df[["Squad", "CK"]]

    table = soup.find("table", {"id" : "stats_squads_passing_types_against"})
    passing_against_df = pd.read_html(str(table))[0]
    corners_against_df = passing_against_df.droplevel(0, axis = 1)
    corners_against_df["Squad"] = squad_name
    team_corners_against_df = corners_against_df[["Squad", "CK"]]


miscellaneous_stats_url = "https://fbref.com/en/comps/676/misc/European-Championship-Stats"

response = requests.get(miscellaneous_stats_url)

if response.status_code == 200:
      soup = BeautifulSoup(response.content, "html.parser")
      table = soup.find("table", {"id" : "stats_squads_misc_for"})

      miscellaneous_for_df = pd.read_html(str(table))[0]
      miscellaneous_for_df = miscellaneous_for_df.droplevel(0, axis = 1)
      miscellaneous_for_df["Squad"] = squad_name

      table = soup.find("table", {"id" : "stats_squads_misc_against"})

      miscellaneous_against_df = pd.read_html(str(table))[0]
      miscellaneous_against_df = miscellaneous_against_df.droplevel(0, axis = 1)
      miscellaneous_against_df["Squad"] = squad_name
      
      discipline_for_df = miscellaneous_for_df[["Squad", "CrdY", "Fls", "Fld", "Off"]] 
      discipline_against_df = miscellaneous_against_df[["Squad", "CrdY", "Fls", "Fld", "Off"]]

    

shooting_stats_url = "https://fbref.com/en/comps/676/shooting/European-Championship-Stats"

response = requests.get(shooting_stats_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id" : "stats_squads_shooting_for"})

    shooting_for_df = pd.read_html(str(table))[0]
    shooting_for_df = shooting_for_df.droplevel(0, axis = 1)
    shooting_for_df["Squad"] = squad_name

    table = soup.find("table", {"id" : "stats_squads_shooting_against"})

    shooting_against_df = pd.read_html(str(table))[0]
    shooting_against_df = shooting_against_df.droplevel(0, axis = 1)
    shooting_against_df["Squad"] = squad_name

    shooting_for_df = shooting_for_df[["Squad", "SoT", "SoT/90"]]
    shooting_against_df = shooting_for_df[["Squad", "SoT", "SoT/90"]]


df_against = discipline_against_df.merge(shooting_against_df, left_on= "Squad", right_on= "Squad")
df_against = df_against.merge(team_corners_against_df, left_on="Squad", right_on="Squad")

df_for = discipline_for_df.merge(shooting_for_df, on = "Squad")
df_for = df_for.merge(team_corners_for_df, on = "Squad")


team = "Slovenia"
df_against_filtered = df_against.loc[df_against["Squad"] == team]
df_against_filtered["For/Against"] = "Against"

df_for_filtered = df_for.loc[df_for["Squad"] == team]
df_for_filtered["For/Against"] = "For"

df = pd.concat([df_for_filtered, df_against_filtered])