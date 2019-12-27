import pandas as pd
import fsds_100719 as fs
import requests
import lxml
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver

url = "https://stats.nba.com/player/1628369/boxscores-traditional/"



# if __name__=='__main__':
#     driver = webdriver.Chrome()


#     driver.get(url)

#     soup = BeautifulSoup(driver.page_source)

#     ## Get all table rows
#     row_tags = soup.find_all('tr')

#     ## Get header/column names
#     head = row_tags[0]
#     column_names = [t.text for t in head.find_all('th')]

#     data = []
#     for row in row_tags[1:]:
#         row_data = [t.text.strip('\n').strip() for t in row.find_all('td')]
#         data.append(row_data)


#     df = pd.DataFrame(data,columns=column_names)

#     float_cols= [col for col in df.columns if '%' in col]
#     obj_cols= ['Match Up','W/L']
#     int_cols = [col for col in df.columns if (col not in float_cols) and (col not in obj_cols)]
#     df.dropna(inplace=True)

#     df[int_cols] = df[int_cols].astype('int')
#     df[float_cols] = df[float_cols].astype('float')


def get_season_df(url,driver=None):
    """
    Loads the provided url. Intended for: stats.nba.com/player/{player_id}}/boxscores-traditional/)
    Helper Function to `get_all_seasons_df`, but can be used alone.
    Args:
        url (str): nba stats plaer boxscore-traditional page. 
        driver (Chrome webdrive), optional): Selenium webdriver object. Created if not provided. Defaults to None.
    
    Returns:
        df (Frame): extracted data table from stats.nba.com
    """
    from selenium import webdriver
    import time
    import pandas as pd
    if driver is None:
        driver = webdriver.Chrome()
        
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source,features='lxml')

    ## Get all table rows
    row_tags = soup.find_all('tr')

    ## Get header/column names
    head = row_tags[0]
    column_names = [t.text for t in head.find_all('th')]

    data = []
    for row in row_tags[1:]:
        row_data = [t.text.strip('\n').strip() for t in row.find_all('td')]
        data.append(row_data)


    df = pd.DataFrame(data,columns=column_names)

    float_cols= [col for col in df.columns if '%' in col]
    obj_cols= ['Match Up','W/L']
    int_cols = [col for col in df.columns if (col not in float_cols) and (col not in obj_cols)]
    df.dropna(inplace=True)

    df[int_cols] = df[int_cols].astype('int')
    df[float_cols] = df[float_cols].astype('float')
    
    df['date'] = df['Match Up'].apply(lambda x: x.split('-')[0])
    df['teams'] = df['Match Up'].apply(lambda x: x.split('-')[1])
    
    df['date']=pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df



def make_season_urls_from_playerid(player_id='1628369',season_years=[2019,2018,2017]):
    """
    Creates the correct urls for each of the season years programmatically.
    base_url = f"https://stats.nba.com/player/{player_id}/boxscores-traditional/"
    season_suffix = f"?Season={start_YR}-{end_yr}&SeasonType=Regular%20Season"

    Args:
        player_id (str, optional): stats.nba.com player id for url. Defaults to '1628369'.
        season_years (list of ints, optional): List of years to extract. Only 3 seasons available. Defaults to [2019,2018,2017].
    
    Returns:
        season_urls (list): List of urls created 
    """
    ## SEPARATING ABOVE INTO F_STRING 
    if isinstance(player_id,int):
        player_id = str(player_id)
        
    base_url = f"https://stats.nba.com/player/{player_id}/boxscores-traditional/"


    season_urls = []

    for year in season_years:
        
        start_YR = str(year)
        end_yr = str(year+1)[-2:]
        
        season_suffix = f"?Season={start_YR}-{end_yr}&SeasonType=Regular%20Season"

        full_url = base_url+season_suffix
        season_urls.append(full_url)

    return season_urls



    
def get_all_seasons_df(season_urls=None,player_id=None,season_years=[2019,2018,2017]):
    """
    Extract data from all season urls provided and concatenate into one dataframe.
    Args:
        season_urls (list of str, optional): List of urls to extract from. If None, generate season_urls from player_id.
        player_id (str or int, optional): stats.nba.com player_id for urls. Defaults to None.
        season_years (list, optional): [description]. Defaults to [2019,2018,2017].
    
    Raises:
        Exception: Must provided EITHER list of season_urls
            or player_id & season_years to generate them with `make_season_urls_from_playerid`
    
    Returns:
        df_combined (Frame): df with all seasons for provided urls/player_id
    """
    import pandas as pd
    import time
    if (season_urls is None):
        if (player_id is None):
            raise Exception("Must provide player_id if not providing season_urls")
        else:
            season_urls = make_season_urls_from_playerid(player_id=player_id,
                                                         season_years=season_years)
                        
    # df = pd.DataFrame()
    df_list = []
    for url in season_urls:
        df_year = get_season_df(url)
        df_list.append(df_year)
        time.sleep(1)
    try:
        df_combined = pd.concat(df_list,axis=0)
        
        if player_id is None:
            player_id = season_urls[0].split('/')[4]
        
        df_combined['player_id']=player_id
        return df_combined
    except:
        print(f'[!] Error during concatenation for player {player_id}. Returning list instead of df...')
        return df_list
    

    
def calc_fantasy_stats(df,pts=None):
    """
    Calculates FantasyPoints from corresponding data columns.
    
    Args:
        df (Frame): df produced by get_all_seasons_df or get_season_df
        
    Returns:
        df_fantasy (Frane): original df + additional fantasy points columns
    """
    
    if pts is None:
        points = pd.read_csv('fantasy_points_conversion.csv',index_col=0)
        pts = dict(zip(points['STAT'],points['PTS']))


    df_fantasy = df.copy()
    
    pts_cols= []
    for k,v in pts.items():
        col_name = k+'_pts'
        df_fantasy[col_name] = df_fantasy[k].apply(lambda x: x*pts[k])
        pts_cols.append(col_name)


    df_fantasy['total_pts'] = df_fantasy.apply(lambda x: x[pts_cols].sum(),axis=1)
    return df_fantasy

    
def save_player_df(df,player_id=None,verbose=True):
    """
    Saves the player df to the data/players/subfolder 
    using the player_id as filename suffix. 
    
    Args:
        df (Frame): player's df to save
        player_id (str, optional): Player_id for filename. Defaults to None, 
            which extracts it from the df..
    """
    if player_id is None:
        player_id=df['player_id'][0]
        
    filename=f"data/players/player_id_{player_id}.csv"
    df.to_csv(filename)
    
    if verbose:
        print(f"[i] df saved as {filename}.")
            