import pandas as pd
import fsds_100719 as fs
import requests
import lxml
from pprint import pprint
from bs4 import BeautifulSoup
url = "https://stats.nba.com/player/1628369/boxscores-traditional/"

# page = requests.get(url,'lxml')

# soup = BeautifulSoup(page.content)
# # pprint(soup.prettify()[:1000])
from selenium import webdriver

if __name__=='__main__':
    driver = webdriver.Chrome()


    driver.get(url)

    soup = BeautifulSoup(driver.page_source)

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


def get_season_df(url,driver=None):
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
    ## SEPARATING ABOVE INTO F_STRING 
    if isinstance(player_id,int):
        player_id = str(player_id)
        
    base_url = f"https://stats.nba.com/player/{player_id}/boxscores-traditional/"


    seasons= {}
    season_urls = []

    for year in season_years:
        
        start_YR = str(year)
        end_yr = str(year+1)[-2:]
        
        # seasons[year] = dict()
        season_suffix = f"?Season={start_YR}-{end_yr}&SeasonType=Regular%20Season"
        full_url = base_url+season_suffix
        season_urls.append(full_url)
    return season_urls



    
def get_all_seasons_df(season_urls=None,player_id=None,season_years=[2019,2018,2017]):
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
    
    
def calc_fantasy_stats(df):
    """
    Calculates FantasyPoints from corresponding data columns.
    
    Args:
        df (Frame): df produced by get_all_seasons_df or get_season_df
        
    Returns:
        df_fantasy (Frane): original df + additional fantasy points columns
    """
    pass