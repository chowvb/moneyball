from bs4 import BeautifulSoup
import requests
import pandas as pd 
import numpy as np

# FBref Euros competition page
euros_url = "https://fbref.com/en/comps/676/European-Championship-Stats"
base_url = "https://fbref.com"

def update_endpoints():
    # Request url from euros_url
    response = requests.get(euros_url)

    # Read requested html page
    soup = BeautifulSoup(response.content, "html.parser")

    # Define a list of the html table id names of each of the group tables.
    table_id = ["results20246761A_overall", "results20246761B_overall", "results20246761C_overall", "results20246761D_overall", "results20246761E_overall", "results20246761F_overall"]


    # If response code is 200 == 
    if response.status_code == 200:
        links = []
        friendly_matches_links = []
        squad_abbr = []
        squad_name = []
        unique_id = []
        mp = []

        for id in table_id:
            table = soup.find("table", id = id)
            teams = table.find_all("a")
            team_links = [l.get("href") for l in teams]

            team_links_filtered = team_links[0::6]
            friendly_links = [item for i, item in enumerate(team_links) if i not in [0,6,12,18]]

            for link in team_links_filtered:
                links.append(link)

                unique_url = link.removeprefix("/en/squads/")
                unique_url = unique_url.replace("/", " ")
                unique_team_code, other = unique_url.split()

                unique_id.append(unique_team_code)

            #for link in friendly_links:
            #    friendly_matches_links.append(link)
            for i in range(0, len(friendly_links), 5):
                friendly_matches_links.append(friendly_links[i:i + 5])



            if table:
                data = [] # Initialise a list to store the table data
                headers = [] # Initialise a list to store the table headers
                
                # Extract header row
                header_row = table.find('thead').find('tr')
                header_columns = header_row.find_all('th')
                headers = [header.get_text(strip=True) for header in header_columns]
                
                # Iterate through rows and extract data and extract the data from the cells
                rows = table.find_all('tr')
                for row in rows:
                    columns = row.find_all(['th', 'td'])
                    row_data = [column.get_text(strip=False) for column in columns]
                    
                    # Skip adding the header row data to the data list
                    if row_data != headers:
                        data.append(row_data)
                
                # Convert data into a DataFrame using pandas
                df = pd.DataFrame(data, columns=headers)
                df.dropna(inplace=True)  # Drop rows with missing values
                df.reset_index(drop=True, inplace=True) # Reset row indicies
                

                # Return the processed DataFrame
            else:
                print("Table not found on the page.")



            for i, name in enumerate(df["Squad"]):
                abbr, name = name.split()
                
                squad_abbr.append(abbr)
                squad_name.append(name)
            
            for i, played in enumerate(df["MP"]):
                mp.append(played)
            



    endpoint_df = pd.DataFrame({
        "Squad" : squad_name,
        "Endpoint_url" : links,
        "unique_id" : unique_id,
        "Last_5_url" : friendly_matches_links,
        "MP" : mp
    })

    endpoint_df.to_json("endpoint.json")

def get_h2h(h2h_teams_list):
    h2h_teams_list = ["England", "Denmark"]
    h2h_teams = h2h_teams_list  
    endpoint_df = pd.read_json("endpoint.json")

    h2h_df = pd.DataFrame()
    for country in h2h_teams:
        team_name = str(country)
        last_5_matches_url = endpoint_df["Last_5_url"].loc[endpoint_df["Squad"] == team_name].tolist()
        last_5_matches_url = last_5_matches_url[0]
        country_unique_id = endpoint_df["unique_id"].loc[endpoint_df["Squad"] == team_name]
        country_html_table_id = "stats_" + country_unique_id + "_summary"
        
        country_df = pd.DataFrame()
        for game in last_5_matches_url:
            print(game)
            response = requests.get(base_url + game)
            soup = BeautifulSoup(response.content, "html.parser")
            if response.status_code == 200:
                table = soup.find("table", {"id": country_html_table_id})

                game_df = pd.read_html(str(table))[0]
                game_df = game_df.droplevel(0, axis = 1)
                game_df = game_df.drop(columns=["#", "Pos", "Age"])
                
                country_df = pd.concat([country_df, game_df])
                country_df = country_df.groupby("Player", as_index=False).sum()[country_df.columns]
                country_df = country_df.iloc[2:]
                country_df["Country"] = country
            else:
                print(response.status_code)
        h2h_df = pd.concat([h2h_df, country_df])
        #return h2h_df


#player_df = get_h2h(["Germany", "Spain"])

#team_df = player_df.drop(columns="Player").groupby("Country", as_index=False).sum()[player_df.columns]